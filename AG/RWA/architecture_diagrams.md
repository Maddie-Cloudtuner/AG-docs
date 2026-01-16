# Technical Architecture - The Visual Guide

Alright, so you want to see how this all fits together technically. Here are the diagrams that show the architecture, workflows, and how money/data flows through the system.

---

## 1. The Full Stack: L0 + L1 Architecture

This shows how our blockchain infrastructure is layered. Think of L0 as the foundation that lets us build specialized chains on top.

```mermaid
graph TB
    subgraph "Layer 0 - The Foundation"
        L0[Invincible Ocean L0]
        L0_Consensus[Consensus Coordination]
        L0_Interop[Cross-Chain Protocol]
        L0_Validator[Validator Network]
        L0_Security[Shared Security Model]
        
        L0 --> L0_Consensus
        L0 --> L0_Interop
        L0 --> L0_Validator
        L0 --> L0_Security
    end
    
    subgraph "Layer 1 - Application Chains"
        L1_RWA[L1 RWA Chain - Real Estate]
        L1_Future[Future L1 Chains - TBD]
        
        L1_RWA_Token[Property Token Module]
        L1_RWA_Compliance[Compliance Module]
        L1_RWA_Smart[Smart Contract Engine]
        L1_RWA_EVM[EVM Compatibility Layer]
        
        L1_RWA --> L1_RWA_Token
        L1_RWA --> L1_RWA_Compliance
        L1_RWA --> L1_RWA_Smart
        L1_RWA --> L1_RWA_EVM
    end
    
    subgraph "External Chains We Bridge To"
        ETH[Ethereum]
        POLY[Polygon]
        SOL[Solana]
    end
    
    L0 -.->|Powers| L1_RWA
    L0 -.->|Can Power| L1_Future
    
    L0_Interop -->|Bridge Protocol| ETH
    L0_Interop -->|Bridge Protocol| POLY
    L0_Interop -->|Bridge Protocol| SOL
    
    style L0 fill:#1a237e,color:#fff
    style L1_RWA fill:#00695c,color:#fff
    style L1_Future fill:#e0e0e0,color:#333
```

**What this means:**  
L0 handles the heavy lifting (security, cross-chain stuff). L1 is where properties get tokenized and traded. Later we can spin up other L1s for different asset types without rebuilding everything.

---

## 2. How Property Tokenization Actually Works

Step by step, from finding a building to investors collecting rent.

```mermaid
flowchart LR
    A[1. Find Property] --> B[2. Legal Setup]
    B --> C[3. Deploy Smart Contracts]
    C --> D[4. Get Compliant]
    D --> E[5. Sell Tokens]
    E --> F[6. Ongoing Operations]
    
    A1[Dubai property<br/>$5M-$50M range] -.-> A
    B1[Create SPV<br/>File VARA license] -.-> B
    C1[Deploy ERC-1155<br/>Upload metadata to IPFS] -.-> C
    D1[Integrate KYC<br/>Link to DLD registry] -.-> D
    E1[Private sale first<br/>Then public] -.-> E
    F1[Monthly rent payout<br/>Secondary trading] -.-> F
    
    subgraph Regulators
        VARA[VARA Oversight]
        DLD[Dubai Land Dept]
    end
    
    B -.-> VARA
    D -.-> VARA
    D -.-> DLD
    F -.-> VARA
    
    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#9C27B0,color:#fff
    style D fill:#FF9800,color:#fff
    style E fill:#F44336,color:#fff
    style F fill:#00BCD4,color:#fff
```

---

## 3. Smart Contract Architecture

These are the main contracts that make everything work. They interact with each other and with external data sources.

