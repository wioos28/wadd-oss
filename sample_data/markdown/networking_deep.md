# Networking Deep Dive

## 1. OSI Model

| Layer | Name | PDU | Protocols | Devices |
|-------|------|-----|-----------|---------|
| 7 | Application | Data | HTTP, FTP, SMTP, DNS | Gateway |
| 6 | Presentation | Data | SSL/TLS, JPEG, ASCII | - |
| 5 | Session | Data | NetBIOS, RPC | - |
| 4 | Transport | Segment | TCP, UDP | Firewall |
| 3 | Network | Packet | IP, ICMP, ARP | Router |
| 2 | Data Link | Frame | Ethernet, Wi-Fi | Switch |
| 1 | Physical | Bit | USB, Bluetooth | Hub, Repeater |

## 2. TCP Deep Dive

### Three-Way Handshake
```
Client                    Server
  |--- SYN (seq=x) ------->|
  |<-- SYN-ACK (seq=y, ack=x+1) --|
  |--- ACK (ack=y+1) ----->|
  |=== Connection Established ===|
```

### Four-Way Termination
```
Client                    Server
  |--- FIN (seq=u) ------->|
  |<-- ACK (ack=u+1) ------|
  |<-- FIN (seq=w) ---------|
  |--- ACK (ack=w+1) ----->|
  |=== Connection Closed ===|
```

### TCP States
- LISTEN: Server waiting for connections
- SYN_SENT: Client sent SYN
- SYN_RECEIVED: Server received SYN
- ESTABLISHED: Connection active
- FIN_WAIT_1/2: Closing
- TIME_WAIT: Waiting for delayed packets
- CLOSE_WAIT: Server received FIN

### Flow Control
- Sliding window protocol
- Window size negotiation
- Congestion avoidance

### Congestion Control
- Slow Start
- Congestion Avoidance
- Fast Retransmit
- Fast Recovery

## 3. UDP Deep Dive

### Characteristics
- Connectionless
- No guaranteed delivery
- No ordering
- No flow control
- Low overhead

### Use Cases
- DNS queries
- Video streaming
- Online gaming
- VoIP
- DHCP

## 4. HTTP Deep Dive

### Request Methods
| Method | Purpose | Body | Safe | Idempotent |
|--------|---------|------|------|------------|
| GET | Retrieve | No | Yes | Yes |
| POST | Create | Yes | No | No |
| PUT | Replace | Yes | No | Yes |
| PATCH | Partial update | Yes | No | No |
| DELETE | Remove | No | No | Yes |
| HEAD | Headers only | No | Yes | Yes |
| OPTIONS | Allowed methods | No | Yes | Yes |

### Status Codes
| Code | Category | Examples |
|------|----------|----------|
| 1xx | Informational | 100 Continue, 101 Switching Protocols |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301 Moved Permanently, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 404 Not Found |
| 5xx | Server Error | 500 Internal Server Error, 503 Service Unavailable |

### Headers
```
# Request Headers
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html
Authorization: Bearer token
Content-Type: application/json

# Response Headers
Content-Type: text/html
Cache-Control: max-age=3600
Set-Cookie: session=abc123
Location: /new-url
```

## 5. DNS Deep Dive

### Record Types
| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | example.com → 93.184.216.34 |
| AAAA | IPv6 address | example.com → 2606:2800:220:1::248 |
| CNAME | Alias | www.example.com → example.com |
| MX | Mail server | example.com → mail.example.com |
| TXT | Text data | SPF, DKIM records |
| NS | Name server | example.com → ns1.example.com |
| SOA | Zone info | Start of Authority |

### DNS Resolution Process
```
1. Browser cache
2. OS cache
3. Router cache
4. ISP DNS server
5. Root nameserver
6. TLD nameserver (.com)
7. Authoritative nameserver
8. Response cached at each level
```

## 6. SSL/TLS Deep Dive

### Handshake Process
```
Client                              Server
  |--- ClientHello ----------------->|
  |    (supported ciphers, random)    |
  |<-- ServerHello ------------------|
  |    (selected cipher, random)      |
  |<-- Certificate ------------------|
  |<-- ServerKeyExchange ------------|
  |<-- ServerHelloDone --------------|
  |--- ClientKeyExchange ----------->|
  |--- ChangeCipherSpec ------------>|
  |--- Finished -------------------->|
  |<-- ChangeCipherSpec -------------|
  |<-- Finished ---------------------|
  |=== Encrypted Communication ======|
```

### Cipher Suites
- Key Exchange: RSA, ECDHE
- Bulk Encryption: AES, ChaCha20
- MAC: SHA256, SHA384

## 7. WebSocket

### Upgrade Process
```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZQ==
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### Frame Format
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data (continued)                  |
+---------------------------------------------------------------+
```

## 8. Network Security

### Firewall Types
- **Packet Filter**: Layer 3-4
- **Stateful Inspector**: Connection tracking
- **Application Layer**: Layer 7
- **Next-Gen (NGFW)**: Deep packet inspection

### VPN Protocols
- **OpenVPN**: SSL/TLS based
- **WireGuard**: Modern, fast
- **IPSec**: Network layer
- **L2TP**: Layer 2 tunneling
