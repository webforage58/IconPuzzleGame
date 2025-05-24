# TODO for ConcentrationGameWeb (Step-by-Step)

## 0. Initial Project Setup (Manual)
- [ ] **Create Project Directory:**
    - Open your terminal.
    - `mkdir /Users/johnhuberd/PythonProjects/ConcentrationGameWeb`
    - `cd /Users/johnhuberd/PythonProjects/ConcentrationGameWeb`
- [ ] **Open in VS Code:**
    - In the terminal (while in the project directory), type: `code .`
- [ ] **Set up Python Virtual Environment (Recommended):**
    - Open the VS Code terminal (View > Terminal).
    - `python3 -m venv venv`  (This creates a virtual environment named 'venv')
    - `source venv/bin/activate` (On macOS/Linux. For Windows: `venv\Scripts\activate`)
    - VS Code might prompt you to select this environment as the interpreter. If so, agree. Otherwise, you can select it via the Command Palette (Cmd+Shift+P) -> "Python: Select Interpreter".
- [ ] **Install Flask:**
    - In the VS Code terminal (with the virtual environment activated):
    - `pip install Flask requests` (Requests is for your `model_connector.py`)

## 1. Backend Development (Python & Flask)

This section focuses on creating the server-side logic.

### 1.1. Basic Flask App Structure
- [x ] **Create `src` directory:**
    - In the VS Code explorer, create a new folder named `src` inside your project root (`ConcentrationGameWeb`).
- [ x] **Copy Existing Python Files:**
    - Move/copy your existing `model_connector.py`, `generator.py`, and `asset_manager.py` (if still needed for font paths, though less critical for web rendering) into the `src` directory.
    *Ensure the paths within these files (like `PROJECT_ROOT` in `asset_manager.py`) are still correct or adjust them. For a web app, `Path(__file__).resolve().parent.parent` might behave differently depending on where you run the app from.*

- [ ] **Create `app.py` (Your main Flask application):**
    - Inside the `src` directory, create a new file named `app.py`.
    - **Initial content for `app.py`:**
      ```python
      from flask import Flask, jsonify, render_template
      # Assuming your generator and connector are in the same 'src' directory
      from model_connector import ModelConnector # Make sure this import works
      from generator import PuzzleGenerator   # Make sure this import works

      # Initialize the Flask application
      app = Flask(__name__, template_folder='../templates', static_folder='../static')
      # Explanation:
      # Flask(__name__): Creates an instance of the Flask application.
      # template_folder='../templates': Tells Flask to look for HTML files in a 'templates' folder
      #                                 located one level up from 'src' (i.e., in the project root).
      # static_folder='../static': Tells Flask to look for static files (CSS, JS, images) in a
      #                            'static' folder, also in the project root.

      # Initialize your puzzle generator
      # You might want to configure the model name based on your preference or availability
      puzzle_gen = PuzzleGenerator(model_name="gemma:2b") # Or your preferred model

      # --- API Endpoint to Generate Puzzles ---
      @app.route('/api/generate-puzzle', methods=['GET'])
      def generate_puzzle_api():
          """
          API endpoint to generate a new emoji puzzle.
          Called by the JavaScript on the frontend.
          """
          print("Received request for a new puzzle...")
          emoji_list = puzzle_gen.generate_parsed_emoji_puzzle()
          if emoji_list:
              print(f"Generated emoji list: {emoji_list}")
              return jsonify({'emojis': emoji_list})
          else:
              print("Failed to generate emoji list.")
              # Return an error or an empty list with a status
              return jsonify({'error': 'Failed to generate puzzle'}), 500

      # --- Route to Serve the Main HTML Page ---
      @app.route('/', methods=['GET'])
      def index():
          """
          Serves the main HTML page (index.html).
          This is what users see when they go to your app's main URL.
          """
          print("Serving index.html")
          # Flask will look for 'index.html' in your 'templates' folder.
          return render_template('index.html')

      # --- Main Block to Run the App ---
      if __name__ == '__main__':
          # Runs the Flask development server.
          # debug=True: Enables debug mode, which provides helpful error messages
          #             and auto-reloads the server when you make code changes.
          # host='0.0.0.0': Makes the server accessible from any IP address on your network
          #                 (useful for testing, though for purely local, '127.0.0.1' is also fine).
          # port=5000: The port number the server will listen on.
          print("Starting Flask development server...")
          app.run(debug=True, host='0.0.0.0', port=5000)
      ```

### 1.2. Adjust Existing Python Modules (If Needed)
- [ ] **Review `model_connector.py` and `generator.py`:**
    - Ensure they can be imported and used by `app.py` as shown.
    - The `ModelConnector` should be robust. Make sure Ollama is running when you test.
    - The `PuzzleGenerator` should return a list of emoji strings or `None`.

## 2. Frontend Development (HTML, CSS, JavaScript)

This is where you build what the user sees and interacts with in their browser.

### 2.1. Create Frontend Directory Structure
- [ ] **Create `templates` directory:**
    - In your project root (`ConcentrationGameWeb`), create a new folder named `templates`. This is where Flask looks for HTML files.
- [ ] **Create `static` directory:**
    - In your project root (`ConcentrationGameWeb`), create a new folder named `static`. This is where Flask looks for CSS, JavaScript, and any other static files.
    - Inside `static`, create two more folders: `css` and `js`.

### 2.2. Create `index.html` (The Main Web Page)
- [ ] **Create `index.html`:**
    - Inside the `templates` folder, create a new file named `index.html`.
    - **Initial content for `index.html`:**
      ```html
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Emoji Puzzle Game</title>
          <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
          </head>
      <body>
          <div class="container">
              <h1>Emoji Puzzle</h1>
              <div id="puzzle-display" class="emoji-puzzle">
                  Loading puzzle...
              </div>
              <button id="new-puzzle-button">New Puzzle</button>
          </div>

          <script src="{{ url_for('static', filename='js/script.js') }}"></script>
      </body>
      </html>
      ```

