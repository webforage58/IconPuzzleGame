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
## 6. Adding Letter Hint Feature ("Help Me" Button)

This section adds individual letter hints to complement the existing word hints system.

### 6.1. Backend API Enhancement (Optional - No Changes Needed)
- [ ] **Review Current API Response:**
    - The existing `/api/generate-puzzle` endpoint already returns all needed data (`phrase`, `words`, `category`, `emojis_list`)
    - No backend changes required since letter hints will be handled entirely on the frontend
    - The puzzle data structure supports both word-level and letter-level hint logic

### 6.2. Frontend HTML Structure Updates
- [ ] **Update `templates/index.html`:**
    - **Add Letter Hint Button** to the hint controls section:
      ```html
      <div class="hint-controls">
          <button id="pause-resume-hints-button">Pause Game</button>
          <button id="letter-hint-button">💡 Letter Hint</button>
          <div>Time to next hint: <span id="hint-timer-display">--</span>s</div>
          <div>Letter hints used: <span id="letter-hints-used-display">0</span>/3</div>
      </div>
      ```
    - **Add Letter Hint Cost Display** (optional):
      ```html
      <div class="hint-info">
          <small>Letter hints cost 5 points each</small>
      </div>
      ```

### 6.3. CSS Styling Updates
- [ ] **Update `static/css/style.css`:**
    - **Style the Letter Hint Button:**
      ```css
      #letter-hint-button {
          background-color: #ff5722; /* Orange-red for distinction */
          color: white;
          margin-left: 10px;
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
      .phrase-display .letter-hinted {
          color: #ff5722;
          background-color: #fff3e0;
          border-radius: 3px;
          padding: 0 2px;
          border-bottom: 2px solid #ff5722;
      }
      
      .hint-info {
          font-size: 12px;
          color: #666;
          margin-top: 5px;
      }
      ```

- [ ] **Update `static/css/mobile.css`:**
    - **Add Mobile-Friendly Letter Hint Button:**
      ```css
      #letter-hint-button {
          background-color: #ff5722;
          color: white;
          margin: 5px 0;
          width: 100%;
      }
      
      #letter-hint-button:active {
          background-color: #e64a19;
          transform: scale(0.98);
      }
      
      .hint-controls {
          flex-direction: column;
          gap: 10px;
      }
      ```

### 6.4. JavaScript Logic Implementation
- [ ] **Update `static/js/script.js` - Add New Variables:**
    - **Add to Game State Variables section:**
      ```javascript
      let revealedLetterPositions = []; // Array of {wordIndex, letterIndex} objects
      let letterHintsUsed = 0;
      const MAX_LETTER_HINTS = 3;
      const LETTER_HINT_COST = 5;
      ```

- [ ] **Add Letter Hint DOM Element Reference:**
    - **Add to DOM Elements section:**
      ```javascript
      const letterHintButton = document.getElementById('letter-hint-button');
      const letterHintsUsedDisplay = document.getElementById('letter-hints-used-display');
      ```

- [ ] **Create Letter Hint Core Functions:**
    - **Add after existing hint functions:**
      ```javascript
      function updateLetterHintDisplay() {
          if (letterHintsUsedDisplay) {
              letterHintsUsedDisplay.textContent = letterHintsUsed;
          }
          if (letterHintButton) {
              letterHintButton.disabled = letterHintsUsed >= MAX_LETTER_HINTS || 
                                         currentTotalScore < LETTER_HINT_COST ||
                                         !currentPuzzle;
          }
      }

      function getAvailableLetterPositions() {
          const availablePositions = [];
          if (!currentPuzzle || !currentPuzzle.words) return availablePositions;
          
          currentPuzzle.words.forEach((word, wordIndex) => {
              if (!revealedWordsIndices.includes(wordIndex)) {
                  for (let letterIndex = 0; letterIndex < word.length; letterIndex++) {
                      const alreadyRevealed = revealedLetterPositions.some(
                          pos => pos.wordIndex === wordIndex && pos.letterIndex === letterIndex
                      );
                      if (!alreadyRevealed) {
                          availablePositions.push({ wordIndex, letterIndex });
                      }
                  }
              }
          });
          return availablePositions;
      }

      function revealRandomLetter() {
          const availablePositions = getAvailableLetterPositions();
          if (availablePositions.length === 0) {
              displayMessage('No more letters to reveal!', 'info');
              return;
          }
          
          const randomPosition = availablePositions[Math.floor(Math.random() * availablePositions.length)];
          revealedLetterPositions.push(randomPosition);
          
          letterHintsUsed++;
          currentTotalScore = Math.max(0, currentTotalScore - LETTER_HINT_COST);
          
          updateScoreDisplay();
          updateLetterHintDisplay();
          renderPhraseDisplay();
          
          const word = currentPuzzle.words[randomPosition.wordIndex];
          const letter = word[randomPosition.letterIndex];
          displayMessage(`Letter hint: "${letter}" revealed! (-${LETTER_HINT_COST} points)`, 'info');
      }
      ```

