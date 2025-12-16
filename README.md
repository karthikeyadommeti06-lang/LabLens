# 🔬 LabLens: Intelligent Component Auditor

> **Theme:** Multimodal Function Calling & Automation
> **Tech Stack:** Python, Streamlit, Google Gemini 2.5-Flash

## 🚀 Overview
LabLens is an AI-powered inventory assistant designed for electronics labs. It uses computer vision to "see" components on a workbench and automatically updates a digital inventory system, eliminating manual counting.

## 💡 Key Features
* **Snap & Audit:** Upload a photo of your hardware; the AI does the counting.
* **Gemini 2.5 Powered:** Uses the latest Flash model for split-second visual reasoning.
* **Function Calling:** The AI doesn't just chat; it executes code to update the database structure.
* **Secure Dashboard:** Features a login system and a real-time metrics dashboard.

## 🛠️ Installation & Run
1.  **Download the repository:**
    
2.  **Install dependencies:**
    ```bash
    pip install streamlit google-generativeai pandas pillow
    ```
3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🤖 How It Works
1.  User uploads an image (e.g., a messy table with Arduinos and Sensors).
2.  Gemini 2.5 analyzes the visual data.
3.  The model triggers the `update_inventory_tool` function with structured JSON data.
4.  The app updates the Pandas DataFrame and refreshes the dashboard metrics.

---

*Submitted for the GenAI Frontiers Hackathon.*
