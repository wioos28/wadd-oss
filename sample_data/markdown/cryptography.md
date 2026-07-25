# Cryptography

## 1. Fundamentals

### Goals of Cryptography
- **Confidentiality**: Only authorized can read
- **Integrity**: Data not modified
- **Authentication**: Verify identity
- **Non-repudiation**: Cannot deny sending

### Kerckhoffs's Principle
A cryptosystem should be secure even if everything about it, except the key, is public knowledge.

## 2. Symmetric Encryption

### Block Ciphers
| Algorithm | Block Size | Key Size | Status |
|-----------|------------|----------|--------|
| DES | 64-bit | 56-bit | Deprecated |
| 3DES | 64-bit | 168-bit | Legacy |
| AES | 128-bit | 128/192/256-bit | Standard |
| Blowfish | 64-bit | 32-448-bit | Legacy |
| ChaCha20 | Stream | 256-bit | Modern |

### AES Modes
| Mode | Description | Parallelizable |
|------|-------------|----------------|
| ECB | Electronic Codebook | Yes |
| CBC | Cipher Block Chaining | Encryption: No, Decryption: Yes |
| CTR | Counter | Yes |
| GCM | Galois/Counter Mode | Yes |
| CFB | Cipher Feedback | No |

### Stream Ciphers
- **RC4**: Deprecated
- **ChaCha20**: Modern, fast
- **Salsa20**: ChaCha20 predecessor

## 3. Asymmetric Encryption

### Key Concepts
- Public key: Encrypt/verify
- Private key: Decrypt/sign
- Key pairs mathematically related

### Algorithms
| Algorithm | Based On | Key Size | Use Case |
|-----------|----------|----------|----------|
| RSA | Integer factorization | 2048-4096 bit | General purpose |
| ECC | Elliptic curve | 256-521 bit | Mobile, IoT |
| Ed25519 | Twisted Edwards | 256 bit | Signatures |
| X25519 | Curve25519 | 256 bit | Key exchange |

### RSA
```python
# Key generation
p, q = generate_primes()
n = p * q
φ(n) = (p-1) * (q-1)
e = 65537  # Public exponent
d = mod_inverse(e, φ(n))  # Private exponent

# Encryption: c = m^e mod n
# Decryption: m = c^d mod n
```

## 4. Hashing

### Properties
- **Deterministic**: Same input → same output
- **Pre-image resistant**: Hard to find input from output
- **Collision resistant**: Hard to find two inputs with same output
- **Avalanche effect**: Small input change → large output change

### Algorithms
| Algorithm | Output Size | Status |
|-----------|-------------|--------|
| MD5 | 128-bit | Broken |
| SHA-1 | 160-bit | Deprecated |
| SHA-256 | 256-bit | Standard |
| SHA-3 | 224/256/384/512-bit | Modern |
| BLAKE2 | Variable | Fast |
| Argon2 | Variable | Password hashing |

### Password Hashing
```python
# Bad: Plain hash
hash = sha256(password)

# Better: With salt
salt = generate_salt()
hash = sha256(salt + password)

# Best: Dedicated password hashing
hash = bcrypt.hashpw(password, bcrypt.gensalt())
hash = argon2.hash(password)
```

## 5. Digital Signatures

### Process
```
Signing:
1. Hash the message
2. Encrypt hash with private key
3. Send message + signature

Verification:
1. Decrypt signature with public key
2. Hash the message
3. Compare hashes
```

### Algorithms
- **RSA-PKCS#1**: Based on RSA
- **ECDSA**: Based on ECC
- **EdDSA (Ed25519)**: Modern, fast
- **DSA**: NIST standard (legacy)

## 6. Key Exchange

### Diffie-Hellman
```
Public: p (prime), g (generator)
Alice: a (private), A = g^a mod p (public)
Bob: b (private), B = g^b mod p (public)

Shared secret: s = B^a mod p = A^b mod p = g^(ab) mod p
```

### ECDH
- Elliptic Curve Diffie-Hellman
- Same concept, elliptic curves
- Smaller key sizes, same security

## 7. TLS/SSL

### TLS 1.3 Handshake
```
Client                              Server
  |--- ClientHello --------------->|
  |    (key shares, ciphers)       |
  |<-- ServerHello ----------------|
  |    (key share, certificate)    |
  |<-- Finished -------------------|
  |--- Finished ------------------>|
  |=== Encrypted Communication ====|
```

### Certificate Chain
```
Root CA
  └── Intermediate CA
        └── Server Certificate
```

## 8. Cryptographic Protocols

### Signal Protocol
- Double Ratchet Algorithm
- X3DH key agreement
- End-to-end encryption

### S/MIME
- Email encryption
- X.509 certificates

### PGP/GPG
- File/email encryption
- Web of Trust model

## 9. Attacks

### Symmetric
- Brute force
- Known plaintext
- Chosen plaintext
- Side-channel attacks

### Asymmetric
- Factoring (RSA)
- Discrete logarithm
- Timing attacks

### Hash
- Collision attacks
- Pre-image attacks
- Rainbow tables

### Protocol
- Man-in-the-middle
- Replay attacks
- Downgrade attacks