- [ ] **Update renderPhraseDisplay Function:**
    - **Modify the existing function to handle individual letter reveals:**
      ```javascript
      function renderPhraseDisplay() {
          if (!currentPuzzle || !phraseDisplay || !currentPuzzle.words) {
              if(phraseDisplay) phraseDisplay.innerHTML = '';
              return;
          }
          phraseDisplay.innerHTML = '';

          currentPuzzle.words.forEach((word, wordIndex) => {
              const wordDiv = document.createElement('div');
              wordDiv.classList.add('word');

              if (revealedWordsIndices.includes(wordIndex)) {
                  // Entire word is revealed
                  wordDiv.textContent = word;
              } else {
                  // Show individual letters/blanks
                  for (let letterIndex = 0; letterIndex < word.length; letterIndex++) {
                      const letterSpan = document.createElement('span');
                      
                      const isLetterRevealed = revealedLetterPositions.some(
                          pos => pos.wordIndex === wordIndex && pos.letterIndex === letterIndex
                      );
                      
                      if (isLetterRevealed) {
                          letterSpan.textContent = word[letterIndex];
                          letterSpan.classList.add('letter-hinted');
                      } else {
                          letterSpan.classList.add('letter-blank');
                          letterSpan.textContent = '_';
                      }
                      wordDiv.appendChild(letterSpan);
                  }
              }
              phraseDisplay.appendChild(wordDiv);
              
              if (wordIndex < currentPuzzle.words.length - 1) {
                   const space = document.createTextNode('\u00A0');
                   phraseDisplay.appendChild(space);
              }
          });
      }
      ```

- [ ] **Update Reset Function:**
    - **Modify resetForNewPuzzle to reset letter hint state:**
      ```javascript
      function resetForNewPuzzle() {
          console.log("Full script: Resetting for new puzzle.");
          revealedWordsIndices = [];
          revealedLetterPositions = []; // Add this line
          letterHintsUsed = 0; // Add this line
          currentPuzzleBasePoints = 100;
          isHintPaused = false;
          if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = 'Pause Game';
          if (guessInput) guessInput.value = '';
          if (submitGuessButton) submitGuessButton.disabled = false;
          timeToNextHintTick = HINT_INTERVAL_SECONDS;
          updateHintTimerDisplay(timeToNextHintTick);
          updateLetterHintDisplay(); // Add this line
          displayMessage('');
      }
      ```

- [ ] **Add Event Listener:**
    - **Add to Event Listeners section:**
      ```javascript
      if (letterHintButton) {
          letterHintButton.addEventListener('click', revealRandomLetter);
      } else {
          console.error("Full script Error: Letter Hint button not found!");
      }
      ```

- [ ] **Update initializeGame Function:**
    - **Add letter hint display update:**
      ```javascript
      function initializeGame() {
          console.log("Full script: Initializing new game...");
          updateScoreDisplay();
          updateLetterHintDisplay(); // Add this line
          fetchNewPuzzle();    
          if (guessInput) guessInput.value = '';
          if (submitGuessButton) submitGuessButton.disabled = false;
      }
      ```

### 6.5. Testing the Letter Hint Feature
- [ ] **Basic Functionality Tests:**
    - Load a new puzzle and verify the "💡 Letter Hint" button appears
    - Click the letter hint button and verify:
        - A random letter is revealed in the puzzle display
        - The letter appears highlighted/styled differently
        - Score decreases by 5 points
        - Letter hints counter increases (0/3 → 1/3)
        - Success message appears
- [ ] **Boundary Tests:**
    - Use all 3 letter hints and verify button becomes disabled
    - Test with low score (< 5 points) and verify button is disabled
    - Test letter hints on words that get revealed by automatic word hints
- [ ] **Mobile Testing:**
    - Test button layout and functionality on mobile viewport
    - Verify button styling and touch interactions work properly
- [ ] **Integration Tests:**
    - Test letter hints combined with word hints
    - Test letter hints with guess submission
    - Test letter hints with pause/resume functionality

### 6.6. Refinement and Polish
- [ ] **Visual Improvements:**
    - Consider adding animation when letters are revealed
    - Test color contrast for hinted letters
    - Ensure mobile layout doesn't break with new elements
- [ ] **UX Improvements:**
    - Add confirmation dialog for letter hints when score is low
    - Consider showing which letters are available for hinting
    - Add sound effects (optional)
- [ ] **Performance:**
    - Ensure letter position tracking doesn't impact game performance
    - Test with longer phrases to ensure UI remains responsive

## 7. Iteration and Refinement (Updated)
- [ ] **Troubleshooting:**
    - **Python/Flask errors:** Look at the terminal where `python app.py` is running. Debug mode will show detailed tracebacks.
    - **JavaScript errors:** Open the browser's developer console.
    - **HTML/CSS issues:** Use the browser's "Inspect Element" tool to examine the HTML structure and applied CSS.
    - **Letter hint bugs:** Check console for letter position tracking errors
- [ ] **Styling:** Adjust `style.css` and `mobile.css` to your liking.
- [ ] **Error Handling:** Improve error messages and resilience in both Python and JavaScript.
- [ ] **LLM Prompts:** Refine prompts in `generator.py` if the puzzle quality isn't what you want.
- [ ] **Game Balance:** Adjust letter hint costs, limits, and scoring based on gameplay testing.

## 8. Documentation (Updated)
- [ ] Update `README.md` with setup and usage instructions for the web application (how to start the Python backend server, how to access in browser).
- [ ] Document the letter hint feature and game mechanics.
- [ ] Add/Update LICENSE.

## 🎁 Stretch Goals (From previous PRD)
- [ ] Add UI for selecting different LLM models.
- [ ] Allow users to copy the emoji sequence.
- [ ] Implement a simple history of generated puzzles.
- [ ] Advanced letter hint options (choose specific positions, vowels first, etc.)
- [ ] Hint combination bonuses (word + letter hints create different scoring)
- [ ] ... and other ideas you have!