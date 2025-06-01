# TODO for ConcentrationGameWeb (Step-by-Step)

## 0. Initial Project Setup (Manual)
- [x] **Create Project Directory:**
    - Open your terminal.
    - `mkdir /Users/johnhuberd/PythonProjects/ConcentrationGameWeb`
    - `cd /Users/johnhuberd/PythonProjects/ConcentrationGameWeb`
- [x] **Open in VS Code:**
    - In the terminal (while in the project directory), type: `code .`
- [x] **Set up Python Virtual Environment (Recommended):**
    - Open the VS Code terminal (View > Terminal).
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    - VS Code might prompt you to select this environment as the interpreter. If so, agree. Otherwise, you can select it via the Command Palette (Cmd+Shift+P) -> "Python: Select Interpreter".
- [x] **Install Flask:**
    - In the VS Code terminal (with the virtual environment activated):
    - `pip install Flask requests`

## 1. Backend Development (Python & Flask)

This section focuses on creating the server-side logic.

### 1.1. Basic Flask App Structure
- [x] **Create `src` directory:**
    - In the VS Code explorer, create a new folder named `src` inside your project root (`ConcentrationGameWeb`).
- [x] **Copy Existing Python Files:**
    - Move/copy your existing `model_connector.py`, `generator.py`, and `asset_manager.py` into the `src` directory.
    *Ensure the paths within these files are correct.*

- [x] **Create `app.py` (Your main Flask application):**
    - Inside the `src` directory, create a new file named `app.py`.
    - **Initial content for `app.py`:**
      ```python
      from flask import Flask, jsonify, render_template, send_from_directory # send_from_directory added
      from model_connector import ModelConnector
      from generator import PuzzleGenerator

      app = Flask(__name__, template_folder='../templates', static_folder='../static')

      try:
          puzzle_gen_instance = PuzzleGenerator(model_name="gemma3:27b") # Updated model name
          # ... (rest of the app.py content from your file)
      except Exception as e:
          print(f"CRITICAL: Failed to initialize PuzzleGenerator: {e}")
          puzzle_gen_instance = None

      @app.route('/api/generate-puzzle', methods=['GET'])
      def generate_puzzle_api():
          print("API: Received request for a new puzzle at /api/generate-puzzle")
          if not puzzle_gen_instance:
              # ...
              return jsonify({'error': 'Puzzle generator not initialized or failed to initialize.'}), 500
          try:
              puzzle_details = puzzle_gen_instance.generate_parsed_puzzle_details()
              if puzzle_details and isinstance(puzzle_details, dict) and 'emojis_list' in puzzle_details: # Check for emojis_list
                  print(f"API: Successfully generated puzzle details: {puzzle_details}")
                  return jsonify(puzzle_details) # Send the whole dictionary
              else:
                  # ...
                  return jsonify({'error': error_message}), 500
          except Exception as e:
              # ...
              return jsonify({'error': f'An unexpected server error occurred: {str(e)}'}), 500

      @app.route('/', methods=['GET'])
      def index():
          print("Serving index.html")
          return render_template('index.html')

      # Route to serve manifest.json for PWA
      @app.route('/manifest.json')
      def manifest():
          return send_from_directory(app.static_folder, 'manifest.json')

      # Route to serve service worker
      @app.route('/service-worker.js')
      def service_worker():
          return send_from_directory(app.static_folder, 'service-worker.js')


      if __name__ == '__main__':
          print("Starting Flask development server for ConcentrationGameWeb...")
          app.run(debug=True, host='0.0.0.0', port=5006) # Updated port
      ```

### 1.2. Adjust Existing Python Modules (If Needed)
- [x] **Review `model_connector.py` and `generator.py`:**
    - Ensure they can be imported and used by `app.py` as shown.
    - The `ModelConnector` should be robust. Make sure Ollama is running when you test.
    - The `PuzzleGenerator` should return a dictionary of puzzle details including `emojis_list`, `phrase`, `words`, `category` or `None`.
    - *Commit messages confirm extensive work on `PuzzleGenerator`: added categories, dynamic focus hints, retry logic for duplicates, random category selection, prompt clarity improvements, model name configuration, recent phrase management.*

## 2. Frontend Development (HTML, CSS, JavaScript)

