// static/js/script.js
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
        const letterHintButton = document.getElementById('letter-hint-button');
        const letterHintsUsedDisplay = document.getElementById('letter-hints-used-display');

        // --- Game State Variables ---
        let currentPuzzle = null;
        let revealedWordsIndices = [];
        let currentTotalScore = 0;
        let currentPuzzleBasePoints = 100;
        let hintTimeoutId = null;
        const HINT_INTERVAL_SECONDS = 15;
        let timeToNextHintTick = HINT_INTERVAL_SECONDS;
        let isHintPaused = false;
        let revealedLetterPositions = [];
        let letterHintsUsed = 0;
        const MAX_LETTER_HINTS = 3;
        const LETTER_HINT_COST = 5;

        let isCurrentPuzzleLogged = false; // NEW: Flag to track if current puzzle result is logged

        // --- Helper Function to Log Puzzle Result to Server ---
        async function logPuzzleResultToServer(logData) {
            if (!logData || !logData.phrase) { // Basic check
                console.warn("logPuzzleResultToServer: Attempted to log empty or invalid data.", logData);
                return;
            }
            console.log("Logging puzzle result to server:", logData);
            try {
                const response = await fetch('/api/log-puzzle-result', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(logData),
                });
                const responseData = await response.json();
                if (response.ok) {
                    console.log('Puzzle result logged successfully:', responseData);
                } else {
                    console.error('Error logging puzzle result:', responseData);
                }
            } catch (error) {
                console.error('Fetch error while logging puzzle result:', error);
            }
        }

        // --- CORE UI Update Functions ---
        function updateScoreDisplay() {
            if (scoreDisplay) scoreDisplay.textContent = currentTotalScore;
        }

        function displayMessage(text, type = 'info') {
            if (messageDisplay) {
                messageDisplay.textContent = text;
                messageDisplay.className = 'message-display';
                if (type === 'success') messageDisplay.classList.add('success');
                else if (type === 'error') messageDisplay.classList.add('error');
            }
        }

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
                    wordDiv.textContent = word;
                } else {
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
        
        function updateHintTimerDisplay(value) {
            if (hintTimerDisplay) hintTimerDisplay.textContent = value;
        }

        // --- Letter Hint Functions ---
        function updateLetterHintDisplay() {
            if (letterHintsUsedDisplay) letterHintsUsedDisplay.textContent = letterHintsUsed;
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
                        if (!revealedLetterPositions.some(pos => pos.wordIndex === wordIndex && pos.letterIndex === letterIndex)) {
                            availablePositions.push({ wordIndex, letterIndex });
                        }
                    }
                }
            });
            return availablePositions;
        }

        function revealRandomLetter() {
            if (letterHintsUsed >= MAX_LETTER_HINTS || currentTotalScore < LETTER_HINT_COST || !currentPuzzle) {
                updateLetterHintDisplay(); // Ensure button state is accurate
                return;
            }
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

        // --- Hint Logic Functions ---
        function stopHintTimer() {
            clearTimeout(hintTimeoutId);
            hintTimeoutId = null;
        }
        
        function revealNextWordAsHint() {
            if (!currentPuzzle || !currentPuzzle.words) return;
            let wordToRevealGlobalIndex = -1;
            for(let i=0; i < currentPuzzle.words.length; i++) {
                if(!revealedWordsIndices.includes(i)) { wordToRevealGlobalIndex = i; break; }
            }
            if (wordToRevealGlobalIndex !== -1) { 
                revealedWordsIndices.push(wordToRevealGlobalIndex);
                renderPhraseDisplay();
                currentPuzzleBasePoints = Math.max(0, currentPuzzleBasePoints - 10); 
                displayMessage(`Hint: Word revealed! Puzzle points now: ${currentPuzzleBasePoints}`, 'info');
            }
            let allWordsNowRevealed = currentPuzzle.words.every((_, i) => revealedWordsIndices.includes(i));
            if (allWordsNowRevealed) {
                updateHintTimerDisplay('All hints given');
                stopHintTimer(); 
            } else {
                timeToNextHintTick = HINT_INTERVAL_SECONDS; 
                updateHintTimerDisplay(timeToNextHintTick);
                if (!isHintPaused) hintTimeoutId = setTimeout(hintTick, 1000); 
            }
        }

        function hintTick() { 
            if (isHintPaused || !currentPuzzle) return;
            timeToNextHintTick--;
            updateHintTimerDisplay(timeToNextHintTick);
            if (timeToNextHintTick <= 0) revealNextWordAsHint(); 
            else hintTimeoutId = setTimeout(hintTick, 1000);
        }

        function startHintTimer() {
            stopHintTimer(); 
            if (!currentPuzzle || !currentPuzzle.words) { updateHintTimerDisplay('--'); return; }
            let allWordsEffectivelyRevealed = currentPuzzle.words.every((_, i) => revealedWordsIndices.includes(i));
            if (isHintPaused || allWordsEffectivelyRevealed) {
                updateHintTimerDisplay(isHintPaused ? 'Paused' : (allWordsEffectivelyRevealed ? 'All hints given' : '--'));
                return;
            }
            timeToNextHintTick = HINT_INTERVAL_SECONDS;
            updateHintTimerDisplay(timeToNextHintTick);
            hintTimeoutId = setTimeout(hintTick, 1000); 
        }
        
        function togglePauseHints() {
            if (!currentPuzzle) return;
            isHintPaused = !isHintPaused;
            if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = isHintPaused ? 'Resume Game' : 'Pause Game';
            if (isHintPaused) {
                clearTimeout(hintTimeoutId); 
                updateHintTimerDisplay('Paused');
                displayMessage('Hints Paused.', 'info');
            } else {
                displayMessage('Hints Resumed.', 'info');
                let allWordsCurrentlyRevealed = currentPuzzle.words.every((_, i) => revealedWordsIndices.includes(i));
                if (!allWordsCurrentlyRevealed) {
                     updateHintTimerDisplay(timeToNextHintTick);
                     hintTimeoutId = setTimeout(hintTick, 1000); 
                } else updateHintTimerDisplay('All hints given');
            }
        }

        // --- Puzzle Fetching & Setup ---
        function resetForNewPuzzle() {
            revealedWordsIndices = [];
            revealedLetterPositions = [];
            letterHintsUsed = 0;
            currentPuzzleBasePoints = 100;
            isHintPaused = false;
            if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = 'Pause Game';
            if (guessInput) guessInput.value = '';
            if (submitGuessButton) submitGuessButton.disabled = false;
            timeToNextHintTick = HINT_INTERVAL_SECONDS; 
            updateHintTimerDisplay(timeToNextHintTick);
            updateLetterHintDisplay();
            displayMessage('');
            isCurrentPuzzleLogged = false; // NEW: Reset logged flag for the new puzzle
        }

        async function fetchNewPuzzle() {
            // --- Log previous puzzle if abandoned and not yet logged ---
            if (currentPuzzle && !isCurrentPuzzleLogged) {
                const abandonedPuzzleData = {
                    category: currentPuzzle.category,
                    phrase: currentPuzzle.phrase,
                    emojis_list: currentPuzzle.emojis_list,
                    solvedCorrectly: "no", // Puzzle is abandoned
                    letterHintsUsed: letterHintsUsed,
                    puzzleScore: 0, // No score for abandoned puzzle
                    totalScoreAtEnd: currentTotalScore // Score at the moment of abandonment
                };
                await logPuzzleResultToServer(abandonedPuzzleData); // Use await if you want to ensure it sends before proceeding
                isCurrentPuzzleLogged = true; // Mark as logged
            }
            // --- End logging abandoned puzzle ---
            
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

                if (currentPuzzle && currentPuzzle.emojis_list && currentPuzzle.phrase && currentPuzzle.words && Array.isArray(currentPuzzle.words)) {
                    resetForNewPuzzle(); // This will set isCurrentPuzzleLogged to false
                    if (emojiDisplay) emojiDisplay.textContent = currentPuzzle.emojis_list.join(' ');
                    if (categoryText) categoryText.textContent = currentPuzzle.category;
                    renderPhraseDisplay();
                    startHintTimer(); 
                } else {
                    throw new Error("Invalid puzzle data received from server.");
                }
            } catch (error) {
                console.error('Error fetching new puzzle:', error);
                displayMessage(`Error fetching puzzle: ${error.message}`, 'error');
                if (emojiDisplay) emojiDisplay.textContent = 'Error';
                currentPuzzle = null;
            }
        }
        
        // --- Guess Handling ---
        function handleSubmitGuess() {
            if (!currentPuzzle || !guessInput || !submitGuessButton || isCurrentPuzzleLogged) { // Don't process if already logged
                return;
            }

            function normalizeString(str) {
                if (typeof str !== 'string') return '';
                return str.trim().toLowerCase().replace(/\s+/g, ' ').replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?']/g, "");
            }

            const userGuess = normalizeString(guessInput.value);
            const solutionPhrase = normalizeString(currentPuzzle.phrase);

            if (userGuess === '') {
                displayMessage('Please enter a guess.', 'error');
                return;
            }

            let puzzleScoreForLog = 0; // Default score for the puzzle if not solved

            if (userGuess === solutionPhrase) {
                stopHintTimer();
                puzzleScoreForLog = currentPuzzleBasePoints; // Score from puzzle itself
                currentTotalScore += puzzleScoreForLog;
                
                let messageText = `Correct! +${puzzleScoreForLog} points. Solution: ${currentPuzzle.phrase}`;
                if (currentPuzzleBasePoints === 100) { // Assuming 100 is initial max before any word hints
                    currentTotalScore += 50; // Speed bonus
                    messageText = `Correct! +${puzzleScoreForLog} points +50 bonus! Solution: ${currentPuzzle.phrase}`;
                }
                displayMessage(messageText, 'success');
                updateScoreDisplay();
                updateLetterHintDisplay(); 
                if (submitGuessButton) submitGuessButton.disabled = true; 
                revealedWordsIndices = currentPuzzle.words.map((_, i) => i); 
                renderPhraseDisplay();

                // --- Log correct guess ---
                const solvedPuzzleData = {
                    category: currentPuzzle.category,
                    phrase: currentPuzzle.phrase,
                    emojis_list: currentPuzzle.emojis_list,
                    solvedCorrectly: "yes",
                    letterHintsUsed: letterHintsUsed,
                    puzzleScore: puzzleScoreForLog,
                    totalScoreAtEnd: currentTotalScore // Score after this puzzle's points and bonus
                };
                logPuzzleResultToServer(solvedPuzzleData);
                isCurrentPuzzleLogged = true; // Mark as logged
                // --- End logging ---

            } else {
                displayMessage('Incorrect. Try again!', 'error');
                // No logging here, as the puzzle is still active
            }
        }

        // --- Initialization ---
        function initializeGame() {
            currentTotalScore = 25; 
            updateScoreDisplay();
            updateLetterHintDisplay();
            fetchNewPuzzle(); 
            if (guessInput) guessInput.value = '';
        }

        // --- Event Listeners ---
        if (newPuzzleButton) newPuzzleButton.addEventListener('click', fetchNewPuzzle);
        else console.error("New Puzzle button not found!");
        if (submitGuessButton) submitGuessButton.addEventListener('click', handleSubmitGuess);
        else console.error("Submit Guess button not found!");
        if (guessInput) {
            guessInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') handleSubmitGuess();
            });
        } else console.error("Guess Input not found!");
        if (pauseResumeHintsButton) pauseResumeHintsButton.addEventListener('click', togglePauseHints);
        else console.error("Pause/Resume Hints button not found!");
        if (letterHintButton) letterHintButton.addEventListener('click', revealRandomLetter);
        else console.error("Letter Hint button not found!");
        
        initializeGame();

    } catch (e) {
        console.error("CRITICAL SCRIPT ERROR CAUGHT:", e);
        const body = document.querySelector('body');
        if (body) {
            const errorDiv = document.createElement('div');
            // Basic styling for visibility
            errorDiv.style.cssText = 'color:red; background-color:white; padding:20px; border:2px solid red; position:fixed; top:10px; left:10px; z-index:9999;';
            errorDiv.innerHTML = `<h2>JavaScript Error!</h2><p><strong>Type:</strong> ${e.name}</p><p><strong>Message:</strong> ${e.message}</p><pre>${e.stack || 'No stack trace.'}</pre>`;
            body.innerHTML = ''; body.appendChild(errorDiv);
        }
    }
});
console.log('Full script.js parsed (outside DOMContentLoaded)');