// static/js/script.js (Full game logic with reordered functions + try...catch)
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
        let hintIntervalId = null;
        const HINT_INTERVAL_SECONDS = 15;
        let timeToNextHint = HINT_INTERVAL_SECONDS;
        let isHintPaused = false;
        let unrevealedWordHintIndex = 0;

        // --- CORE UI Update Functions (defined early) ---
        function updateScoreDisplay() {
            if (scoreDisplay) scoreDisplay.textContent = currentTotalScore;
        }

        function displayMessage(text, type = 'info') {
            if (messageDisplay) {
                messageDisplay.textContent = text;
                messageDisplay.className = 'message-display';
                if (type === 'success') {
                    messageDisplay.classList.add('success');
                } else if (type === 'error') {
                    messageDisplay.classList.add('error');
                }
            }
        }

        function renderPhraseDisplay() {
            if (!currentPuzzle || !phraseDisplay) return;
            phraseDisplay.innerHTML = ''; 

            currentPuzzle.words.forEach((word, index) => {
                const wordDiv = document.createElement('div');
                wordDiv.classList.add('word');

                if (revealedWordsIndices.includes(index)) {
                    wordDiv.textContent = word;
                } else {
                    for (let i = 0; i < word.length; i++) {
                        const letterSpan = document.createElement('span');
                        letterSpan.classList.add('letter-blank');
                        letterSpan.textContent = '_';
                        wordDiv.appendChild(letterSpan);
                    }
                }
                phraseDisplay.appendChild(wordDiv);
                if (index < currentPuzzle.words.length - 1) {
                     const space = document.createTextNode('\u00A0');
                     phraseDisplay.appendChild(space);
                }
            });
        }
        
        function updateHintTimerDisplay(value) {
            if (hintTimerDisplay) hintTimerDisplay.textContent = value;
        }

        // --- Hint Logic Functions (defined before use in fetchNewPuzzle/startGame) ---
        function stopHintTimer() {
            clearInterval(hintIntervalId);
            hintIntervalId = null;
        }
        
        function revealNextWordAsHint() {
            if (!currentPuzzle || unrevealedWordHintIndex >= currentPuzzle.words.length) {
                return; 
            }
    
            let wordToRevealGlobalIndex = -1;
            for(let i=0; i < currentPuzzle.words.length; i++){
                if(!revealedWordsIndices.includes(i)){
                    wordToRevealGlobalIndex = i;
                    break;
                }
            }
            
            if (wordToRevealGlobalIndex !== -1 && !revealedWordsIndices.includes(wordToRevealGlobalIndex)) {
                revealedWordsIndices.push(wordToRevealGlobalIndex);
                // unrevealedWordHintIndex++; // This was tracking which *hint number* it is, not direct word index.
                                          // The loop above now correctly finds the next actual unrevealed word.
                renderPhraseDisplay();
                currentPuzzleBasePoints = Math.max(0, currentPuzzleBasePoints - 10); 
                displayMessage(`Hint: Word revealed! Current puzzle points: ${currentPuzzleBasePoints}`, 'info');
                console.log(`Revealed word index: ${wordToRevealGlobalIndex}`);
            }
    
            // Check if all words are now revealed
            let allWordsRevealed = true;
            for(let i=0; i < currentPuzzle.words.length; i++){
                if(!revealedWordsIndices.includes(i)){
                    allWordsRevealed = false;
                    break;
                }
            }

            if (allWordsRevealed) {
                stopHintTimer();
                updateHintTimerDisplay('All hints given');
            } else {
                 // Reset timer for the next hint if not all revealed
                timeToNextHint = HINT_INTERVAL_SECONDS; 
                updateHintTimerDisplay(timeToNextHint);
            }
        }

        function startHintTimer() {
            stopHintTimer(); 
            
            // Check if all words are already revealed before starting a new timer
            let allWordsEffectivelyRevealed = true;
            if (currentPuzzle && currentPuzzle.words) { // Ensure currentPuzzle and words exist
                for(let i=0; i < currentPuzzle.words.length; i++){
                    if(!revealedWordsIndices.includes(i)){
                        allWordsEffectivelyRevealed = false;
                        break;
                    }
                }
            } else {
                allWordsEffectivelyRevealed = true; // No puzzle or words, so nothing to reveal
            }


            if (isHintPaused || allWordsEffectivelyRevealed) {
                updateHintTimerDisplay(isHintPaused ? 'Paused' : (allWordsEffectivelyRevealed && currentPuzzle ? 'All hints given' : '--'));
                return;
            }
    
            timeToNextHint = HINT_INTERVAL_SECONDS;
            updateHintTimerDisplay(timeToNextHint);
    
            hintIntervalId = setInterval(() => {
                if (isHintPaused) return;
    
                timeToNextHint--;
                updateHintTimerDisplay(timeToNextHint);
    
                if (timeToNextHint <= 0) {
                    revealNextWordAsHint(); 
                }
            }, 1000); 
        }
        
        function togglePauseHints() {
            if (!currentPuzzle) return;
            isHintPaused = !isHintPaused;
            if (pauseResumeHintsButton) {
                pauseResumeHintsButton.textContent = isHintPaused ? 'Resume Hints' : 'Pause Hints';
            }
            if (isHintPaused) {
                 updateHintTimerDisplay('Paused');
            } else {
                // If resuming, ensure the timer logic correctly shows current countdown or starts if needed
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
                     updateHintTimerDisplay(timeToNextHint);
                     // If the timer was running, it will just continue. If it was stopped due to all hints given, it won't restart.
                     // The startHintTimer() function handles not starting if all hints given.
                } else {
                     updateHintTimerDisplay('All hints given');
                }
            }
            displayMessage(isHintPaused ? 'Hints Paused.' : 'Hints Resumed.', 'info');
        }


        // --- Puzzle Fetching & Setup (defined before initializeGame) ---
        function resetForNewPuzzle() {
            revealedWordsIndices = [];
            currentPuzzleBasePoints = 100;
            // unrevealedWordHintIndex = 0; // Re-evaluating how this is used; direct check of revealedWordsIndices is better.
            isHintPaused = false;
            if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = 'Pause Hints';
            if (guessInput) guessInput.value = '';
            if (submitGuessButton) submitGuessButton.disabled = false;
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

                if (currentPuzzle && currentPuzzle.emojis_list && currentPuzzle.phrase && currentPuzzle.words) {
                    resetForNewPuzzle();
                    if (emojiDisplay) emojiDisplay.textContent = currentPuzzle.emojis_list.join(' ');
                    if (categoryText) categoryText.textContent = currentPuzzle.category;
                    renderPhraseDisplay(); // Shows initial blanks
                    startHintTimer(); // Start hints for the new puzzle
                } else {
                    throw new Error("Invalid puzzle data received from server. Missing essential fields.");
                }
            } catch (error) {
                console.error('Full script: Error fetching new puzzle:', error);
                displayMessage(`Error: ${error.message}`, 'error');
                if (emojiDisplay) emojiDisplay.textContent = 'Error';
            }
        }
        
        // --- Guess Handling (defined before initializeGame) ---
        function handleSubmitGuess() {
            if (!currentPuzzle || !guessInput || !submitGuessButton) return;

            const userGuess = guessInput.value.trim().toLowerCase();
            const solutionPhrase = currentPuzzle.phrase.trim().toLowerCase();

            if (userGuess === '') {
                displayMessage('Please enter a guess.', 'error');
                return;
            }

            if (userGuess === solutionPhrase) {
                stopHintTimer();
                currentTotalScore += currentPuzzleBasePoints;
                
                let allWordsWereManuallyGuessed = true;
                for(let i=0; i < currentPuzzle.words.length; i++){
                    if(revealedWordsIndices.includes(i)){ // If any word was revealed as a hint
                        allWordsWereManuallyGuessed = false;
                        break;
                    }
                }

                if (allWordsWereManuallyGuessed) { // Check if any hints were used (i.e., words revealed)
                    currentTotalScore += 50; 
                    displayMessage(`Correct! +${currentPuzzleBasePoints} points +50 bonus! Solution: ${currentPuzzle.phrase}`, 'success');
                } else {
                    displayMessage(`Correct! +${currentPuzzleBasePoints} points. Solution: ${currentPuzzle.phrase}`, 'success');
                }
                updateScoreDisplay();
                submitGuessButton.disabled = true; 
                revealedWordsIndices = currentPuzzle.words.map((_, i) => i); 
                renderPhraseDisplay();
            } else {
                displayMessage('Incorrect. Try again!', 'error');
            }
            guessInput.value = ''; 
        }


        // --- Initialization (now defined after its dependencies) ---
        function initializeGame() {
            console.log("Full script: Initializing new game...");
            updateScoreDisplay(); // Defined above
            fetchNewPuzzle();     // Defined above
            if (guessInput) guessInput.value = '';
            if (submitGuessButton) submitGuessButton.disabled = false;
        }

        // --- Event Listeners ---
        console.log("Full script: Setting up event listeners...");
        if (newPuzzleButton) {
            newPuzzleButton.addEventListener('click', fetchNewPuzzle); // fetchNewPuzzle directly
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
            // ... (error display div styling from before) ...
             errorDiv.style.color = 'red';
            errorDiv.style.backgroundColor = 'white';
            errorDiv.style.padding = '20px';
            errorDiv.style.border = '2px solid red';
            errorDiv.style.position = 'fixed';
            errorDiv.style.top = '10px';
            errorDiv.style.left = '10px';
            errorDiv.style.zIndex = '9999';
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