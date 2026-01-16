# Fraction Estate / Invincible Ocean - User Flow Documentation

> Complete user journey documentation for the RWA (Real World Asset) tokenization platform.

---

## Platform Overview

Fraction Estate operates as a **Web3-enabled real estate tokenization platform** that bridges traditional real estate investment with blockchain technology. The platform enables fractional ownership of high-value properties through tokenization.

### Key Platform Sections

| Section | Status | Description |
|---------|--------|-------------|
| Landing Page | ✅ Live | Marketing homepage with platform overview |
| Global Map | ✅ Live | Interactive 3D world map showing properties |
| Property View | ✅ Live | Detailed 3D visualization of individual properties |
| Admin Dashboard | ✅ Live | Property listing management interface |
| KYC Verification | ✅ Live | Identity verification flow |
| Marketplace | 🚧 Coming Soon | Property trading platform |
| Staking | 🚧 Coming Soon | Token staking functionality |
| My Assets | 🚧 Coming Soon | User portfolio management |

---

## User Personas

### 1. Investor
Real estate investors seeking fractional ownership opportunities with lower entry barriers.

### 2. Property Owner
Real estate owners wanting to tokenize and fractionalize their properties.

### 3. Platform Admin
Administrative users managing listings, approvals, and platform operations.

---

## User Flow Diagrams

### 1. Complete Platform Navigation Flow

```mermaid
flowchart TD
    A[Landing Page] --> B{User Action}
    B -->|Get Started| C[Global Map View]
    B -->|Connect Wallet| D[WalletConnect Modal]
    B -->|List Property| E[Admin Dashboard]
    B -->|Scroll/Explore| F[Homepage Sections]
    
    C --> G[Property Markers]
    G -->|Click Marker| H[3D Property View]
    H -->|Back to Map| C
    
    E --> I{KYC Status}
    I -->|Not Verified| J[KYC Verification Flow]
    I -->|Verified| K[Dashboard Home]
    J -->|Complete KYC| K
    
    K --> L[Manage Listings]
    L -->|Add New| M[Property Submission]
    
    D --> N[Select Wallet Provider]
    N --> O[Wallet Connected]
    O --> C

    style A fill:#1a1a2e,color:#fff
    style C fill:#16213e,color:#fff
    style H fill:#0f3460,color:#fff
    style K fill:#e94560,color:#fff
```

---

### 2. Investor Journey Flow

```mermaid
flowchart TD
    subgraph Discovery["🔍 Discovery Phase"]
        A1[Visit Landing Page] --> A2[Explore Platform Features]
        A2 --> A3[View TVL & Stats]
        A3 --> A4[Read Why Us Section]
    end
    
    subgraph Engagement["💼 Engagement Phase"]
        B1[Click Get Started] --> B2[View Global Map]
        B2 --> B3[Browse Property Markers]
        B3 --> B4[Select Property Location]
        B4 --> B5[View 3D Property Details]
    end
    
    subgraph Connection["🔗 Web3 Connection"]
        C1[Click Connect Wallet] --> C2[WalletConnect Modal]
        C2 --> C3{Select Provider}
        C3 -->|Binance| C4[Binance Wallet]
        C3 -->|Ledger| C5[Ledger Hardware]
        C3 -->|Fireblocks| C6[Fireblocks]
        C3 -->|Other| C7[Additional Wallets]
        C4 & C5 & C6 & C7 --> C8[Wallet Connected]
    end
    
    subgraph Investment["💰 Investment Phase - Coming Soon"]
        D1[Access Marketplace] --> D2[Browse Available Fractions]
        D2 --> D3[Select Investment Amount]
        D3 --> D4[Confirm Transaction]
        D4 --> D5[Receive Property Tokens]
    end
    
    Discovery --> Engagement
    Engagement --> Connection
    Connection --> Investment

    style D1 fill:#666,color:#fff,stroke-dasharray: 5 5
    style D2 fill:#666,color:#fff,stroke-dasharray: 5 5
    style D3 fill:#666,color:#fff,stroke-dasharray: 5 5
    style D4 fill:#666,color:#fff,stroke-dasharray: 5 5
    style D5 fill:#666,color:#fff,stroke-dasharray: 5 5
```

---

### 3. Property Owner Listing Flow

```mermaid
flowchart TD
    subgraph Onboarding["📋 Onboarding"]
        A1[Click List Property] --> A2[KYC Verification Modal]
        A2 --> A3[Enter Personal Info]
        A3 --> A4[Full Name & Email]
        A4 --> A5[Phone & DOB]
        A5 --> A6[Nationality Selection]
        A6 --> A7[Document Verification]
        A7 --> A8[KYC Approved]
    end
    
    subgraph Dashboard["📊 Dashboard Access"]
        B1[Access Admin Dashboard] --> B2[View Stats Overview]
        B2 --> B3[Total Properties]
        B2 --> B4[Approved Listings]
        B2 --> B5[Pending Submissions]
        B2 --> B6[Fractional Status]
    end
    
    subgraph Listing["🏠 Property Listing"]
        C1[Submit New Property] --> C2[Property Details Form]
        C2 --> C3[Location & Images]
        C3 --> C4[Valuation & Price]
        C4 --> C5[Fractionalization Terms]
        C5 --> C6[Submit for Review]
        C6 --> C7[Pending Approval]
        C7 --> C8[Property Approved]
        C8 --> C9[Listed on Global Map]
    end
    
    Onboarding --> Dashboard
    Dashboard --> Listing

    style A1 fill:#e94560,color:#fff
    style B1 fill:#16213e,color:#fff
    style C9 fill:#00d9ff,color:#000
```

