# Import Package
from cryptography.fernet import Fernet

# Generate a Key and Instantiate a Fernet Instance
key = Fernet.generate_key()
f = Fernet(key)
print(key)
# b'tgC9X86oL1NsO8SMG-glC1K227i68yLsYdQNKTEGHmo='

# Define our message
plaintext = b"encryption is very useful"

# Encrypt
ciphertext = f.encrypt(plaintext)
print(ciphertext)
# b'gAAAAABd5GccfPra7_UxGBGszabu6-r8Vkh1g6Aqio3PuhG04SCov3f0NMEpmIP6hFSTkp14UDl20EKPMKiFj-9VtOPCHK6NnTBjgTdRTkwJwdBMiOEa1SM='

# Decrypt
decryptedtext = f.decrypt(ciphertext)
print(decryptedtext)
# b'encryption is very useful'