### 2.3. Create `style.css` (For Styling the Page)
- [ ] **Create `style.css`:**
    - Inside the `static/css` folder, create a new file named `style.css`.
    - **Initial content for `style.css`:**
      ```css
      body {
          font-family: sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
          background-color: #f0f0f0;
          color: #333;
      }

      .container {
          text-align: center;
          background-color: white;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      h1 {
          color: #1a73e8; /* A nice blue */
      }

      .emoji-puzzle {
          font-family: 'Noto Color Emoji', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif; /* Font stack for emojis */
          font-size: 64px; /* Large emojis */
          margin-top: 20px;
          margin-bottom: 30px;
          padding: 20px;
          background-color: #e8f0fe; /* Light blue background for the puzzle */
          border-radius: 4px;
          min-height: 80px; /* Ensure space even when loading */
          display: flex; /* For better alignment if needed */
          justify-content: center;
          align-items: center;
      }

      #new-puzzle-button {
          background-color: #1a73e8;
          color: white;
          border: none;
          padding: 12px 24px;
          font-size: 16px;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.3s ease;
      }

      #new-puzzle-button:hover {
          background-color: #1558b3; /* Darker blue on hover */
      }
      ```

### 2.4. Create `script.js` (For Frontend Logic)
- [ ] **Create `script.js`:**
    - Inside the `static/js` folder, create a new file named `script.js`.
    - **Initial content for `script.js`:**
      ```javascript
      // Wait for the entire HTML document to be fully loaded and parsed
      document.addEventListener('DOMContentLoaded', function() {
          // Get references to the HTML elements we need to interact with
          const puzzleDisplay = document.getElementById('puzzle-display');
          const newPuzzleButton = document.getElementById('new-puzzle-button');

          // --- Function to Fetch and Display a New Puzzle ---
          async function fetchAndDisplayPuzzle() {
              puzzleDisplay.textContent = 'Loading puzzle...'; // Show loading message
              try {
                  // Make a GET request to our Flask API endpoint
                  const response = await fetch('/api/generate-puzzle');

                  if (!response.ok) {
                      // If the server responded with an error (e.g., 500)
                      const errorData = await response.json();
                      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                  }

                  // Parse the JSON response from the server
                  const data = await response.json();

                  if (data.emojis && data.emojis.length > 0) {
                      // Join the array of emojis into a single string with spaces
                      puzzleDisplay.textContent = data.emojis.join(' ');
                  } else {
                      puzzleDisplay.textContent = 'No puzzle found. Try again!';
                  }
              } catch (error) {
                  // Log any errors to the console and display an error message
                  console.error('Error fetching puzzle:', error);
                  puzzleDisplay.textContent = `Error: ${error.message}`;
              }
          }

          // --- Event Listener for the "New Puzzle" Button ---
          if (newPuzzleButton) { // Check if the button exists
              newPuzzleButton.addEventListener('click', fetchAndDisplayPuzzle);
          } else {
              console.error("New Puzzle button not found!");
          }

          // --- Load the first puzzle when the page loads ---
          fetchAndDisplayPuzzle();
      });
      ```

## 3. Running and Testing Your Web Application

- [ ] **Ensure Ollama is Running:**
    - Your `ModelConnector` needs Ollama to be active. Open a separate terminal and ensure your Ollama service is running (e.g., `ollama serve` if you don't have it running as a background service).
- [ ] **Run the Flask App:**
    - Go to your VS Code terminal where your virtual environment (`venv`) is activated.
    - Navigate into the `src` directory: `cd src`
    - Run the Flask application: `python app.py`
    - You should see output indicating the server is running, typically like:
      ```
      * Serving Flask app 'app'
      * Debug mode: on
      * Running on [http://0.0.0.0:5000/](http://0.0.0.0:5000/)
      * Restarting with stat
      * Debugger is active!
      * Debugger PIN: xxx-xxx-xxx
      ```
- [ ] **Open in Browser:**
    - Open your web browser (Safari, Chrome, Firefox on your Mac mini).
    - Go to the address: `http://127.0.0.1:5000/` or `http://localhost:5000/`.
- [ ] **Test Functionality:**
    - Does the page load?
    - Does an initial puzzle appear?
    - Does the "New Puzzle" button fetch and display a new puzzle?
    - Check the VS Code terminal (running `app.py`) for print statements and error messages from the backend.
    - Check the browser's developer console (usually F12 or Right-click > Inspect > Console) for JavaScript errors or `console.log` messages.

## 4. Iteration and Refinement
- [ ] **Troubleshooting:**
    - **Python/Flask errors:** Look at the terminal where `python app.py` is running. Debug mode will show detailed tracebacks.
    - **JavaScript errors:** Open the browser's developer console.
    - **HTML/CSS issues:** Use the browser's "Inspect Element" tool to examine the HTML structure and applied CSS.
- [ ] **Styling:** Adjust `style.css` to your liking.
- [ ] **Error Handling:** Improve error messages and resilience in both Python and JavaScript.
- [ ] **LLM Prompts:** Refine prompts in `generator.py` if the puzzle quality isn't what you want.

## 5. Documentation
- [ ] Update `README.md` with setup and usage instructions for the web application (how to start the Python backend server, how to access in browser).
- [ ] Add/Update LICENSE.

## 🎁 Stretch Goals (From previous PRD)
- [ ] Add UI for selecting different LLM models.
- [ ] Allow users to copy the emoji sequence.
- [ ] Implement a simple history of generated puzzles.
- [ ] ... and other ideas you have!