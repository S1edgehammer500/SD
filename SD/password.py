from passlib.hash import sha256_crypt
print(sha256_crypt.hash(str('England')))