// static/js/script.js (Complete Game Logic - May 24, 2025)
document.addEventListener('DOMContentLoaded', function() {
    try {
        // --- DOM Elements ---
        const emojiDisplay = document.getElementById('emoji-display');
        const categoryText = document.getElementById('category-text');
        const phraseDisplay = document.getElementById('phrase-display');
        const guessInput = document.getElementById('guess-input');
        const submitGuessButton = document.getElementById('submit-guess-button');
        const pauseResumeHintsButton = document.getElementById('pause-resume-hints-button');
        const hintTimerDisplay = document.getElementById('hint-timer-display');
        const messageDisplay = document.getElementById('message-display');
        const scoreDisplay = document.getElementById('score-display');
        const newPuzzleButton = document.getElementById('new-puzzle-button');

        // --- Game State Variables ---
        let currentPuzzle = null;
        let revealedWordsIndices = [];
        let currentTotalScore = 0;
        let currentPuzzleBasePoints = 100;
        let hintTimeoutId = null;
        const HINT_INTERVAL_SECONDS = 15;
        let timeToNextHintTick = HINT_INTERVAL_SECONDS;
        let isHintPaused = false;

        // --- CORE UI Update Functions ---
        function updateScoreDisplay() {
            if (scoreDisplay) scoreDisplay.textContent = currentTotalScore;
        }

        function displayMessage(text, type = 'info') { // type can be 'info', 'success', 'error'
            if (messageDisplay) {
                messageDisplay.textContent = text;
                messageDisplay.className = 'message-display'; // Reset classes
                if (type === 'success') {
                    messageDisplay.classList.add('success');
                } else if (type === 'error') {
                    messageDisplay.classList.add('error');
                }
            }
        }

        function renderPhraseDisplay() {
            if (!currentPuzzle || !phraseDisplay || !currentPuzzle.words) {
                if(phraseDisplay) phraseDisplay.innerHTML = ''; // Clear if no puzzle
                return;
            }
            phraseDisplay.innerHTML = ''; // Clear previous phrase

            currentPuzzle.words.forEach((word, index) => {
                const wordDiv = document.createElement('div');
                wordDiv.classList.add('word');

                if (revealedWordsIndices.includes(index)) {
                    wordDiv.textContent = word;
                } else {
                    // Display blanks for unrevealed words
                    for (let i = 0; i < word.length; i++) {
                        const letterSpan = document.createElement('span');
                        letterSpan.classList.add('letter-blank');
                        letterSpan.textContent = '_';
                        wordDiv.appendChild(letterSpan);
                    }
                }
                phraseDisplay.appendChild(wordDiv);
                // Add a space after each word div, except the last one
                if (index < currentPuzzle.words.length - 1) {
                     const space = document.createTextNode('\u00A0'); // Non-breaking space
                     phraseDisplay.appendChild(space);
                }
            });
        }
        
        function updateHintTimerDisplay(value) {
            if (hintTimerDisplay) hintTimerDisplay.textContent = value;
        }

        // --- Hint Logic Functions ---
        function stopHintTimer() {
            clearTimeout(hintTimeoutId);
            hintTimeoutId = null;
            console.log("Full script: Hint timer stopped.");
        }
        
        function revealNextWordAsHint() {
            if (!currentPuzzle || !currentPuzzle.words) {
                console.log("Full script: revealNextWordAsHint - No current puzzle or words.");
                return;
            }
    
            let wordToRevealGlobalIndex = -1;
            for(let i=0; i < currentPuzzle.words.length; i++){
                if(!revealedWordsIndices.includes(i)){
                    wordToRevealGlobalIndex = i;
                    break;
                }
            }
            
            if (wordToRevealGlobalIndex !== -1) { 
                revealedWordsIndices.push(wordToRevealGlobalIndex);
                renderPhraseDisplay();
                currentPuzzleBasePoints = Math.max(0, currentPuzzleBasePoints - 10); 
                displayMessage(`Hint: Word revealed! Current puzzle points: ${currentPuzzleBasePoints}`, 'info');
                console.log(`Full script: Revealed word index: ${wordToRevealGlobalIndex}`);
            } else {
                console.log("Full script: revealNextWordAsHint - No more words to reveal by index search.");
            }
    
            let allWordsNowRevealed = true;
            for(let i=0; i < currentPuzzle.words.length; i++){
                if(!revealedWordsIndices.includes(i)){
                    allWordsNowRevealed = false;
                    break;
                }
            }

            if (allWordsNowRevealed) {
                updateHintTimerDisplay('All hints given');
                stopHintTimer(); 
            } else {
                timeToNextHintTick = HINT_INTERVAL_SECONDS; 
                updateHintTimerDisplay(timeToNextHintTick);
                if (!isHintPaused) { 
                    hintTimeoutId = setTimeout(hintTick, 1000); 
                }
            }
        }

        function hintTick() { 
            if (isHintPaused || !currentPuzzle) {
                if (!isHintPaused && currentPuzzle && hintTimeoutId) { 
                   // If timer was active but became paused by other means or puzzle ended
                   // For safety, can re-schedule if conditions are met, but revealNextWordAsHint handles rescheduling primarily
                }
                return;
            }

            timeToNextHintTick--;
            updateHintTimerDisplay(timeToNextHintTick);

            if (timeToNextHintTick <= 0) {
                revealNextWordAsHint(); 
            } else {
                hintTimeoutId = setTimeout(hintTick, 1000);
            }
        }

        function startHintTimer() {
            stopHintTimer(); 
            console.log("Full script: Starting hint timer sequence.");

            if (!currentPuzzle || !currentPuzzle.words) {
                 updateHintTimerDisplay('--'); console.log("Full script: No puzzle/words to start hint timer."); return;
            }
            
            let allWordsEffectivelyRevealed = true;
            for(let i=0; i < currentPuzzle.words.length; i++){
                if(!revealedWordsIndices.includes(i)){
                    allWordsEffectivelyRevealed = false;
                    break;
                }
            }

            if (isHintPaused || allWordsEffectivelyRevealed) {
                updateHintTimerDisplay(isHintPaused ? 'Paused' : (allWordsEffectivelyRevealed ? 'All hints given' : '--'));
                console.log(`Full script: Hint timer not starting (paused: ${isHintPaused}, all revealed: ${allWordsEffectivelyRevealed})`);
                return;
            }
    
            timeToNextHintTick = HINT_INTERVAL_SECONDS;
            updateHintTimerDisplay(timeToNextHintTick);
            hintTimeoutId = setTimeout(hintTick, 1000); 
            console.log("Full script: Hint timer initiated.");
        }
        
        function togglePauseHints() {
            if (!currentPuzzle) return;
            isHintPaused = !isHintPaused;
            if (pauseResumeHintsButton) {
                pauseResumeHintsButton.textContent = isHintPaused ? 'Resume Hints' : 'Pause Hints';
            }
            
            if (isHintPaused) {
                clearTimeout(hintTimeoutId); 
                updateHintTimerDisplay('Paused');
                displayMessage('Hints Paused.', 'info');
                console.log("Full script: Hints Paused.");
            } else {
                displayMessage('Hints Resumed.', 'info');
                console.log("Full script: Hints Resumed.");
                let allWordsCurrentlyRevealed = true;
                 if (currentPuzzle && currentPuzzle.words) {
                    for(let i=0; i < currentPuzzle.words.length; i++){
                        if(!revealedWordsIndices.includes(i)){
                            allWordsCurrentlyRevealed = false;
                            break;
                        }
                    }
                }
                if (!allWordsCurrentlyRevealed) {
                     updateHintTimerDisplay(timeToNextHintTick); // Show current countdown before starting tick
                     hintTimeoutId = setTimeout(hintTick, 1000); 
                } else {
                     updateHintTimerDisplay('All hints given');
                }
            }
        }

        // --- Puzzle Fetching & Setup ---
        function resetForNewPuzzle() {
            console.log("Full script: Resetting for new puzzle.");
            revealedWordsIndices = [];
            currentPuzzleBasePoints = 100;
            isHintPaused = false;
            if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = 'Pause Hints';
            if (guessInput) guessInput.value = '';
            if (submitGuessButton) submitGuessButton.disabled = false;
            timeToNextHintTick = HINT_INTERVAL_SECONDS; 
            updateHintTimerDisplay(timeToNextHintTick); // Initialize display
            displayMessage('');
        }

        async function fetchNewPuzzle() {
            console.log("Full script: Fetching new puzzle...");
            if (emojiDisplay) emojiDisplay.textContent = 'Loading...';
            if (categoryText) categoryText.textContent = 'Loading...';
            if (phraseDisplay) phraseDisplay.innerHTML = '';
            displayMessage('');
            stopHintTimer(); 

            try {
                const response = await fetch('/api/generate-puzzle');
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: "Network response was not ok." }));
                    throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
                }
                currentPuzzle = await response.json();
                console.log("Full script: Puzzle data received:", currentPuzzle);

                if (currentPuzzle && currentPuzzle.emojis_list && currentPuzzle.phrase && currentPuzzle.words && Array.isArray(currentPuzzle.words)) {
                    resetForNewPuzzle();
                    if (emojiDisplay) emojiDisplay.textContent = currentPuzzle.emojis_list.join(' ');
                    if (categoryText) categoryText.textContent = currentPuzzle.category;
                    renderPhraseDisplay();
                    startHintTimer(); 
                } else {
                    console.error("Full script: Invalid puzzle data structure from server.", currentPuzzle);
                    throw new Error("Invalid puzzle data received from server. Missing essential fields or incorrect types.");
                }
            } catch (error) {
                console.error('Full script: Error fetching new puzzle:', error);
                displayMessage(`Error fetching puzzle: ${error.message}`, 'error');
                if (emojiDisplay) emojiDisplay.textContent = 'Error';
                currentPuzzle = null; // Ensure no old puzzle data is used
            }
        }
        
        // --- Guess Handling (with improved normalization) ---
        function handleSubmitGuess() {
            if (!currentPuzzle || !guessInput || !submitGuessButton) {
                console.log("Full script: handleSubmitGuess - prerequisites not met.");
                return;
            }

            function normalizeString(str) {
                if (typeof str !== 'string') return '';
                return str.trim()
                          .toLowerCase()
                          .replace(/\s+/g, ' ')
                          .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?']/g, "");
            }

            const userGuess = normalizeString(guessInput.value);
            const solutionPhrase = normalizeString(currentPuzzle.phrase);

            console.log(`Full script: Normalized User Guess: "${userGuess}"`);
            console.log(`Full script: Normalized Solution Phrase: "${solutionPhrase}"`);

            if (userGuess === '') {
                displayMessage('Please enter a guess.', 'error');
                return;
            }

            if (userGuess === solutionPhrase) {
                stopHintTimer();
                currentTotalScore += currentPuzzleBasePoints;
                
                // Speed bonus: if no words were revealed by hints
                // Check if revealedWordsIndices is empty OR if currentPuzzleBasePoints is still at max.
                // revealedWordsIndices might contain words if the user guessed *while* a hint was showing
                // but before the points for that specific hint were deducted in the next cycle.
                // A simpler check is if currentPuzzleBasePoints is still the initial max.
                if (currentPuzzleBasePoints === 100) { 
                    currentTotalScore += 50; 
                    displayMessage(`Correct! +${currentPuzzleBasePoints} points +50 bonus! Solution: ${currentPuzzle.phrase}`, 'success');
                } else {
                    displayMessage(`Correct! +${currentPuzzleBasePoints} points. Solution: ${currentPuzzle.phrase}`, 'success');
                }
                updateScoreDisplay();
                if (submitGuessButton) submitGuessButton.disabled = true; 
                revealedWordsIndices = currentPuzzle.words.map((_, i) => i); 
                renderPhraseDisplay(); // Show full phrase
            } else {
                displayMessage('Incorrect. Try again!', 'error');
            }
            // Keep guessInput.value for editing on incorrect guess
        }

        // --- Initialization ---
        function initializeGame() {
            console.log("Full script: Initializing new game...");
            updateScoreDisplay();
            fetchNewPuzzle();    
            if (guessInput) guessInput.value = '';
            if (submitGuessButton) submitGuessButton.disabled = false;
        }

        // --- Event Listeners ---
        console.log("Full script: Setting up event listeners...");
        if (newPuzzleButton) {
            newPuzzleButton.addEventListener('click', fetchNewPuzzle);
        } else {
            console.error("Full script Error: New Puzzle button not found!");
        }
        if (submitGuessButton) {
            submitGuessButton.addEventListener('click', handleSubmitGuess);
        } else {
            console.error("Full script Error: Submit Guess button not found!");
        }
        if (guessInput) {
            guessInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    handleSubmitGuess();
                }
            });
        } else {
            console.error("Full script Error: Guess Input not found!");
        }
        if (pauseResumeHintsButton) {
            pauseResumeHintsButton.addEventListener('click', togglePauseHints);
        } else {
            console.error("Full script Error: Pause/Resume Hints button not found!");
        }
        console.log("Full script: Event listeners setup complete.");

        // --- Start the game ---
        console.log("Full script: Calling initializeGame().");
        initializeGame();
        console.log("Full script: initializeGame() called.");

    } catch (e) {
        console.error("CRITICAL SCRIPT ERROR CAUGHT:", e);
        console.error("Error name:", e.name);
        console.error("Error message:", e.message);
        if (e.stack) {
            console.error("Error stack:", e.stack);
        }
        const body = document.querySelector('body');
        if (body) {
            const errorDiv = document.createElement('div');
            errorDiv.style.color = 'red'; errorDiv.style.backgroundColor = 'white';
            errorDiv.style.padding = '20px'; errorDiv.style.border = '2px solid red';
            errorDiv.style.position = 'fixed'; errorDiv.style.top = '10px';
            errorDiv.style.left = '10px'; errorDiv.style.zIndex = '9999';
            errorDiv.innerHTML = `<h2>JavaScript Error!</h2>
                                <p><strong>Type:</strong> ${e.name}</p>
                                <p><strong>Message:</strong> ${e.message}</p>
                                <pre>${e.stack || 'No stack trace available.'}</pre>
                                <p>Check the browser console for more details.</p>`;
            body.innerHTML = ''; 
            body.appendChild(errorDiv);
        }
    }
});
console.log('Full script.js parsed (outside DOMContentLoaded)');