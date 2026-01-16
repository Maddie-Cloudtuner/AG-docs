# CloudTuner Modern Web Presence

This project contains the consolidated and modernized web assets for CloudTuner.ai. It includes two implementations:
1.  **React Application**: A modern, high-performance Next.js app.
2.  **WordPress Theme**: A custom theme mirroring the new design for legacy compatibility.

## 📂 Project Structure

```
/website
├── /react-app              # Next.js 14 Application
│   ├── /src
│   │   ├── /app            # App Router Pages (Home, Pricing, Contact)
│   │   ├── /components     # Reusable UI Components (Navbar, Hero, etc.)
│   │   └── /styles         # Global Styles & Tailwind Config
│   ├── package.json        # Dependencies
│   └── tailwind.config.ts  # Design System Configuration
│
├── /wordpress-theme        # Custom WordPress Theme
│   └── /cloudtuner-modern  # Theme Files
│       ├── style.css       # Theme Metadata & Styles
│       ├── functions.php   # Theme Logic & Enqueueing
│       ├── index.php       # Main Template
│       ├── header.php      # Header & Nav
│       └── footer.php      # Footer
│
└── Analysis_and_Plan.md    # Strategic Modernization Plan
```

---

## 🚀 1. React Application Setup (Recommended)

This is the production-ready, future-proof implementation using Next.js 14 and Tailwind CSS.

### Prerequisites
*   Node.js 18+ installed.

### Installation
1.  Navigate to the react app directory:
    ```bash
    cd react-app
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your browser.

### Deployment
*   **Vercel (Recommended)**: Simply push this folder to GitHub and import into Vercel. It will auto-detect Next.js.
*   **Docker**: Run `npm run build` then `npm start`.

---

## 📝 2. WordPress Theme Setup

Use this if you must stay on the existing WordPress CMS but want the new look.

### Installation
1.  Navigate to `/wordpress-theme`.
2.  Zip the `cloudtuner-modern` folder.
3.  Go to your WordPress Admin Dashboard -> Appearance -> Themes -> Add New -> Upload Theme.
4.  Upload the zip file and click **Activate**.

### Configuration
*   **Menus**: Go to Appearance -> Menus. Create a "Primary Menu" and assign it to the "Primary" location.
*   **Tailwind**: The theme currently loads Tailwind via CDN for immediate preview. For production, you should set up a build process to compile the CSS.

---

## 🎨 Design System

*   **Primary Color**: `#00D4FF` (Cyan/Teal)
*   **Secondary Color**: `#6C5CE7` (Violet)
*   **Background**: `#0F172A` (Slate 900)
*   **Fonts**: Inter (UI), Outfit (Headings)

## 🔍 SEO & Performance Notes

*   **Next.js**: Server-side rendering is enabled by default for optimal SEO.
*   **Images**: Use Next.js `<Image>` component for automatic optimization (not fully implemented in this skeleton).
*   **Accessibility**: Semantic HTML tags (`nav`, `main`, `footer`) and ARIA labels are used.
