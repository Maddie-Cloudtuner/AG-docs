# CloudTuner Design System v3: "Approachable FinOps"

## 1. Strategic Pivot
*   **Goal**: Position CloudTuner as a partner for Finance & DevOps teams.
*   **Tone**: Supportive, energetic, grounded. "We help you do more with less."
*   **Visuals**: Clean, professional, trustworthy. Less "Cyberpunk", more "Modern SaaS" (e.g., Linear, Stripe, Datadog).

## 2. Visual Identity Refresh

### Color Palette "Clear Skies"
*   **Background**: `#0F172A` (Slate 900) - Deep, professional blue-grey. (Softer than the previous black).
*   **Primary**: `#3B82F6` (Blue 500) - Trust, stability, clarity.
*   **Secondary**: `#10B981` (Emerald 500) - Savings, growth, sustainability.
*   **Accent**: `#F59E0B` (Amber 500) - Alerts, attention (used sparingly).
*   **Typography**:
    *   **Headings**: `Plus Jakarta Sans` (Modern, friendly, geometric).
    *   **Body**: `Inter` (Standard, highly legible).

### Content Strategy
*   **Hero**: Focus on "Balancing budgets, innovation, and sustainability."
*   **Features**:
    *   **Core**: Multi-cloud analytics, Tagging/Visibility, Enterprise Workflows.
    *   **Subtle**: Web3 (Gas/Deployment costs), Carbon Tracking.
*   **Copy**: "Stop guessing," "Take control," "Your team's new favorite tool."

## 3. Component Updates

### React App
*   **`Hero.tsx`**: Remove "Command Center" rhetoric. Use "The FinOps Platform for Modern Teams."
*   **`BentoGrid.tsx`** -> **`FeatureShowcase.tsx`**: Focus on Analytics & Workflows. Move Web3 to a "Future-Proofing" section.
*   **`Navbar.tsx`**: Clean, professional links.

### WordPress Theme
*   Update CSS variables to match new palette.
*   Update typography.

## 4. Implementation Steps
1.  Update `tailwind.config.ts` (Colors/Fonts).
2.  Rewrite `Hero.tsx` with new copy.
3.  Refactor `BentoGrid` to `Features.tsx` with new hierarchy.
4.  Update `page.tsx` to restructure sections.
5.  Sync WordPress theme.
