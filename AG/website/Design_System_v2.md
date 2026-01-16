# CloudTuner Design System v2: "Hyper-Scale"

## 1. Critique of v1
*   **Issue**: "Generic AI look." Standard centered hero, 3-column pricing, basic dark mode.
*   **Goal**: Align with top-tier FinOps (precision, data) and Web3 (futurism, glass).
*   **Inspiration**: Linear, Raycast, Dune Analytics, Vercel.

## 2. Visual Identity Refresh

### Color Palette "Deep Space"
*   **Background**: `#030712` (Rich Black) with subtle noise texture.
*   **Primary Accent**: `#6366F1` (Electric Indigo) → `#A855F7` (Purple) gradient.
*   **Secondary Accent**: `#10B981` (Emerald) for "Savings/Positive Data".
*   **Surface**: `rgba(255, 255, 255, 0.03)` with `backdrop-blur-xl`.
*   **Borders**: `rgba(255, 255, 255, 0.08)` (Subtle, crisp).

### Typography
*   **Headings**: `Space Grotesk` - Technical, geometric, distinct.
*   **Body**: `Plus Jakarta Sans` - Highly legible, modern geometric sans.
*   **Monospace**: `JetBrains Mono` - For code snippets and data values.

### UI Patterns
*   **Bento Grids**: Asymmetric, content-dense feature layouts.
*   **Glassmorphism**: High-quality blur effects.
*   **Micro-interactions**: Hover glows, border shines.
*   **Data Visualization**: Abstract representations of charts/graphs in the hero.

## 3. Component Overhaul

### Hero Section
*   **Old**: Centered text + buttons.
*   **New**: Split layout or "Hero with Dashboard Preview". Large, gradient text. "Trusted by" ticker immediately visible.

### Feature Section
*   **Old**: 4-column grid with icons.
*   **New**: "Bento Grid" layout. Cards of different sizes. Some showing code, some showing stats, some showing text.

### Navbar
*   **Old**: Full width, sticky.
*   **New**: Floating "Pill" navbar, centered, detached from top.

## 4. Implementation Steps
1.  Update `tailwind.config.ts` with new fonts/colors.
2.  Install new fonts in `layout.tsx`.
3.  Create `BentoGrid` component.
4.  Redesign `Hero` with "Glow" effects.
5.  Update `Navbar` to floating style.
6.  Apply changes to WordPress theme CSS.