This is where you build what the user sees and interacts with in their browser.

### 2.1. Create Frontend Directory Structure
- [x] **Create `templates` directory:**
    - In your project root (`ConcentrationGameWeb`), create a new folder named `templates`.
- [x] **Create `static` directory:**
    - In your project root (`ConcentrationGameWeb`), create a new folder named `static`.
    - Inside `static`, create two more folders: `css` and `js`.
    - *A `manifest.json` and `apple-touch-icon.png` would also go into `static` for PWA support.*

### 2.2. Create `index.html` (The Main Web Page)
- [x] **Create `index.html`:**
    - Inside the `templates` folder, create a new file named `index.html`.
    - *Content updated to include PWA tags, score display, category display, phrase display, guess input, submit button, hint controls, message display, and new puzzle button as per the provided `index.html`.*

### 2.3. Create `style.css` (For Styling the Page)
- [x] **Create `style.css`:**
    - Inside the `static/css` folder, create a new file named `style.css`.
    - *Content reflects the provided `style.css` including game container, header, score, puzzle area, emoji display, category, phrase display, interaction area, buttons, and message styling.*

### 2.4. Create `script.js` (For Frontend Logic)
- [x] **Create `script.js`:**
    - Inside the `static/js` folder, create a new file named `script.js`.
    - *Content now handles fetching the puzzle object, displaying emojis, phrase, category, managing score, guess submission, and the letter hint feature logic as per commits.*
    - *Based on commit messages, the script should now handle the full puzzle object (`phrase`, `words`, `category`, `emojis_list`) from the backend.*

## 3. Running and Testing Your Web Application

- [x] **Ensure Ollama is Running:**
    - Your `ModelConnector` needs Ollama to be active.
- [x] **Run the Flask App:**
    - Go to your VS Code terminal where your virtual environment (`venv`) is activated.
    - Navigate into the `src` directory: `cd src`
    - Run the Flask application: `python app.py`
    - Server will run on `http://0.0.0.0:5006/`.
- [x] **Open in Browser:**
    - Open your web browser.
    - Go to the address: `http://127.0.0.1:5006/` or `http://localhost:5006/`.
- [x] **Test Functionality:**
    - Does the page load?
    - Does an initial puzzle (emojis, category, blank phrase) appear?
    - Does the "New Puzzle" button fetch and display a new puzzle?
    - Can you submit guesses? Does it correctly identify right/wrong guesses?
    - Does the score update?
    - Check the VS Code terminal (running `app.py`) for print statements and error messages from the backend.
    - Check the browser's developer console for JavaScript errors.
    - *Letter Hint functionality should also be tested as per section 6.5.*

## 4. Iteration and Refinement
- [x] **Troubleshooting:** (This is an ongoing task)
    - **Python/Flask errors:** Look at the terminal where `python app.py` is running.
    - **JavaScript errors:** Open the browser's developer console.
    - **HTML/CSS issues:** Use the browser's "Inspect Element" tool.
- [x] **Styling:** Adjust `style.css` and `mobile.css` to your liking. *Commits indicate UI and styling refactoring.*
- [x] **Error Handling:** Improve error messages and resilience in both Python and JavaScript.
- [x] **LLM Prompts:** Refine prompts in `generator.py` if the puzzle quality isn't what you want. *Commits indicate significant work here.*

## 5. Documentation
- [ ] Update `README.md` with setup and usage instructions for the web application (how to start the Python backend server, how to access in browser).
- [ ] Add/Update LICENSE.

## Features Added (Based on Commits - Consider if these were tracked and can be checked, or if they were new additions)
- [x] **PWA Support:** Added `manifest.json`, service worker routes in `app.py`, PWA meta tags in `index.html`, and `apple-touch-icon.png`.
- [x] **Mobile Styling:** Added `mobile.css` for responsive design.
- [x] **Score Display:** Implemented score display and logic.
- [x] **PuzzleGenerator - Advanced Features:**
    - [x] Expanded categories (108+ new).
    - [x] Dynamic focus hints.
    - [x] Retry logic for duplicate phrases & max retry attempts.
    - [x] Random category selection.
    - [x] Management of recently used phrases.

## 6. Adding Letter Hint Feature ("Help Me" Button)

This section adds individual letter hints to complement the existing word hints system. *Commits confirm this feature is largely implemented.*