```mermaid
graph TD
    subgraph "Property Ownership Contracts"
        PT[PropertyToken.sol<br/>ERC-1155 Standard]
        PM[PropertyMetadata.sol<br/>Links to IPFS docs]
        PO[PropertyOwnership.sol<br/>Tracks who owns what]
    end
    
    subgraph "Compliance & Security"
        CM[ComplianceManager.sol<br/>Main compliance logic]
        KYC[KYCRegistry.sol<br/>Whitelist of verified users]
        WL[Whitelist.sol<br/>Transfer restrictions]
        TM[TransactionMonitor.sol<br/>Flags suspicious activity]
    end
    
    subgraph "Money Flow"
        RD[RentDistributor.sol<br/>Sends rent to holders]
        RC[RentCollector.sol<br/>Receives from property mgr]
        PE[PaymentEscrow.sol<br/>Holds funds safely]
    end
    
    subgraph "Governance"
        GV[Governance.sol<br/>Voting mechanism]
        VM[VotingMechanism.sol<br/>Vote counting logic]
        PR[ProposalRegistry.sol<br/>Tracks all proposals]
    end
    
    subgraph "External Integrations"
        ORACLE[Price Oracle<br/>Chainlink + custom]
        KYC_API[KYC Provider<br/>Onfido/Sumsub]
        DLD_API[DLD Registry<br/>Official property data]
    end
    
    PT --> CM
    PT --> PO
    PT --> PM
    
    CM --> KYC
    CM --> WL
    CM --> TM
    
    RD --> RC
    RD --> PE
    RD --> PT
    
    GV --> VM
    GV --> PR
    GV --> PT
    
    CM --> KYC_API
    RD --> ORACLE
    PM --> DLD_API
    
    style PT fill:#1976D2,color:#fff
    style CM fill:#D32F2F,color:#fff
    style RD fill:#388E3C,color:#fff
    style GV fill:#7B1FA2,color:#fff
```

**Key insight:**  
Every token transfer goes through the ComplianceManager first. Can't transfer to someone who hasn't done KYC. Can't transfer to a sanctioned wallet. This is enforced at the protocol level, not just in the UI.

---

## 4. How Someone Becomes an Investor

The full KYC → token purchase flow.

```mermaid
sequenceDiagram
    participant I as New Investor
    participant P as Our Platform
    participant KYC as KYC Provider
    participant CM as ComplianceManager
    participant PT as PropertyToken
    participant W as Their Wallet
    
    I->>P: Sign up
    P->>KYC: Start verification
    I->>KYC: Upload passport, selfie, etc
    KYC->>KYC: Check identity, liveness
    KYC->>P: Verified ✓ or Rejected ✗
    
    alt If Verified
        P->>CM: Add wallet to whitelist
        CM->>CM: Check AML/sanctions
        CM-->>P: Whitelisted
        P->>I: You're approved, can buy tokens
        
        I->>P: Buy $10K worth
        P->>CM: Can this person buy?
        CM-->>P: Yes, whitelisted
        P->>PT: Mint 10,000 tokens
        PT->>W: Transfer to wallet
        PT-->>I: You now own 10K tokens
    else If Rejected
        KYC-->>P: Verification failed
        P-->>I: Sorry, can't verify you
    end
```

The important part: Once someone's whitelisted, their wallet address is approved. They can trade on DEXs and it'll still work because the smart contract checks the whitelist.

---

## 5. How Rent Gets Distributed

From property manager → token holders, automatically.

```mermaid
graph LR
    A[Property Manager] -->|Sends monthly rent| B[RentCollector Contract]
    B -->|Converts AED to USDC| C[Payment Processing]
    C -->|Deducts fees| D[RentDistributor Contract]
    
    D -->|Platform fee 2%| E[Platform Treasury]
    D -->|Mgmt fee 10%| F[Property Manager Account]
    D -->|Net 88%| G[All Token Holders]
    
    G -->|Based on %| H[Investor 1]
    G -->|Based on %| I[Investor 2]
    G -->|Based on %| J[Investor 3]
    G -->|Based on %| K[Everyone else...]
    
    subgraph "All On-Chain, Automated"
        B
        C
        D
    end
    
    style B fill:#4CAF50,color:#fff
    style D fill:#2196F3,color:#fff
    style G fill:#FF9800,color:#fff
```

**Example:**  
Property generates $50K rent this month. Manager sends it → RentCollector converts to stablecoin → Takes 2% platform fee ($1K), 10% mgmt fee ($5K) → Distributes remaining $44K proportionally to all token holders based on how many tokens they own.

