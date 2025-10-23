from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, constr
import requests
import os
import json
import sqlite3
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Settings ---
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "f2d2bc9d7addb7162b99e7c22c90679a")
DB_PATH = "weather.db"

# --- FastAPI App ---
app = FastAPI()


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html
@app.get("/")
def read_index():
    return FileResponse(os.path.join("static", "index.html"))


# Route for manifest.json
@app.get("/manifest.json")
def manifest():
    return FileResponse(os.path.join("static", "manifest.json"))

# Route for service-worker.js
@app.get("/service-worker.js")
def service_worker():
    return FileResponse(os.path.join("static", "service-worker.js"), media_type="application/javascript")

# ---------- CORS (allow your frontend to talk to backend) ----------
origins = [
    "http://localhost:5500",        # Local testing frontend 
    "http://127.0.0.1:5500",       # frontend locally
    "https://weapp2.onrender.com"  # your deployed frontend-render
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    last_login = Column(DateTime)

Base.metadata.create_all(bind=engine)

# --- Auth Utilities ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)

def get_user(db, username: str):
    logger.info(f"Searching user: {username}")
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        logger.warning("User not found")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning("Incorrect password")
        return None
    logger.info(f"User authenticated: {username}")
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Token created for: {data.get('sub')}")
    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise credentials_exception
    user = get_user(db, username)
    if not user:
        raise credentials_exception
    return user

# --- Schemas ---
class RegisterUser(BaseModel):
    username: constr(strip_whitespace=True, min_length=4, max_length=50)
    password: constr(min_length=6, max_length=100)

class ForgotPasswordRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)
    new_password: constr(min_length=6, max_length=100)

# --- Initial Demo User ---
def create_demo_user():
    db = SessionLocal()
    username = "user@example.com"
    password = "password123"
    if not get_user(db, username):
        hashed_password = pwd_context.hash(password[:72])  # bcrypt limit
        db.add(User(username=username, hashed_password=hashed_password))
        db.commit()
        logger.info("Demo user created")
    db.close()

if os.getenv("CREATE_DEMO_USER", "1") == "1":
    create_demo_user()

# --- Routes ---
@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(user.password[:72])  # bcrypt limit
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {user.username}")
    return {"message": "User registered successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    user.last_login = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in: {user.username} at {user.last_login}")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "last_login": str(user.last_login)}

@app.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = pwd_context.hash(req.new_password[:72]) # bcrypt limit
    db.commit()
    logger.info(f"Password reset for user: {req.username}")
    return {"message": "Password reset successful"}

@app.get("/weather")
def get_weather(city: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None,
                db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    logger.info(f"User {user.username} requested weather for {city or lat or lon}")
    if city:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    elif lat is not None and lon is not None:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    else:
        city = "Nairobi"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    res = requests.get(url)
    data = res.json()

    if data.get("cod") != 200:
        logger.error(f"Weather API error: {data}")
        raise HTTPException(status_code=404, detail=data.get("message", "City not found"))

    city_name = city.capitalize() if city else "Nairobi"
    new_search = SearchHistory(city=city_name)
    db.add(new_search)
    db.commit()

    return {
        "city": city_name,
        "temperature": f"{data.get('main', {}).get('temp', 'N/A')} °C",
        "condition": data.get("weather")[0].get("description", "N/A").capitalize(),
        "wind": f"{data.get('wind', {}).get('speed', 'N/A')} m/s",
        "humidity": f"{data.get('main', {}).get('humidity', 'N/A')}%",
        "saved_id": new_search.id,
        "time": datetime.now().strftime("%H:%M:%S"),
"date": datetime.now().strftime("%Y-%m-%d")
    }
#--- Forecast Route ---
@app.get("/forecast")
def get_forecast(city: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logger.info(f"User {user.username} requested forecast for {city}")

    if not city:
        raise HTTPException(status_code=400, detail="City parameter is required")

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        logger.error(f"Forecast API error: {res.text}")
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()

    forecast = []
    for i in range(0, len(data.get("list", [])), 8):  # every 8 items = roughly 24h
        item = data["list"][i]
        forecast.append({
            "date": item["dt_txt"].split(" ")[0],
            "temperature": f"{item['main']['temp']} °C",
            "condition": item["weather"][0]["description"].capitalize(),
            "wind": f"{item['wind']['speed']} m/s",
            "humidity": f"{item['main']['humidity']}%"
        })

    logger.info(f"Forecast for {city} returned successfully")
    return {
        "city": data.get("city", {}).get("name", city),
        "forecast": forecast
    }
#---geolocation Route ---
@app.get("/weather-by-coords")
async def weather_by_coords(lat: float, lon: float, current_user: dict = Depends(get_current_user)):
    # Use your weather API to get weather data by coordinates
    # Example:
    weather_data = get_weather_from_api_by_coords(lat, lon)
    return weather_data
def get_weather_from_api_by_coords(lat: float, lon: float):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url)
    data = res.json()
    if data.get("cod") != 200:
        logger.error(f"Weather API error: {data}")
        raise HTTPException(status_code=404, detail=data.get("message", "Location not found"))
    return {
        "city": data.get("name", "Unknown"),
        "temperature": f"{data.get('main', {}).get('temp', 'N/A')} °C",
        "condition": data.get("weather")[0].get("description", "N/A").capitalize(),
        "wind": f"{data.get('wind', {}).get('speed', 'N/A')} m/s",
        "humidity": f"{data.get('main', {}).get('humidity', 'N/A')}%",
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d")
        
            
    }
# --- Run app on Render ---
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Starting Uvicorn server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

# --- Subscribe Route ---
@app.post("/subscribe")
async def subscribe(request: Request):
    try:
        subscription = await request.json()
        endpoint = subscription.get("endpoint")
        keys = json.dumps(subscription.get("keys"))
        if not endpoint or not keys:
            raise HTTPException(status_code=400, detail="Missing subscription endpoint or keys")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY, endpoint TEXT, keys TEXT)")
        cursor.execute("INSERT INTO subscriptions (endpoint, keys) VALUES (?, ?)", (endpoint, keys))
        conn.commit()
        conn.close()

        logger.info("New subscription saved")
        return JSONResponse({"message": "Subscription saved successfully"}, status_code=201)
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)