### 6.1. Backend API Enhancement (Optional - No Changes Needed)
- [x] **Review Current API Response:**
    - The existing `/api/generate-puzzle` endpoint already returns all needed data (`phrase`, `words`, `category`, `emojis_list`)
    - No backend changes required since letter hints will be handled entirely on the frontend.
    - The puzzle data structure supports both word-level and letter-level hint logic.

### 6.2. Frontend HTML Structure Updates
- [x] **Update `templates/index.html`:**
    - **Add Letter Hint Button** to the hint controls section:
      ```html
      <div class="hint-controls">
          <button id="pause-resume-hints-button">Pause Game</button> <button id="letter-hint-button">💡 Letter Hint</button> <div>Time to next hint: <span id="hint-timer-display">--</span>s</div>
          <div>Letter hints used: <span id="letter-hints-used-display">0</span>/3</div>
      </div>
      ```
    - **Add Letter Hint Cost Display**:
      ```html
      <div class="hint-info">
          <small>Letter hints cost 5 points each</small>
      </div>
      ```

### 6.3. CSS Styling Updates
- [x] **Update `static/css/style.css`:**
    - **Style the Letter Hint Button:**
      ```css
      #letter-hint-button {
          background-color: #ff5722; /* Orange-red for distinction */
          color: white;
          margin-left: 10px; /* Retained from original TODO */
      }
      
      #letter-hint-button:hover {
          background-color: #e64a19;
      }
      
      #letter-hint-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
      }
      ```
    - **Style Hinted Letters Differently:**
      ```css
      /* In style.css */
      .phrase-display .letter-hinted {
          color: #ff5722;
          background-color: #fff3e0;
          border-radius: 3px;
          padding: 0 2px;
          border-bottom: 2px solid #ff5722;
          /* Other properties from style.css as needed */
      }
      
      .hint-info { /* style.css has this */
          font-size: 12px;
          color: #666;
          margin-top: 5px;
          text-align: center;
      }
      ```

- [x] **Update `static/css/mobile.css`:**
    - **Add Mobile-Friendly Letter Hint Button:**
      ```css
      /* In mobile.css */
      #letter-hint-button {
          background-color: #ff5722;
          color: white;
          margin: 5px 0; /* from mobile.css */
          width: 100%;   /* from mobile.css */
      }
      
      #letter-hint-button:active { /* from mobile.css */
          background-color: #e64a19;
          transform: scale(0.98);
      }
      
      .hint-controls { /* from mobile.css */
          flex-direction: column;
          gap: 10px;
          /* align-items: center; might be useful from mobile.css */
      }
      /* Ensure .phrase-display .letter-hinted is also styled for mobile if needed */
      .phrase-display .letter-hinted { /* from mobile.css */
          font-size: 24px; /* Example from mobile.css */
          /* other mobile specific styles */
      }
      ```

### 6.4. JavaScript Logic Implementation
- [x] **Update `static/js/script.js` - Add New Variables:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      let revealedLetterPositions = [];
      let letterHintsUsed = 0;
      const MAX_LETTER_HINTS = 3;
      const LETTER_HINT_COST = 5;
      // let currentTotalScore; // (Assumed to exist elsewhere)
      // let currentPuzzle; // (Assumed to exist elsewhere)
      // const HINT_INTERVAL_SECONDS; // (Assumed to exist elsewhere)
      ```

- [x] **Add Letter Hint DOM Element Reference:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      const letterHintButton = document.getElementById('letter-hint-button');
      const letterHintsUsedDisplay = document.getElementById('letter-hints-used-display');
      // const phraseDisplay = document.getElementById('phrase-display'); // (Assumed to exist elsewhere)
      // const pauseResumeHintsButton = document.getElementById('pause-resume-hints-button'); // (Assumed to exist elsewhere)
      // const guessInput = document.getElementById('guess-input'); // (Assumed to exist elsewhere)
      // const submitGuessButton = document.getElementById('submit-guess-button'); // (Assumed to exist elsewhere)
      ```