All automatic. Once a month. No manual work.

---

## 6. Cross-Chain Bridge (How We Connect to Ethereum, etc.)

This lets someone take their property token from our chain to Ethereum if they want.

```mermaid
graph TB
    subgraph "Invincible Ocean L0"
        L0_Bridge[Bridge Protocol]
        L0_Validator[Validator Set - Approves transfers]
        L0_Relay[Relay Chain - Routes messages]
    end
    
    subgraph "Invincible Ocean L1"
        L1_Lock[Lock/Unlock Contract]
        L1_Verify[Verification Module]
    end
    
    subgraph "Ethereum Mainnet"
        ETH_Contract[Wrapped Property Token]
        ETH_Bridge[Bridge Contract]
    end
    
    subgraph "Polygon"
        POLY_Contract[Wrapped Property Token]
        POLY_Bridge[Bridge Contract]
    end
    
    User[Token Holder] -->|1. Lock tokens on our chain| L1_Lock
    L1_Lock -->|2. Event emitted| L0_Bridge
    L0_Bridge -->|3. Validators confirm| L0_Validator
    L0_Validator -->|4. Relay to destination| L0_Relay
    L0_Relay -->|5. Message to Ethereum| ETH_Bridge
    ETH_Bridge -->|6. Mint wrapped tokens| ETH_Contract
    ETH_Contract -->|7. Deliver to user| User
    
    style L0_Bridge fill:#1a237e,color:#fff
    style L1_Lock fill:#00695c,color:#fff
    style ETH_Contract fill:#627eea,color:#fff
    style POLY_Contract fill:#8247e5,color:#fff
```

**Why this matters:**  
Someone might want to use their property tokens in Ethereum DeFi. They can bridge over, use them as collateral, then bridge back. The actual property stays where it is, but the token representation moves.

---

## 7. VARA Compliance Framework

What we need to do to stay licensed and legal.

```mermaid
graph TD
    A[Invincible Ocean - ARVA Issuer]
    
    subgraph "Before Getting Licensed"
        B1[Dubai LLC + AED 1.5M capital]
        B2[Comprehensive whitepaper]
        B3[AML/CTF policies written]
        B4[Management team in place]
    end
    
    subgraph "After Getting Licensed"
        C1[Independent audit every 6 months]
        C2[Monthly reports to VARA]
        C3[Client funds in segregated accounts]
        C4[24/7 transaction monitoring]
        C5[Incident reporting within 24hrs]
    end
    
    subgraph "Technical Requirements"
        D1[Verify tokens match assets 1:1]
        D2[Track token circulation real-time]
        D3[Maintain investor whitelist]
        D4[Smart contract audits before deploy]
    end
    
    subgraph "DLD Integration"
        E1[Link blockchain to property registry]
        E2[Issue ownership certificates]
        E3[Notify on every transfer]
    end
    
    A --> B1 & B2 & B3 & B4
    A --> C1 & C2 & C3 & C4 & C5
    A --> D1 & D2 & D3 & D4
    A --> E1 & E2 & E3
    
    VARA[VARA - The Regulator] -.->|Oversees everything| A
    DLD[Dubai Land Department] -.->|Validates property data| E1
    
    style A fill:#D32F2F,color:#fff
    style VARA fill:#1976D2,color:#fff
    style DLD fill:#388E3C,color:#fff
```

---

## 8. Where the Money Goes (Token Distribution & Revenue Split)

**For a $10M Property:**

```mermaid
pie title How Tokens Get Distributed
    "Public Sale - Anyone can buy (50%)" : 5000000
    "Private Sale - Early investors (30%)" : 3000000
    "Seed Round - Strategic partners (10%)" : 1000000
    "Reserve - Liquidity & incentives (10%)" : 1000000
```

**Monthly Rent Distribution:**

```mermaid
pie title Where Rent Money Goes Each Month
    "Token Holders Get This (88%)" : 88
    "Property Management Fee (10%)" : 10
    "Platform Fee to Us (2%)" : 2
```

