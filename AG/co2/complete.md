# CloudTuner.ai CT02 Carbon Token: Technical & Functional Specification
## India CCTS Compliance & Regulatory Framework Edition

**Version:** 1.0  
**Date:** November 2025  
**Status:** Final Draft for Regulatory Review  
**Reference:** CCTS-2024-25, Energy Conservation Act 2001 (Amendment 2022)

---

## 1. Carbon Market Context: The Indian Landscape

### 1.1 The Carbon Credit Trading Scheme (CCTS)
The **Carbon Credit Trading Scheme (CCTS)**, notified by the Central Government under the **Energy Conservation Act, 2001 (amended 2022)**, establishes the framework for the Indian Carbon Market (ICM). Unlike the earlier Perform, Achieve and Trade (PAT) scheme which traded Energy Saving Certificates (ESCert), CCTS trades **Carbon Credit Certificates (CCCs)**, where **1 CCC = 1 tonne of CO2 equivalent (tCO2e)**.

The scheme operates on a **"Cap-and-Trade" (or Baseline-and-Credit)** model with intensity-based targets:
*   **Obligated Entities:** Initially covers 9 energy-intensive sectors (Iron & Steel, Cement, Fertilizer, Chlor-Alkali, Aluminum, Petrochemicals, Thermal Power, etc.).
*   **Compliance Mechanism:** Entities are assigned specific GHG emission intensity targets (tCO2e/unit of production).
    *   **Over-achievement:** Entities beating their target earn CCCs.
    *   **Under-achievement:** Entities missing their target must purchase CCCs to comply.
*   **Banking:** Surplus CCCs can be banked for future compliance cycles, subject to vintage limits set by the Bureau of Energy Efficiency (BEE).

### 1.2 Regulatory Authority Matrix
The governance structure is strictly defined to ensure integrity and prevent fraud:

| Authority | Role & Responsibility |
|-----------|-----------------------|
| **Ministry of Power (MoP)** | **Apex Policy Maker.** Notifies the scheme, sets overall targets, and governs the CCTS rules. |
| **Bureau of Energy Efficiency (BEE)** | **Administrator.** Responsible for: <br>1. Developing GHG monitoring methodologies (MRV).<br>2. Accrediting Carbon Verification Agencies (ACVs).<br>3. Issuing Carbon Credit Certificates (CCCs).<br>4. Managing the ICM Registry. |
| **Central Electricity Regulatory Commission (CERC)** | **Trading Regulator.** Regulates the trading of CCCs on Power Exchanges (IEX, PXIL, HPX). Ensures fair pricing and market integrity. |
| **Grid Controller of India Ltd (Grid-India)** | **Registry Manager.** Maintains the secure database of all CCC issuances, transfers, and retirements. |
| **SEBI** | **Commodity Derivatives Regulator.** Regulates carbon credits when traded as derivatives (futures/options) on commodity exchanges, ensuring alignment with financial market norms. |

---

## 2. Regulatory Compliance & Tokenization Logic

### 2.1 Alignment with CCTS & MRV Protocols
CloudTuner.ai’s **CT02 token** is designed not as a speculative crypto-asset, but as a **digital twin** of the regulatory Carbon Credit Certificate (CCC) or a high-integrity Voluntary Carbon Credit (VCC) compliant with the **Draft Green Credit Programme (GCP)** rules.

#### Monitoring, Reporting, and Verification (MRV)
To mint a CT02 token, CloudTuner enforces a rigorous MRV cycle compliant with **BEE’s "Common Modalities and Procedures for MRV"**:

1.  **Monitoring (Automated via CloudTuner Agent):**
    *   **Scope:** Scope 2 (Indirect emissions from purchased electricity for cloud compute).
    *   **Methodology:** Real-time ingestion of cloud usage logs (AWS Cost & Usage Reports, Azure Exports).
    *   **Calculation:** `Activity Data (kWh) × Grid Emission Factor (tCO2e/kWh)`.
    *   *Compliance Check:* Uses the latest **Central Electricity Authority (CEA)** CO2 baseline database for Indian grid emission factors (e.g., 0.71 tCO2/MWh for 2024-25).

