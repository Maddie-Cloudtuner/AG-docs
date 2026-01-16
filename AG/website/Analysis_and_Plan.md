# CloudTuner Website Modernization Plan

## 1. Legacy Site Analysis

### Sources Analyzed
*   **Main Site (`cloudtuner.ai`)**: Corporate landing page. Focus on "Cloud Cost Optimization". Design is functional but dated (standard corporate blue/white).
*   **Audit Tool (`audit.cloudtuner.ai`)**: Modern, dark/light mode web app. Focus on "Smart Contract Security". Distinct, more tech-forward design system.
*   **Pricing (`/pricing-new`)**: Three-tier pricing model (Free, Pro, Enterprise).
*   **Contact (`/contact-us`)**: Standard form and FAQ.

### Key Findings
*   **Fragmentation**: The "Audit" tool and "Main" site feel like two different companies.
*   **Design Disconnect**: The main site uses a generic corporate style, while the Audit tool uses a modern SaaS aesthetic.
*   **Navigation**: Multiple subdomains and pages with overlapping intent.

## 2. Modernization Strategy

### Core Philosophy
**"One Platform, Total Cloud Confidence."**
Consolidate the *Cost* (CloudTuner) and *Security* (Audit) value propositions into a single, cohesive brand narrative. Adopt the **Audit tool's modern aesthetic** (Dark Mode default, vibrant gradients) as the new master brand identity to signal innovation and technical depth.

### Consolidated Site Architecture
1.  **Home (`/`)**: Unified value prop. "Optimize Costs, Secure Contracts."
2.  **Platform**:
    *   **Cost Optimization**: Kubernetes & Cloud spend (Legacy Main).
    *   **Security Audit**: Smart Contract analysis (Legacy Audit).
3.  **Tools**:
    *   **Audit App**: Embedded or linked web app.
    *   **Gas Fees**: Utility tracker.
4.  **Pricing**: Unified table for Cost & Security tiers.
5.  **Resources**: Documentation, Blog, Case Studies.

### Design System (New)
*   **Primary Color**: `#00D4FF` (Cyan/Teal) - Represents Optimization/Flow.
*   **Secondary Color**: `#6C5CE7` (Violet) - Represents Intelligence/AI.
*   **Background**: `#0F172A` (Slate 900) - Modern SaaS dark theme.
*   **Typography**: `Inter` (UI) + `Outfit` (Headings).

## 3. Implementation Plan

### A. React / Next.js (The "Future" Stack)
*   **Framework**: Next.js 14 (App Router) for performance and SEO.
*   **Styling**: Tailwind CSS for rapid, consistent design.
*   **Animation**: Framer Motion for "wow" factor (micro-interactions).
*   **Structure**: Modular components (Hero, FeatureGrid, Pricing).

### B. WordPress (The "Legacy" Bridge)
*   **Theme**: Custom `cloudtuner-modern` theme.
*   **Approach**: Replicate the React design using standard PHP/CSS.
*   **Builder**: Compatible with Gutenberg or Elementor (optional), but core layout hardcoded for speed.

## 4. Deliverables
1.  **React App Source**: Full Next.js project structure.
2.  **WordPress Theme**: Installable theme folder.
3.  **Documentation**: Setup and deployment guides.