---

## 9. The 3-Year Build Timeline

What we're building when.

```mermaid
gantt
    title Invincible Ocean Development Roadmap
    dateFormat YYYY-MM
    
    section Year 1 - Foundation
    Build L0/L1 blockchain       :2025-01, 2025-06
    File & get VARA license      :2025-02, 2025-08
    Find and buy first property  :2025-07, 2025-10
    Launch mainnet & token sale  :2025-09, 2025-12
    
    section Year 2 - Growth
    Tokenize 10 properties       :2026-01, 2026-12
    Build cross-chain bridges    :2026-01, 2026-06
    Release developer SDK        :2026-04, 2026-06
    Integrate with DeFi protocols:2026-07, 2026-12
    
    section Year 3 - Scale
    Get to 50 properties         :2027-01, 2027-12
    Expand internationally       :2027-01, 2027-12
    Close institutional partnerships:2027-06, 2027-12
```

---

## 10. Data Architecture - What Lives Where

Not everything goes on the blockchain. Here's what goes where and why.

```mermaid
graph TB
    subgraph "On-Chain - Immutable"
        A1[Who owns which tokens]
        A2[Every transaction ever]
        A3[All compliance records]
        A4[Governance votes]
    end
    
    subgraph "IPFS - Distributed Storage"
        B1[Property photos & videos]
        B2[Legal documents & deeds]
        B3[Valuation reports]
        B4[Contracts & agreements]
    end
    
    subgraph "Traditional Database - Fast queries"
        C1[User profiles & settings]
        C2[KYC documents - encrypted]
        C3[Analytics & metrics]
        C4[Email/notification logs]
    end
    
    subgraph "External APIs - Live data"
        D1[Dubai Land Dept registry]
        D2[Property valuation oracles]
        D3[Currency exchange rates]
        D4[Market data feeds]
    end
    
    SC[Smart Contracts] --> A1 & A2 & A3 & A4
    SC -.->|Store hash only| B1 & B2 & B3 & B4
    Platform[Our Backend] --> C1 & C2 & C3 & C4
    Platform -.->|Query when needed| D1 & D2 & D3 & D4
    
    SC -->|Write| Blockchain[(Blockchain State)]
    B1 -->|Store files| IPFS[(IPFS Network)]
    C1 -->|Store data| DB[(PostgreSQL)]
    
    style SC fill:#9C27B0,color:#fff
    style Blockchain fill:#1976D2,color:#fff
    style IPFS fill:#4CAF50,color:#fff
    style DB fill:#FF9800,color:#fff
```

**Why this split:**  
- Blockchain: Things that need to be immutable and trustless
- IPFS: Large files that need to be distributed
- Database: Things that need to be updated or queried quickly
- APIs: Live data from external sources

---

## Technical Specs Summary

Just the numbers:

**L0 Layer:**
- Target: 1,000+ cross-chain messages/second
- Security: $100M+ staked (eventually)
- Validators: Start with 50, scale to 100+
- Consensus: BFT with 2-second finality

**L1 RWA Chain:**
- Throughput: 5,000-10,000 TPS
- Block time: 2-5 seconds
- Finality: 2-10 seconds (depending on consensus)
- Gas fees: Fixed low ($0.01-0.10 per transaction)
- Node requirements: 500GB-2TB storage

**Smart Contracts:**
- Property tokens: ERC-1155 (multi-token standard)
- Metadata: IPFS links for documents
- Compliance: Custom precompiles built into the chain
- Governance: On-chain voting

**Security:**
- Minimum 2 independent audits (CertiK + OpenZeppelin)
- Bug bounty: $100K+ pool on Immunefi
- Pen testing: Quarterly by external firms
- Monitoring: 24/7 with <1 hour response time

---

**Notes:**  
These diagrams will evolve as we build. The important thing is the architecture is sound - we can adjust implementation details as we go.

If any of this is unclear or you want to dive deeper into a specific component, just ask. This is the foundation we're building on, so it's worth getting it right.