2.  **Reporting (Immutable Ledger):**
    *   Raw usage data is hashed and anchored to the CloudTuner blockchain.
    *   Generates a **"Carbon Ledger Report"** formatted for submission to the **ICM Registry**.

3.  **Verification (Accredited CVA Integration):**
    *   Before minting, data is exposed to **Accredited Carbon Verification Agencies (ACVs)** via API.
    *   ACVs validate the baseline and reduction claims against the specific sector targets.
    *   *Only verified reductions trigger the smart contract to mint CT02.*

### 2.2 Legal Logic: Creation, Banking, and Export
*   **Credit Creation:** CT02 tokens are minted strictly 1:1 against verified tCO2e reductions.
    *   *Rule:* No algorithmic minting without underlying physical reduction evidence.
*   **Banking:** The smart contract enforces **validity periods**. If CCTS rules state CCCs are valid for 3 years, the CT02 token metadata includes an `expiry_date`. Unused tokens beyond this date are automatically burned or marked "expired" to prevent zombie credits.
*   **Export Restrictions (Article 6 Compliance):**
    *   Per **MoP’s August 2023 notification**, carbon credits generated in India cannot be sold internationally until India’s own **Nationally Determined Contributions (NDC)** targets are met.
    *   **Smart Contract Guardrail:** The `transfer()` function checks the destination wallet. If the destination is flagged as "Non-Domestic" (e.g., an international exchange wallet), the transfer is **blocked** unless a specific "Letter of Authorization" (LoA) token from the National Designated Authority (NDA) is attached.

---

## 3. Technical Design & Token Lifecycle

### 3.1 GHG Data Calculation to Token Minting
The foundation of the CT02 token is the **CloudTuner Emissions Engine**.

**Step 1: Data Ingestion (The Oracle)**
*   **Source:** Cloud Provider APIs (AWS CloudWatch, Azure Monitor).
*   **Granularity:** Instance-level (e.g., `i-0123456789abcdef0`).
*   **Frequency:** Hourly batch processing.

**Step 2: The Calculation Engine (BEE Compliant)**
```python
def calculate_emissions(usage_kwh, region):
    # Fetch official CEA Grid Emission Factor for the region
    emission_factor = get_cea_factor(region, year=2025) 
    
    # Calculate Gross Emissions
    gross_emissions = usage_kwh * emission_factor
    
    # Apply Renewable Energy Certificates (RECs) if retired
    net_emissions = gross_emissions - retired_recs
    
    return net_emissions
```

**Step 3: The Minting Contract**
*   **Trigger:** Verification Signal from ACV.
*   **Action:** Mint `n` CT02 tokens to User Wallet.
*   **Metadata:**
    *   `vintage`: Year of generation (e.g., 2025).
    *   `project_id`: CloudTuner_India_001.
    *   `verification_hash`: Link to the ACV's signed report.
    *   `serial_number`: Matches the ICM Registry serial number.

### 3.2 Lifecycle Flows & Registry Interaction
*(Referencing `ct02_lifecycle_flow.png`)*

1.  **Generation:** Cloud usage -> Emission Calculation -> Verification -> **Mint CT02**.
2.  **Registration:** CloudTuner API pushes minting data to **Grid-India (ICM Registry)** to obtain unique serial numbers.
3.  **Trading:**
    *   **Compliance Market:** User transfers CT02 to "Exchange Escrow". CloudTuner retires CT02 on-chain and transfers equivalent CCCs on the Power Exchange (IEX/PXIL).
    *   **Voluntary Market:** Peer-to-peer trading of CT02 within the CloudTuner ecosystem for supply chain decarbonization (Scope 3).
4.  **Retirement (Offset):**
    *   User calls `burn()` function.
    *   Smart contract destroys CT02.
    *   CloudTuner API notifies ICM Registry to mark CCCs as "Retired".
    *   **Certificate:** User receives a "Sustainability Certificate" compliant with **SEBI BRSR** reporting formats.

