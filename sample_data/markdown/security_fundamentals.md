# Security Fundamentals

## 1. CIA Triad
| Principle | Mô tả | Ví dụ |
|-----------|-------|-------|
| **Confidentiality** | Chỉ authorized users mới access được | Encryption, Access Control |
| **Integrity** | Dữ liệu không bị thay đổi unauthorized | Checksums, Digital Signatures |
| **Availability** | Hệ thống luôn accessible | Redundancy, DDoS protection |

## 2. Authentication vs Authorization

### Authentication (Xác thực)
"你是谁?" - Xác nhận danh tính
- **Something you know**: Password, PIN
- **Something you have**: Token, Smart card
- **Something you are**: Biometrics (fingerprint, face)

### Authorization (Phân quyền)
"你能做什么?" - Quyết định quyền hạn
- **RBAC**: Role-Based Access Control
- **ABAC**: Attribute-Based Access Control
- **ACL**: Access Control Lists

## 3. Common Vulnerabilities (OWASP Top 10)

### 1. Injection
```python
# BAD
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# GOOD
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```

### 2. Broken Authentication
- Weak passwords
- Session fixation
- Credential stuffing

### 3. Sensitive Data Exposure
- Unencrypted data in transit/at rest
- Hardcoded secrets
- Logging sensitive data

### 4. XML External Entities (XXE)
- Malicious XML parsing
- Read internal files
- Server-side request forgery

### 5. Broken Access Control
- IDOR (Insecure Direct Object References)
- Privilege escalation
- CORS misconfiguration

### 6. Security Misconfiguration
- Default credentials
- Unnecessary features enabled
- Missing security headers

### 7. Cross-Site Scripting (XSS)
```javascript
// Reflected XSS
url: ?q=<script>alert('XSS')</script>

// Stored XSS
// Malicious script stored in database

// DOM-based XSS
document.getElementById("output").innerHTML = location.hash
```

### 8. Insecure Deserialization
- Remote code execution
- Object injection
- Tampered serialized objects

### 9. Using Components with Known Vulnerabilities
- Outdated libraries
- Known CVEs
- Unnecessary dependencies

### 10. Insufficient Logging & Monitoring
- No audit trails
- Delayed detection
- Inadequate incident response

## 4. Cryptography

### Symmetric Encryption
Same key cho encrypt và decrypt
- **AES**: Advanced Encryption Standard (128, 192, 256-bit)
- **DES/3DES**: Deprecated
- **ChaCha20**: Modern alternative

### Asymmetric Encryption
Public key encrypt, private key decrypt
- **RSA**: Widely used
- **ECC**: Elliptic Curve Cryptography
- **Ed25519**: Modern, fast

### Hashing
One-way transformation
- **SHA-256**: Secure, used in blockchain
- **bcrypt**: Password hashing
- **Argon2**: Modern password hashing

### Digital Signatures
- Verify authenticity
- Ensure non-repudiation
- Components: Hash + Asymmetric encryption

## 5. Web Security

### HTTPS/TLS
```
Client                          Server
  |--- ClientHello ------------->|
  |<-- ServerHello --------------|
  |<-- Certificate --------------|
  |<-- ServerKeyExchange --------|
  |--- ClientKeyExchange ------->|
  |--- ChangeCipherSpec -------->|
  |<-- ChangeCipherSpec ---------|
  |--- Finished ---------------->|
  |<-- Finished -----------------|
  |=== Encrypted Data ===========|
```

### Security Headers
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000
X-XSS-Protection: 1; mode=block
```

### CORS (Cross-Origin Resource Sharing)
```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Content-Type
```

## 6. API Security

### Authentication Methods
- **API Keys**: Simple, but less secure
- **OAuth 2.0**: Industry standard
  - Authorization Code Flow
  - Client Credentials Flow
  - PKCE (Proof Key for Code Exchange)
- **JWT**: JSON Web Tokens
  - Header.Payload.Signature
  - Stateless, scalable

### Rate Limiting
- Token Bucket
- Sliding Window
- Fixed Window

### Input Validation
- Whitelist validation
- Type checking
- Length limits
- Regular expressions

## 7. DevSecOps

### Security in CI/CD
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- SCA (Software Composition Analysis)
- Container scanning

### Infrastructure Security
- Network segmentation
- Least privilege principle
- Regular patching
- Security monitoring

## 8. Incident Response

### Phases
1. **Preparation**: Plans, tools, training
2. **Detection & Analysis**: Identify incidents
3. **Containment**: Limit damage
4. **Eradication**: Remove threat
5. **Recovery**: Restore systems
6. **Post-Incident**: Lessons learned
