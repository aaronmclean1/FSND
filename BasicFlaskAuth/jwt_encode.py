# EXAMPLE 1

# Import Python Package
from jose import jwt

import base64

# Init our Data
payload = {'park':'madison square'}
algo = 'HS256' #HMAC-SHA 256
secret = 'learning'

# Encode a JWT
encoded_jwt = jwt.encode(payload, secret, algorithm=algo)
print(encoded_jwt)

# Decode a JWT
decoded_jwt = jwt.decode(encoded_jwt, secret)
print(decoded_jwt)

# Decode with Simple Base64 Encoding
decoded_base64 = base64.b64decode(str(encoded_jwt).split(".")[1]+"==")
print(decoded_base64)