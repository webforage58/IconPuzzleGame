# ConcentrationGameLocal - Product Requirements Document (Web Version)

## 1. Objective
Build a local web application, "ConcentrationGameWeb," that generates emoji-based logic puzzles (e.g., emoji rebuses) using a local LLM. The puzzles will be rendered in a web browser on a specific Mac mini M4, leveraging its native emoji support and CSS for styling. This is a personal "vibe coding project."

## 2. User & Environment
-   **Primary User:** John Huberd
-   **Development Environment:** Visual Studio Code
-   **Target Machine:** Mac mini M4 (64GB RAM)
-   **Project Directory:** `/Users/johnhuberd/PythonProjects/ConcentrationGameWeb`
-   **Usage:** Solely for personal use on the specified machine. No internet or cloud interaction is expected for core functionality (LLM and puzzle generation remain local). Viewing requires a local web browser.

## 3. Core Features
1.  **Emoji Puzzle Generator (Backend)**
    * Uses a local LLM (Ollama) via Python (`model_connector.py`, `generator.py`) to generate emoji puzzles.
    * Puzzles are short (3–5 emojis) and follow logical or idiomatic patterns.
    * The Python backend will provide an API endpoint for the frontend to fetch generated emoji sequences.

2.  **Puzzle Renderer (Frontend - Browser)**
    * The web browser (on the Mac mini M4) will be responsible for rendering the emoji sequence received from the backend.
    * Utilizes HTML to structure the display of emojis and CSS for styling (e.g., `font-family: 'Noto Color Emoji'`, `font-size`, spacing).
    * Leverages the system's installed emoji fonts for display.

3.  **Puzzle Viewer (Frontend - Web Interface)**
    * A simple web page (HTML, CSS, JavaScript) will serve as the GUI.
    * Displays the emoji puzzle.
    * Will include a button ("New Puzzle") to request a new puzzle from the backend.

## 4. Architecture
-   **Backend:** Python with the **Flask** web framework.
    -   Handles communication with the local LLM (Ollama).
    -   Generates emoji sequences.
    -   Serves the frontend (HTML, CSS, JS files) and provides API endpoints.
-   **Frontend:** HTML, CSS, JavaScript.
    -   Runs in the user's local web browser on the Mac mini M4.
    -   Fetches emoji puzzles from the backend.
    * Renders emojis using browser capabilities and specified CSS fonts (e.g., 'Noto Color Emoji').
-   **LLM:** Small language model (e.g., Gemma 2B/7B or user's choice of installed model) running locally via Ollama.
-   **Emoji Handling:** Primarily relies on the browser's text rendering engine and the system emoji fonts on the Mac mini M4, guided by CSS font preferences.

## 5. Non-Goals
-   No public internet server hosting (the web application is served and accessed locally).
-   No user login or complex database requirements.
-   No advanced AI image generation for the emojis themselves; relies on font-based emoji rendering.
-   Cross-browser or cross-platform compatibility beyond the specified Mac mini M4 setup.