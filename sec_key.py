import secrets

# Generate a secure random string
secret_key = secrets.token_hex(32)  # 32 bytes will give you a 64-character hexadecimal string
print(secret_key)
