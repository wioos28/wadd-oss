# Blockchain & Web3

## 1. Blockchain Fundamentals

### What is Blockchain?
- Distributed, immutable ledger
- Blocks linked via cryptographic hashes
- Consensus mechanisms for agreement
- Decentralized, no single point of failure

### Block Structure
```
┌─────────────────────────────────┐
│ Block Header                    │
│  - Previous Block Hash          │
│  - Timestamp                    │
│  - Merkle Root                  │
│  - Nonce                        │
│  - Difficulty Target            │
├─────────────────────────────────┤
│ Block Body                      │
│  - Transaction 1                │
│  - Transaction 2                │
│  - ...                          │
└─────────────────────────────────┘
```

### Merkle Tree
```
        Root Hash
       /         \
    Hash AB      Hash CD
    /    \      /    \
  Hash A  Hash B  Hash C  Hash D
    |      |      |      |
  Tx A   Tx B   Tx C   Tx D
```

## 2. Consensus Mechanisms

### Proof of Work (PoW)
- Miners solve cryptographic puzzles
- First to solve adds block
- Energy intensive
- Used by: Bitcoin (historically), Litecoin

### Proof of Stake (PoS)
- Validators stake tokens
- Selection based on stake
- Energy efficient
- Used by: Ethereum 2.0, Cardano

### Delegated Proof of Stake (DPoS)
- Token holders vote for delegates
- Delegates validate transactions
- Faster than PoS
- Used by: EOS, Tron

### Practical Byzantine Fault Tolerance (PBFT)
- Tolerates f < n/3 faulty nodes
- Fast finality
- Used by: Hyperledger Fabric

### Proof of Authority (PoA)
- Pre-approved validators
- Fast, centralized
- Used by: Private chains

## 3. Smart Contracts

### Solidity (Ethereum)
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData;
    
    event DataChanged(uint256 newValue);
    
    function set(uint256 x) public {
        storedData = x;
        emit DataChanged(x);
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
}
```

### Smart Contract Patterns
- **Access Control**: Ownable, Roles
- **Proxy Pattern**: Upgradeable contracts
- **Factory Pattern**: Create multiple contracts
- **State Machine**: Workflow management

## 4. Ethereum & EVM

### EVM (Ethereum Virtual Machine)
- Turing-complete
- Executes smart contracts
- Gas-based execution fees

### Gas
```
Transaction Cost = Gas Used × Gas Price

Gas Limit: Max gas willing to spend
Gas Price: Price per gas unit (in Gwei)
```

### Tokens
| Standard | Use Case |
|----------|----------|
| ERC-20 | Fungible tokens |
| ERC-721 | Non-fungible tokens (NFTs) |
| ERC-1155 | Multi-token standard |

## 5. DeFi (Decentralized Finance)

### Protocols
- **Uniswap**: Automated Market Maker (AMM)
- **Aave**: Lending/Borrowing
- **MakerDAO**: Stablecoin (DAI)
- **Compound**: Lending protocol
- **Curve**: Stablecoin exchange

### AMM Formula
```
x × y = k (Constant Product Formula)

x: Reserve of Token A
y: Reserve of Token B
k: Constant
```

### Yield Farming
- Provide liquidity to protocols
- Earn rewards (tokens + fees)
- Strategies: Single-sided, LP farming

## 6. NFTs (Non-Fungible Tokens)

### ERC-721
```solidity
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MyNFT is ERC721 {
    uint256 private _tokenIdCounter;
    
    constructor() ERC721("MyNFT", "MNFT") {}
    
    function mint(address to) public returns (uint256) {
        uint256 tokenId = _tokenIdCounter++;
        _safeMint(to, tokenId);
        return tokenId;
    }
}
```

### Metadata
```json
{
    "name": "My NFT",
    "description": "A unique digital asset",
    "image": "ipfs://Qm...",
    "attributes": [
        {"trait_type": "Color", "value": "Blue"},
        {"trait_type": "Rarity", "value": "Rare"}
    ]
}
```

## 7. IPFS & Storage

### IPFS (InterPlanetary File System)
- Content-addressed storage
- Deduplication
- Decentralized

### Filecoin
- Incentivized storage layer
- Storage providers earn tokens
- Proof of Replication/Spacetime

## 8. Wallets & Security

### Key Management
```
Private Key → Public Key → Address

Private Key: 256-bit random number
Public Key: Derived from private key (ECDSA)
Address: Hash of public key
```

### Wallet Types
| Type | Security | Convenience |
|------|----------|-------------|
| Hardware | High | Low |
| Software | Medium | High |
| Paper | High (offline) | Low |

### Security Best Practices
- Never share private keys
- Use hardware wallets for large amounts
- Verify transaction details
- Be aware of phishing

## 9. Layer 2 Solutions

### Rollups
- **Optimistic Rollups**: Fraud proofs
- **ZK-Rollups**: Zero-knowledge proofs

### State Channels
- Off-chain transactions
- On-chain settlement
- Used for: Payments, games

### Sidechains
- Separate chains with bridge
- Different consensus rules
- Used for: Scaling, specific use cases
