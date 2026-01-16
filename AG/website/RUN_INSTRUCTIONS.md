# How to Run the CloudTuner Website Locally

This guide will help you get the new "Hyper-Scale" website running on your machine. You have two options: the **React Application** (Recommended) or the **WordPress Theme**.

---

## Option 1: Running the React Application (Next.js)
**Best for:** Viewing the full interactive experience, animations, and modern design.

### Prerequisites
*   **Node.js**: You need Node.js installed (version 18 or higher).
    *   Check if installed: Open terminal and type `node -v`
    *   Download: [nodejs.org](https://nodejs.org/)

### Steps
1.  **Open your terminal** (PowerShell, Command Prompt, or VS Code Terminal).
2.  **Navigate to the project folder**:
    ```powershell
    cd "c:\Users\LENOVO\Desktop\my_docs\AG\website\react-app"
    ```
3.  **Install Dependencies**:
    This downloads all the necessary libraries (Next.js, React, Tailwind, etc.).
    ```powershell
    npm install
    ```
4.  **Start the Development Server**:
    ```powershell
    npm run dev
    ```
5.  **View in Browser**:
    *   Open your web browser (Chrome, Edge, etc.).
    *   Go to: `http://localhost:3000`

### Troubleshooting
*   **Error: "npm is not recognized"**: You need to install Node.js.
*   **Error: "EADDRINUSE: address already in use"**: Something else is running on port 3000. Try `npm run dev -- -p 3001` to run on port 3001 instead.

---

## Option 2: Installing the WordPress Theme
**Best for:** Applying the design to an existing WordPress content management system.

### Prerequisites
*   A local WordPress environment (e.g., **LocalWP**, **XAMPP**, or **Docker**).
    *   Easiest tool: [LocalWP](https://localwp.com/) (Free and simple).

### Steps
1.  **Locate the Theme Folder**:
    The theme files are located at:
    `c:\Users\LENOVO\Desktop\my_docs\AG\website\wordpress-theme\cloudtuner-modern`

2.  **Create a Zip File**:
    *   Right-click the `cloudtuner-modern` folder.
    *   Select **Send to** > **Compressed (zipped) folder**.
    *   Name it `cloudtuner-modern.zip`.

3.  **Upload to WordPress**:
    *   Log in to your local WordPress Admin Dashboard (usually `http://localhost/wp-admin`).
    *   Go to **Appearance** > **Themes**.
    *   Click **Add New** (top button).
    *   Click **Upload Theme**.
    *   Choose the `cloudtuner-modern.zip` file you just created.
    *   Click **Install Now**.
    *   Click **Activate**.

4.  **Setup Menu**:
    *   Go to **Appearance** > **Menus**.
    *   Create a new menu called "Main Menu".
    *   Add your pages (Home, About, etc.).
    *   Check the box **Display location: Primary Menu**.
    *   Click **Save Menu**.

---

## Which one should I use?
*   **Use React (Option 1)** if you want to see the "perfect" version of the design with all the smooth animations and instant page loads. This is what modern startups use.
*   **Use WordPress (Option 2)** only if you are required to use WordPress for content management. The design is similar but may lack some of the advanced interactivity of the React version.