---

## 4. Tokenomics & Governance

### 4.1 Rate-Based Pricing & Compliance Cycles
*   **Pricing Mechanism:** Unlike volatile crypto-tokens, CT02 pricing in the compliance market is influenced by the **Floor and Ceiling prices** set by CERC.
    *   *Floor Price:* Minimum price to ensure project viability.
    *   *Ceiling Price:* Maximum price to protect industries from excessive costs.
*   **Tokenomics Model:**
    *   **Supply:** Elastic. Increases only with verified reductions (Hard Cap = Total Verified Reductions).
    *   **Demand:** Driven by Obligated Entities needing to meet March 31st compliance deadlines.

### 4.2 Anti-Fraud & Audit Mechanisms
*   **Double Counting Prevention:**
    *   The **"Corresponding Adjustment"** flag in the smart contract ensures that if a credit is sold internationally (with LoA), it is deducted from India's national registry.
    *   Token metadata includes the specific **Registry Serial Number**. A global oracle checks if this serial number is active in any other registry (Verra, Gold Standard).
*   **Penalty Mechanism:**
    *   If a user mints tokens based on false data (detected post-audit), the **"Clawback"** function is triggered.
    *   The user's staked CT02 tokens are slashed.
    *   Per **Energy Conservation Act**, non-compliance attracts a penalty of up to **₹10 Lakhs** plus the market value of missing credits.

---

## 5. Business & Policy Alignment

### 5.1 Serving the Market
*   **Compliance Market:** CloudTuner acts as an aggregator for smaller tech entities (Data Centers, IT Parks) to pool reductions and trade on Power Exchanges.
*   **Voluntary Market:** Enables corporates to offset "unavoidable" digital emissions.
*   **ESG & BRSR:** Provides listed companies with immutable proof of "Scope 2" reductions, directly feedable into SEBI's BRSR Core reporting format.
*   **CBAM Readiness:** For Indian exporters (Steel, Aluminum) using cloud-heavy design/logistics, CT02 provides verifiable carbon data to reduce **Carbon Border Adjustment Mechanism (CBAM)** taxes in the EU.

### 5.2 Integration & Sandbox
*   **Regulatory Sandbox:** CloudTuner will apply for the **CERC Regulatory Sandbox** to pilot "Tokenized Carbon Credits" as a more efficient, transparent layer on top of the legacy registry system.
*   **Policy Updates:** The system is built with modular "Rule Engines" to adapt to annual updates in CCTS targets or new sector inclusions (e.g., adding the IT sector to the obligated list).

---

## Appendix: Regulatory References & Action Points

### A.1 Key Regulations & Methodologies
1.  **Carbon Credit Trading Scheme (CCTS), 2023 & 2024 Amendments:** [Ministry of Power Gazette Notification](https://powermin.gov.in)
2.  **Energy Conservation (Amendment) Act, 2022:** Legal basis for carbon markets in India.
3.  **BEE MRV Guidelines:** "Detailed Procedure for Compliance Mechanism under CCTS".
4.  **SEBI Master Circular on ESG Rating Providers (ERPs):** Guidelines for assurance and verification.
5.  **Green Credit Programme (GCP) Rules, 2023:** MoEFCC notification for voluntary environmental actions.

### A.2 Business & Developer Action Points
*   **For Developers:**
    *   Implement **OAuth** with the ICM Registry (when API is available).
    *   Build **"Shadow Accounting"** features to track "Banked" vs "Free" credits.
    *   Ensure smart contracts support **"Pause"** functionality (required by regulators for emergency halts).
*   **For Audit Readiness:**
    *   Maintain 5-year data retention of all raw cloud logs (AWS/Azure).
    *   Pre-register CloudTuner as a "Designated Consumer" aggregator with BEE.
    *   Conduct quarterly internal audits using the **ISO 14064** standard (Greenhouse Gases).

---
*This document serves as the master technical blueprint for the CT02 token, ensuring full compliance with the evolving Indian Carbon Market regulations.*
