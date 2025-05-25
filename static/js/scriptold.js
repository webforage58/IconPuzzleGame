// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
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
    let currentPuzzle = null; // To store { phrase, words, category, emojis_list }
    let revealedWordsIndices = []; // Indices of words from currentPuzzle.words that are revealed
    let currentTotalScore = 0;
    let currentPuzzleBasePoints = 100; // Points for solving this puzzle, decreases with hints
    let hintIntervalId = null; // Stores the ID from setInterval
    const HINT_INTERVAL_SECONDS = 15; // Time between word reveals
    let timeToNextHint = HINT_INTERVAL_SECONDS;
    let isHintPaused = false;
    let unrevealedWordHintIndex = 0; // Index of the next word to be revealed from currentPuzzle.words

    // --- Initialization ---
    function initializeGame() {
        console.log("Initializing new game...");
        updateScoreDisplay();
        fetchNewPuzzle();
        if (guessInput) guessInput.value = '';
        if (submitGuessButton) submitGuessButton.disabled = false;
    }

    // --- UI Update Functions ---
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
        if (!currentPuzzle || !phraseDisplay) return;
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
                    letterSpan.textContent = '_'; // Or use an underscore character
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


    // --- Puzzle Fetching ---
    async function fetchNewPuzzle() {
        console.log("Fetching new puzzle...");
        if (emojiDisplay) emojiDisplay.textContent = 'Loading...';
        if (categoryText) categoryText.textContent = 'Loading...';
        if (phraseDisplay) phraseDisplay.innerHTML = '';
        displayMessage(''); // Clear old messages
        stopHintTimer(); // Stop timer from previous puzzle

        try {
            const response = await fetch('/api/generate-puzzle');
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Network response was not ok." }));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            currentPuzzle = await response.json();
            console.log("Puzzle data received:", currentPuzzle);

            if (currentPuzzle && currentPuzzle.emojis_list && currentPuzzle.phrase) {
                resetForNewPuzzle();
                if (emojiDisplay) emojiDisplay.textContent = currentPuzzle.emojis_list.join(' ');
                if (categoryText) categoryText.textContent = currentPuzzle.category;
                renderPhraseDisplay();
                startHintTimer();
            } else {
                throw new Error("Invalid puzzle data received from server.");
            }
        } catch (error) {
            console.error('Error fetching new puzzle:', error);
            displayMessage(`Error: ${error.message}`, 'error');
            if (emojiDisplay) emojiDisplay.textContent = 'Error';
        }
    }

    function resetForNewPuzzle() {
        revealedWordsIndices = [];
        currentPuzzleBasePoints = 100; // Reset points for this puzzle
        unrevealedWordHintIndex = 0;
        isHintPaused = false;
        if (pauseResumeHintsButton) pauseResumeHintsButton.textContent = 'Pause Hints';
        if (guessInput) guessInput.value = '';
        if (submitGuessButton) submitGuessButton.disabled = false;
        displayMessage('');
    }

    // --- Hint Logic ---
    function startHintTimer() {
        stopHintTimer(); // Clear any existing timer
        if (isHintPaused || unrevealedWordHintIndex >= currentPuzzle.words.length) {
            updateHintTimerDisplay(isHintPaused ? 'Paused' : '--');
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
                // Reset timer or stop if all words revealed
                if (unrevealedWordHintIndex < currentPuzzle.words.length) {
                    timeToNextHint = HINT_INTERVAL_SECONDS;
                    updateHintTimerDisplay(timeToNextHint);
                } else {
                    stopHintTimer();
                    updateHintTimerDisplay('All hints given');
                }
            }
        }, 1000); // Update countdown every second
    }

    function stopHintTimer() {
        clearInterval(hintIntervalId);
        hintIntervalId = null;
    }

    function revealNextWordAsHint() {
        if (!currentPuzzle || unrevealedWordHintIndex >= currentPuzzle.words.length) {
            return; // All words already revealed or no puzzle
        }

        // Find the actual index of the next unrevealed word
        let wordToRevealGlobalIndex = -1;
        for(let i=0; i < currentPuzzle.words.length; i++){
            if(!revealedWordsIndices.includes(i)){
                wordToRevealGlobalIndex = i;
                break;
            }
        }
        
        // Find the next word that hasn't been revealed yet.
        // This is a bit simplified; a better way would be to find the first word index not in revealedWordsIndices.
        // For this implementation, we assume unrevealedWordHintIndex correctly tracks this.
        if (wordToRevealGlobalIndex !== -1 && !revealedWordsIndices.includes(wordToRevealGlobalIndex)) {
            revealedWordsIndices.push(wordToRevealGlobalIndex);
            unrevealedWordHintIndex++; // Increment for the next hint cycle
            renderPhraseDisplay();
            currentPuzzleBasePoints = Math.max(0, currentPuzzleBasePoints - 10); // Deduct points for hint
            displayMessage(`Hint: Word revealed! Current puzzle points: ${currentPuzzleBasePoints}`, 'info');
            console.log(`Revealed word index: ${wordToRevealGlobalIndex}, new hint index: ${unrevealedWordHintIndex}`);
        }


        if (unrevealedWordHintIndex >= currentPuzzle.words.length) {
            stopHintTimer();
            updateHintTimerDisplay('All hints given');
        }
    }


    function updateHintTimerDisplay(value) {
        if (hintTimerDisplay) hintTimerDisplay.textContent = value;
    }

    function togglePauseHints() {
        if (!currentPuzzle) return;
        isHintPaused = !isHintPaused;
        if (pauseResumeHintsButton) {
            pauseResumeHintsButton.textContent = isHintPaused ? 'Resume Hints' : 'Pause Hints';
        }
        if (isHintPaused) {
            // Display 'Paused' but don't clear the interval if we want to resume countdown
             updateHintTimerDisplay('Paused');
        } else {
            // If resuming and timer was active, it will continue.
            // If it had stopped (all hints given), it won't restart here.
            // If no hints started, start it.
            if (unrevealedWordHintIndex < currentPuzzle.words.length) {
                 updateHintTimerDisplay(timeToNextHint); // Show current countdown
                 // The existing interval will pick up if it wasn't cleared, or start if needed.
                 // For simplicity, if paused, the interval continues but the tick function does nothing.
                 // When resumed, the tick function starts decrementing again.
                 // This means the 'timeToNextHint' effectively freezes while paused.
            } else {
                 updateHintTimerDisplay('All hints given');
            }
        }
        displayMessage(isHintPaused ? 'Hints Paused.' : 'Hints Resumed.', 'info');
    }


    // --- Guess Handling ---
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
            // Speed bonus: if no words were revealed by hints (unrevealedWordHintIndex is still 0)
            if (unrevealedWordHintIndex === 0 && revealedWordsIndices.length === 0) {
                currentTotalScore += 50; // Add speed bonus
                displayMessage(`Correct! +${currentPuzzleBasePoints} points +50 bonus! Solution: ${currentPuzzle.phrase}`, 'success');
            } else {
                displayMessage(`Correct! +${currentPuzzleBasePoints} points. Solution: ${currentPuzzle.phrase}`, 'success');
            }
            updateScoreDisplay();
            submitGuessButton.disabled = true; // Prevent further guesses for this puzzle
            revealedWordsIndices = currentPuzzle.words.map((_, i) => i); // Reveal all words
            renderPhraseDisplay();
        } else {
            displayMessage('Incorrect. Try again!', 'error');
            // Optional: Deduct points for wrong guesses, e.g.
            // currentTotalScore = Math.max(0, currentTotalScore - 1);
            // updateScoreDisplay();
        }
        guessInput.value = ''; // Clear input field
    }

    // --- Event Listeners ---
    if (newPuzzleButton) {
        newPuzzleButton.addEventListener('click', fetchNewPuzzle);
    }
    if (submitGuessButton) {
        submitGuessButton.addEventListener('click', handleSubmitGuess);
    }
    if (guessInput) {
        guessInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                handleSubmitGuess();
            }
        });
    }
    if (pauseResumeHintsButton) {
        pauseResumeHintsButton.addEventListener('click', togglePauseHints);
    }

    // --- Start the game ---
    initializeGame();
});