- [x] **Create Letter Hint Core Functions:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      function updateLetterHintDisplay() { /* ... */ }
      function getAvailableLetterPositions() { /* ... */ }
      function revealRandomLetter() { /* ... */ }
      // function updateScoreDisplay() { /* ... (Assumed) */ }
      // function displayMessage(message, type) { /* ... (Assumed) */ }
      ```

- [x] **Update renderPhraseDisplay Function:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      function renderPhraseDisplay() { /* ...modified to show letter-hinted class ... */ }
      ```

- [x] **Update Reset Function:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      function resetForNewPuzzle() {
          // ...
          revealedLetterPositions = [];
          letterHintsUsed = 0;
          // ...
          updateLetterHintDisplay();
          // ...
      }
      ```

- [x] **Add Event Listener:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      if (letterHintButton) {
          letterHintButton.addEventListener('click', revealRandomLetter);
      }
      ```

- [x] **Update initializeGame Function:**
    - *Confirmed by commits enhancing letter hint functionality.*
      ```javascript
      function initializeGame() {
          // ...
          updateLetterHintDisplay();
          // ...
      }
      ```

### 6.5. Testing the Letter Hint Feature
- [ ] **Basic Functionality Tests:** (Mark as 'in progress' or 'to be verified')
    - Load a new puzzle and verify the "💡 Letter Hint" button appears.
    - Click the letter hint button and verify:
        - A random letter is revealed in the puzzle display.
        - The letter appears highlighted/styled differently.
        - Score decreases by 5 points.
        - Letter hints counter increases (0/3 → 1/3).
        - Success message appears.
- [ ] **Boundary Tests:** (Mark as 'in progress' or 'to be verified')
    - Use all 3 letter hints and verify button becomes disabled.
    - Test with low score (< 5 points) and verify button is disabled.
    - Test letter hints on words that get revealed by automatic word hints.
- [ ] **Mobile Testing:** (Mark as 'in progress' or 'to be verified')
    - Test button layout and functionality on mobile viewport.
    - Verify button styling and touch interactions work properly.
- [ ] **Integration Tests:** (Mark as 'in progress' or 'to be verified')
    - Test letter hints combined with word hints.
    - Test letter hints with guess submission.
    - Test letter hints with pause/resume functionality.

### 6.6. Refinement and Polish
- [ ] **Visual Improvements:** (Some done via general UI commits, but specific animations etc. might be pending)
    - Consider adding animation when letters are revealed.
    - Test color contrast for hinted letters.
    - Ensure mobile layout doesn't break with new elements. *Mobile styles were added.*
- [ ] **UX Improvements:**
    - Add confirmation dialog for letter hints when score is low.
    - Consider showing which letters are available for hinting.
    - Add sound effects (optional).
- [ ] **Performance:**
    - Ensure letter position tracking doesn't impact game performance.
    - Test with longer phrases to ensure UI remains responsive.

## 7. Iteration and Refinement (Updated)
- [ ] **Troubleshooting:** (Ongoing)
    - **Python/Flask errors:** Look at the terminal where `python app.py` is running.
    - **JavaScript errors:** Open the browser's developer console.
    - **HTML/CSS issues:** Use the browser's "Inspect Element" tool.
    - **Letter hint bugs:** Check console for letter position tracking errors.
- [ ] **Styling:** Adjust `style.css` and `mobile.css` to your liking. (Ongoing, commits indicate work here).
- [ ] **Error Handling:** Improve error messages and resilience in both Python and JavaScript. (Ongoing).
- [ ] **LLM Prompts:** Refine prompts in `generator.py` if the puzzle quality isn't what you want. (Ongoing, significant work committed).
- [ ] **Game Balance:** Adjust letter hint costs, limits, and scoring based on gameplay testing.

## 8. Documentation (Updated)
- [ ] Update `README.md` with setup and usage instructions for the web application (how to start the Python backend server, how to access in browser).
- [ ] Document the letter hint feature and game mechanics.
- [ ] Document PWA features.
- [ ] Add/Update LICENSE.

## 🎁 Stretch Goals (From previous PRD)
- [ ] Add UI for selecting different LLM models. *(Model name is configurable in code but not via UI yet)*
- [ ] Allow users to copy the emoji sequence.
- [ ] Implement a simple history of generated puzzles.
- [ ] Advanced letter hint options (choose specific positions, vowels first, etc.)
- [ ] Hint combination bonuses (word + letter hints create different scoring)
- [ ] ... and other ideas you have!