---

### 4. KYC Verification Flow (Detailed)

```mermaid
flowchart LR
    subgraph Step1["Step 1: Personal Info"]
        A1[Full Name]
        A2[Email Address]
        A3[Phone Number]
    end
    
    subgraph Step2["Step 2: Identity"]
        B1[Date of Birth]
        B2[Nationality]
        B3[Country of Residence]
    end
    
    subgraph Step3["Step 3: Documents"]
        C1[ID Document Upload]
        C2[Proof of Address]
        C3[Selfie Verification]
    end
    
    subgraph Step4["Step 4: Review"]
        D1[Submit for Review]
        D2[Verification Processing]
        D3[KYC Approved/Rejected]
    end
    
    Step1 --> Step2 --> Step3 --> Step4
```

---

### 5. Platform Admin Flow

```mermaid
flowchart TD
    subgraph AdminAuth["🔐 Admin Authentication"]
        A1[Admin Login] --> A2[Wallet Verification]
        A2 --> A3[Admin Dashboard]
    end
    
    subgraph PropertyMgmt["🏗️ Property Management"]
        B1[View All Submissions] --> B2{Review Property}
        B2 -->|Approve| B3[Mark as Approved]
        B2 -->|Reject| B4[Mark as Rejected]
        B2 -->|Request Info| B5[Request Changes]
        B3 --> B6[Add to Global Map]
    end
    
    subgraph UserMgmt["👥 User Management"]
        C1[View KYC Submissions] --> C2{Verify Identity}
        C2 -->|Valid| C3[Approve KYC]
        C2 -->|Invalid| C4[Reject KYC]
        C3 --> C5[Enable User Features]
    end
    
    subgraph Analytics["📈 Analytics"]
        D1[Platform Statistics]
        D2[TVL Tracking]
        D3[User Metrics]
        D4[Property Performance]
    end
    
    AdminAuth --> PropertyMgmt
    AdminAuth --> UserMgmt
    AdminAuth --> Analytics
```

---

## Interactive Elements & UI Components

### Navigation Structure

```
🏠 Header Navigation
├── Home (Landing Page)
├── Why Us (Features Section)
├── Assets (Property Listings)
├── Blog (Community Updates)
├── List Property → Admin Dashboard / KYC
└── Connect Wallet → WalletConnect Modal

🗺️ App Navigation (dApp Mode)
├── Back to Home
├── Back to Map (from Property View)
├── Marketplace (Coming Soon)
├── Staking (Coming Soon)
└── My Assets (Coming Soon)
```

### Interactive Components

| Component | Location | Function |
|-----------|----------|----------|
| Property Markers | Global Map | Navigate to 3D property view |
| Map Controls | Property View | Zoom, rotate, reset view |
| KYC Modal | Dashboard Entry | Identity verification steps |
| WalletConnect | Header | Multi-wallet connection |
| Coming Soon Modal | Bottom Nav | Placeholder for future features |
| Stats Cards | Homepage & Dashboard | Display TVL, investor count, etc. |

---

## Web3 Integration Points

### Wallet Connection Options
- **WalletConnect** - Primary integration protocol
- **Binance Wallet** - Direct integration
- **Ledger** - Hardware wallet support
- **Fireblocks** - Institutional custody

### Blockchain Features
- Asset tokenization on Ethereum
- ETH-based pricing (e.g., "2.5 ETH")
- Blockchain audit trails for transactions
- Smart contract-based ownership

---

## Future Flow Additions (Coming Soon)

### Marketplace Flow
```mermaid
flowchart LR
    A[Browse Properties] --> B[View Fractions Available]
    B --> C[Select Investment Amount]
    C --> D[Connect Wallet]
    D --> E[Sign Transaction]
    E --> F[Receive Tokens]
    F --> G[Own Property Fraction]
    
    style A fill:#666,stroke-dasharray: 5 5
    style B fill:#666,stroke-dasharray: 5 5
    style C fill:#666,stroke-dasharray: 5 5
    style D fill:#666,stroke-dasharray: 5 5
    style E fill:#666,stroke-dasharray: 5 5
    style F fill:#666,stroke-dasharray: 5 5
    style G fill:#666,stroke-dasharray: 5 5
```

### Staking Flow
```mermaid
flowchart LR
    A[Access Staking] --> B[View Staking Pools]
    B --> C[Select Pool & Amount]
    C --> D[Approve Tokens]
    D --> E[Stake Tokens]
    E --> F[Earn Rewards]
    
    style A fill:#666,stroke-dasharray: 5 5
    style B fill:#666,stroke-dasharray: 5 5
    style C fill:#666,stroke-dasharray: 5 5
    style D fill:#666,stroke-dasharray: 5 5
    style E fill:#666,stroke-dasharray: 5 5
    style F fill:#666,stroke-dasharray: 5 5
```

---

## Site Exploration Recording

The following recording documents the complete exploration of the Fraction Estate website:

![Fraction Estate Website Exploration](C:/Users/LENOVO/.gemini/antigravity/brain/60443387-14ef-48e4-925f-3a9c9f8834d3/fraction_estate_exploration_1766987267305.webp)

---

## Summary

This documentation captures the current state of Fraction Estate's user flows as of December 2024. The platform has a functional:

✅ **Landing Page** with rich marketing content  
✅ **3D Global Map** for property visualization  
✅ **Admin Dashboard** for property management  
✅ **KYC System** for user verification  
✅ **WalletConnect Integration** for Web3 connectivity  

🚧 **Coming Soon**: Marketplace, Staking, and My Assets sections.

---

*Document generated: December 29, 2024*
