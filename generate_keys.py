from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate a private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Export private key
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Export public key
public_key = private_key.public_key()
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Print them in hex
print("Public Key:", public_bytes.hex())
print("Private Key:", private_bytes.hex())
