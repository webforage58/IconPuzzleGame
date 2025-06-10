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
        const explanationDisplay = document.getElementById('explanation-display'); // NEW Explanation Element

        // --- Step-Based UI Elements ---
        const nextHintButton = document.getElementById('next-hint-button');
        const skipToAnswerButton = document.getElementById('skip-to-answer-button');
        const pauseResumeButton = document.getElementById('pause-resume-button');
        const currentStepNameDisplay = document.getElementById('current-step-name');
        const nextStepNameDisplay = document.getElementById('next-step-name');
        const pointsAvailableDisplay = document.getElementById('points-available');
        const stepStatusPanel = document.querySelector('.step-status-panel');
        const progressTimeline = document.querySelector('.progress-timeline');
        
        // --- NEW: Final Answer Timer Elements ---
        const finalAnswerTimer = document.getElementById('final-answer-timer');
        const finalTimerDisplay = document.getElementById('final-timer-display');

        // --- Step-Based Game State Variables ---
        let currentStep = 1; // Steps 1-8
        let maxAvailablePoints = 100; // Decreases with each step
        let gamePhase = 'playing'; // 'playing', 'completed', 'abandoned', 'final_answer'
        let stepsCompleted = []; // Array to track which steps are done
        let finalAnswerTimeoutId = null; // Timer for final answer
        let finalAnswerTimeRemaining = 30; // 30 seconds for final answer

        // --- FIXED: Step Configuration Object (changed "New Puzzle" to "Start") ---
        const GAME_STEPS = {
            1: { name: 'Start', points: 100, type: 'start' },
            2: { name: '1st Letter Hint', points: 90, type: 'letter' },
            3: { name: '2nd Letter Hint', points: 80, type: 'letter' },
            4: { name: '3rd Letter Hint', points: 70, type: 'letter' },
            5: { name: '1st Word Hint', points: 60, type: 'word' },
            6: { name: '2nd Word Hint', points: 50, type: 'word' },
            7: { name: '3rd Word Hint', points: 40, type: 'word' },
            8: { name: 'Reveal Answer', points: 0, type: 'reveal' }
        };

        // --- Original Game State Variables ---
        let currentPuzzle = null;
        let revealedWordsIndices = [];
        let currentTotalScore = 0;
        let currentPuzzleBasePoints = 100;
        let hintTimeoutId = null;
        const HINT_INTERVAL_SECONDS = 30;
        let timeToNextHintTick = HINT_INTERVAL_SECONDS;
        let isHintPaused = false;
        let revealedLetterPositions = [];
        let letterHintsUsed = 0;
        const MAX_LETTER_HINTS = 3;
        const LETTER_HINT_COST = 5;

        let isCurrentPuzzleLogged = false; // Flag to track if current puzzle result is logged
        
        // --- UPDATED: Function to display the puzzle explanation ---
        function displayExplanation() {
            if (explanationDisplay && currentPuzzle && currentPuzzle.explanation) {
                explanationDisplay.innerHTML = `<strong>Explanation:</strong> ${currentPuzzle.explanation}`;
                explanationDisplay.style.display = 'block';
                // NEW: Scroll the explanation into view smoothly
                explanationDisplay.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

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

        // --- NEW: Final Answer Timer Functions ---
        function startFinalAnswerTimer() {
            if (finalAnswerTimeoutId) {
                clearTimeout(finalAnswerTimeoutId);
            }
            
            gamePhase = 'final_answer';
            finalAnswerTimeRemaining = 10; // 10 seconds for final answer
            
            if (finalAnswerTimer) {
                finalAnswerTimer.style.display = 'block';
            }
            
            updateFinalTimerDisplay();
            updateAllUI();
            
            displayMessage('Final answer required! You have 10 seconds to submit your guess.', 'error');
            
            finalAnswerTimeoutId = setTimeout(finalAnswerTick, 1000);
        }
        
        function finalAnswerTick() {
            finalAnswerTimeRemaining--;
            updateFinalTimerDisplay();
            
            if (finalAnswerTimeRemaining <= 0) {
                handleFinalAnswerTimeout();
            } else {
                finalAnswerTimeoutId = setTimeout(finalAnswerTick, 1000);
            }
        }
        
        function updateFinalTimerDisplay() {
            if (finalTimerDisplay) {
                finalTimerDisplay.textContent = finalAnswerTimeRemaining;
            }
        }
        
        function stopFinalAnswerTimer() {
            if (finalAnswerTimeoutId) {
                clearTimeout(finalAnswerTimeoutId);
                finalAnswerTimeoutId = null;
            }
            
            if (finalAnswerTimer) {
                finalAnswerTimer.style.display = 'none';
            }
        }
        
        function handleFinalAnswerTimeout() {
            stopFinalAnswerTimer();
            handlePuzzleLoss('Time ran out! No final answer submitted.');
        }

        // --- NEW: Game Loss Handler ---
        function handlePuzzleLoss(lossMessage) {
            gamePhase = 'abandoned';
            maxAvailablePoints = 0;
            
            if (submitGuessButton) submitGuessButton.disabled = true;
            
            // Reveal the answer
            revealedWordsIndices = currentPuzzle.words.map((_, i) => i);
            renderPhraseDisplay();
            
            displayMessage(`${lossMessage} Answer: ${currentPuzzle.phrase}`, 'error');
            displayExplanation(); // NEW: Show explanation on loss
            updateAllUI();
            
            // Log the loss
            if (currentPuzzle && !isCurrentPuzzleLogged) {
                const lostPuzzleData = {
                    category: currentPuzzle.category,
                    phrase: currentPuzzle.phrase,
                    emojis_list: currentPuzzle.emojis_list,
                    solvedCorrectly: "no",
                    letterHintsUsed: letterHintsUsed,
                    puzzleScore: 0,
                    totalScoreAtEnd: currentTotalScore
                };
                logPuzzleResultToServer(lostPuzzleData);
                isCurrentPuzzleLogged = true;
            }
        }

        // --- NEW: Helper Functions for Game Logic ---
        function getUnrevealedWordCount() {
            if (!currentPuzzle || !currentPuzzle.words) return 0;
            
            return currentPuzzle.words.filter((_, index) => 
                !revealedWordsIndices.includes(index)
            ).length;
        }

        function areAllWordsRevealed() {
            if (!currentPuzzle || !currentPuzzle.words) return false;
            return revealedWordsIndices.length === currentPuzzle.words.length;
        }

        function shouldTriggerFinalAnswer(nextStepType) {
            if (nextStepType !== 'word') return false;
            
            const unrevealedWords = getUnrevealedWordCount();
            return unrevealedWords === 1; // Only one word left unrevealed
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
                // DELETED: The conflicting code that added a space was removed from here.
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

        // --- Original Hint Logic Functions (for backward compatibility) ---
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
                
                // NEW: Check if all words are now revealed
                if (areAllWordsRevealed()) {
                    // All words revealed - game should end
                    gamePhase = 'abandoned';
                    maxAvailablePoints = 0;
                    updateHintTimerDisplay('All words revealed');
                    stopHintTimer();
                    displayMessage(`All words revealed! Puzzle completed with 0 points. Answer: ${currentPuzzle.phrase}`, 'error');
                    displayExplanation(); // NEW: Show explanation
                    updateAllUI();
                    
                    // Log the result
                    if (currentPuzzle && !isCurrentPuzzleLogged) {
                        const allWordsRevealedData = {
                            category: currentPuzzle.category,
                            phrase: currentPuzzle.phrase,
                            emojis_list: currentPuzzle.emojis_list,
                            solvedCorrectly: "no",
                            letterHintsUsed: letterHintsUsed,
                            puzzleScore: 0,
                            totalScoreAtEnd: currentTotalScore
                        };
                        logPuzzleResultToServer(allWordsRevealedData);
                        isCurrentPuzzleLogged = true;
                    }
                    return;
                }
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

        // --- Step-Based Functions ---
        function resetStepBasedState() {
            currentStep = 1;
            maxAvailablePoints = 100;
            gamePhase = 'playing';
            stepsCompleted = [];
            stopFinalAnswerTimer();
            console.log('Step-based state reset - Current Step:', currentStep, 'Max Points:', maxAvailablePoints);
        }

        function updateMaxAvailablePoints() {
            if (GAME_STEPS[currentStep]) {
                maxAvailablePoints = GAME_STEPS[currentStep].points;
                console.log(`Step ${currentStep}: ${GAME_STEPS[currentStep].name} - Max Points: ${maxAvailablePoints}`);
            }
        }

        // --- UPDATED: Core Step Progression Functions (with gameplay fix) ---
        function advanceToNextStep() {
            if (currentStep < 8 && gamePhase === 'playing') {
                if (!stepsCompleted.includes(currentStep)) {
                    stepsCompleted.push(currentStep);
                }
                
                const nextStep = currentStep + 1;
                const nextStepInfo = GAME_STEPS[nextStep];
                
                // NEW: Check if next step would trigger final answer state
                if (nextStepInfo && shouldTriggerFinalAnswer(nextStepInfo.type)) {
                    displayMessage('Cannot reveal more words! You must submit your final answer now.', 'error');
                    startFinalAnswerTimer();
                    return;
                }
                
                currentStep++;
                updateMaxAvailablePoints();
                executeCurrentStep();
                updateAllUI();
                console.log(`Advanced to Step ${currentStep}: ${GAME_STEPS[currentStep]?.name}`);
            }
        }

        function executeCurrentStep() {
            if (!currentPuzzle) return;
            
            switch(currentStep) {
                case 2: case 3: case 4: // Letter hints
                    revealNextLetterStep();
                    break;
                case 5: case 6: case 7: // Word hints
                    revealNextWordStep();
                    break;
                case 8: // Reveal answer
                    revealFullAnswer();
                    break;
            }
        }

        function revealNextLetterStep() {
            const availablePositions = getAvailableLetterPositions();
            if (availablePositions.length === 0) {
                displayMessage('No more letters to reveal!', 'info');
                return;
            }
            const randomPosition = availablePositions[Math.floor(Math.random() * availablePositions.length)];
            revealedLetterPositions.push(randomPosition);
            renderPhraseDisplay();
            const word = currentPuzzle.words[randomPosition.wordIndex];
            const letter = word[randomPosition.letterIndex];
            displayMessage(`Letter hint: "${letter}" revealed!`, 'info');
        }

        function revealNextWordStep() {
            let wordToRevealIndex = -1;
            for(let i = 0; i < currentPuzzle.words.length; i++) {
                if(!revealedWordsIndices.includes(i)) { 
                    wordToRevealIndex = i; 
                    break; 
                }
            }
            if (wordToRevealIndex !== -1) { 
                revealedWordsIndices.push(wordToRevealIndex);
                renderPhraseDisplay();
                displayMessage(`Word hint: "${currentPuzzle.words[wordToRevealIndex]}" revealed!`, 'info');
                
                // NEW: Check if all words are now revealed
                if (areAllWordsRevealed()) {
                    // All words revealed - game should end, player gets 0 points
                    gamePhase = 'abandoned';
                    maxAvailablePoints = 0;
                    displayMessage(`All words revealed! Puzzle completed with 0 points. Answer: ${currentPuzzle.phrase}`, 'error');
                    displayExplanation(); // NEW: Show explanation
                    updateAllUI();
                    
                    // Log the result as completed with 0 points
                    if (currentPuzzle && !isCurrentPuzzleLogged) {
                        const allWordsRevealedData = {
                            category: currentPuzzle.category,
                            phrase: currentPuzzle.phrase,
                            emojis_list: currentPuzzle.emojis_list,
                            solvedCorrectly: "no", // All words revealed = not solved by player
                            letterHintsUsed: letterHintsUsed,
                            puzzleScore: 0,
                            totalScoreAtEnd: currentTotalScore
                        };
                        logPuzzleResultToServer(allWordsRevealedData);
                        isCurrentPuzzleLogged = true;
                    }
                }
            }
        }

        function revealFullAnswer() {
            stopFinalAnswerTimer();
            revealedWordsIndices = currentPuzzle.words.map((_, i) => i);
            renderPhraseDisplay();
            gamePhase = 'completed';
            maxAvailablePoints = 0;
            displayMessage(`Answer revealed: ${currentPuzzle.phrase}`, 'info');
            displayExplanation(); // NEW: Show explanation on reveal
            if (submitGuessButton) submitGuessButton.disabled = true;
            updateAllUI();
        }

        function skipToAnswer() {
            if (!currentPuzzle || (gamePhase !== 'playing' && gamePhase !== 'final_answer')) return;
            currentStep = 8;
            maxAvailablePoints = 0;
            gamePhase = 'abandoned';
            revealFullAnswer();
            console.log('Skipped to answer - puzzle abandoned');
        }

        function togglePauseGame() {
            if (!currentPuzzle) return;
            
            // Don't allow pausing during final answer timer
            if (gamePhase === 'final_answer') {
                displayMessage('Cannot pause during final answer countdown!', 'error');
                return;
            }
            
            isHintPaused = !isHintPaused;
            updateAllUI();
            displayMessage(isHintPaused ? 'Game Paused' : 'Game Resumed', 'info');
        }

        // --- UI Update Functions ---
        function updateProgressTimeline() {
            if (!progressTimeline) return;
            const steps = progressTimeline.querySelectorAll('.step');
            steps.forEach((stepElement, index) => {
                const stepNumber = index + 1;
                stepElement.className = 'step';
                
                if (stepsCompleted.includes(stepNumber) || (stepNumber < currentStep)) {
                    stepElement.classList.add('completed');
                } else if (stepNumber === currentStep) {
                    stepElement.classList.add('current');
                } else {
                    stepElement.classList.add('upcoming');
                }
            });
        }

        function updateStepStatusPanel() {
            if (!currentStepNameDisplay || !nextStepNameDisplay || !pointsAvailableDisplay || !stepStatusPanel) return;
            
            // Update step names
            currentStepNameDisplay.textContent = GAME_STEPS[currentStep]?.name || 'Unknown';
            
            if (gamePhase === 'final_answer') {
                nextStepNameDisplay.textContent = 'Submit Final Answer!';
            } else {
                const nextStep = currentStep < 8 ? currentStep + 1 : 8;
                nextStepNameDisplay.textContent = currentStep < 8 ? GAME_STEPS[nextStep]?.name || 'Complete' : 'Complete';
            }
            
            // Update points
            pointsAvailableDisplay.textContent = maxAvailablePoints;
            
            // Update background color
            stepStatusPanel.className = 'step-status-panel';
            if (gamePhase === 'playing' || gamePhase === 'final_answer') {
                stepStatusPanel.classList.add('playing');
            } else if (gamePhase === 'completed') {
                stepStatusPanel.classList.add('completed');
            } else if (gamePhase === 'abandoned') {
                stepStatusPanel.classList.add('abandoned');
            }
        }

        function updateButtonStates() {
            if (!nextHintButton || !skipToAnswerButton || !pauseResumeButton) return;
            
            // Next Hint button
            const canAdvance = (currentStep < 8 && gamePhase === 'playing' && !isHintPaused);
            nextHintButton.disabled = !canAdvance || gamePhase === 'final_answer';
            
            if (gamePhase === 'final_answer') {
                nextHintButton.textContent = 'Submit Answer Required!';
            } else if (currentStep >= 8) {
                nextHintButton.textContent = 'Game Complete';
            } else {
                nextHintButton.textContent = 'Next Hint';
            }
            
            // Skip to Answer button
            skipToAnswerButton.disabled = (currentStep >= 8 || (gamePhase !== 'playing' && gamePhase !== 'final_answer'));
            
            // Pause/Resume button
            pauseResumeButton.textContent = isHintPaused ? 'Resume Game' : 'Pause Game';
            pauseResumeButton.disabled = (gamePhase === 'completed' || gamePhase === 'abandoned' || gamePhase === 'final_answer');
            
            // Submit button during final answer and when all words revealed
            if (submitGuessButton) {
                const allWordsRevealed = areAllWordsRevealed();
                
                if (allWordsRevealed) {
                    // All words revealed - disable submit button
                    submitGuessButton.disabled = true;
                    submitGuessButton.style.backgroundColor = '#ccc'; // Gray for disabled
                    submitGuessButton.textContent = 'All Words Revealed';
                } else if (gamePhase === 'final_answer') {
                    // Final answer countdown
                    submitGuessButton.disabled = false;
                    submitGuessButton.style.backgroundColor = '#f44336'; // Red for urgency
                    submitGuessButton.textContent = 'SUBMIT FINAL ANSWER!';
                } else if (gamePhase === 'completed' || gamePhase === 'abandoned') {
                    // Game over
                    submitGuessButton.disabled = true;
                    submitGuessButton.style.backgroundColor = ''; // Reset to default
                    submitGuessButton.textContent = 'Submit Guess';
                } else {
                    // Normal gameplay
                    submitGuessButton.disabled = false;
                    submitGuessButton.style.backgroundColor = ''; // Reset to default
                    submitGuessButton.textContent = 'Submit Guess';
                }
            }
        }

        function updateAllUI() {
            updateProgressTimeline();
            updateStepStatusPanel();
            updateButtonStates();
            updateScoreDisplay();
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
            if (submitGuessButton) {
                submitGuessButton.disabled = false;
                submitGuessButton.style.backgroundColor = ''; // Reset color
                submitGuessButton.textContent = 'Submit Guess'; // Reset text
            }
            timeToNextHintTick = HINT_INTERVAL_SECONDS; 
            updateHintTimerDisplay(timeToNextHintTick);
            updateLetterHintDisplay();
            displayMessage('');
            if (explanationDisplay) { // NEW: Hide and clear explanation
                explanationDisplay.style.display = 'none';
                explanationDisplay.innerHTML = '';
            }
            isCurrentPuzzleLogged = false; // Reset logged flag for the new puzzle
            
            // Reset step-based state and update UI
            resetStepBasedState();
            updateAllUI();
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
                await logPuzzleResultToServer(abandonedPuzzleData);
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
                    resetForNewPuzzle(); // This will set isCurrentPuzzleLogged to false and reset step state
                    if (emojiDisplay) emojiDisplay.textContent = currentPuzzle.emojis_list.join(' ');
                    if (categoryText) categoryText.textContent = currentPuzzle.category;
                    renderPhraseDisplay();
                    // startHintTimer();// disable auto-start for hints on new puzzle
                    
                    // Update all UI elements for new puzzle
                    updateAllUI();
                    console.log(`New puzzle loaded - Step ${currentStep}: ${GAME_STEPS[currentStep].name}`);
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
        
        // --- UPDATED: Guess Handling (with final answer logic and all-words-revealed check) ---
        function handleSubmitGuess() {
            if (!currentPuzzle || !guessInput || !submitGuessButton || isCurrentPuzzleLogged) { 
                return;
            }

            // NEW: Check if all words are already revealed - if so, player cannot submit
            if (areAllWordsRevealed()) {
                displayMessage('Cannot submit answer! All words have been revealed through hints.', 'error');
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
                // Correct answer
                stopHintTimer();
                stopFinalAnswerTimer();
                
                // Use step-based scoring instead of time-based
                puzzleScoreForLog = maxAvailablePoints; // Score from current step
                currentTotalScore += puzzleScoreForLog;
                
                let messageText = `Correct! +${puzzleScoreForLog} points. Solution: ${currentPuzzle.phrase}`;
                if (maxAvailablePoints === 100) { // If solved at step 1 (full points)
                    currentTotalScore += 50; // Speed bonus
                    messageText = `Correct! +${puzzleScoreForLog} points +50 bonus! Solution: ${currentPuzzle.phrase}`;
                }
                displayMessage(messageText, 'success');
                displayExplanation(); // NEW: Show explanation on correct guess
                updateScoreDisplay();
                updateLetterHintDisplay(); 
                if (submitGuessButton) {
                    submitGuessButton.disabled = true;
                    submitGuessButton.style.backgroundColor = ''; // Reset color
                    submitGuessButton.textContent = 'Submit Guess'; // Reset text
                }
                revealedWordsIndices = currentPuzzle.words.map((_, i) => i); 
                renderPhraseDisplay();

                // Update game phase and UI
                gamePhase = 'completed';
                updateAllUI();
                console.log(`Puzzle solved at step ${currentStep} for ${puzzleScoreForLog} points`);

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

            } else {
                // Incorrect answer
                if (gamePhase === 'final_answer') {
                    // Final answer was wrong - player loses
                    stopFinalAnswerTimer();
                    handlePuzzleLoss('Incorrect final answer!');
                } else {
                    displayMessage('Incorrect. Try again!', 'error');
                }
            }
        }

        // --- Initialization ---
        function initializeGame() {
            currentTotalScore = 25; 
            updateScoreDisplay();
            updateLetterHintDisplay();
            
            // Initialize step-based state and UI
            resetStepBasedState();
            updateAllUI();
            
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

        // --- Step-Based Event Listeners ---
        if (nextHintButton) nextHintButton.addEventListener('click', advanceToNextStep);
        else console.error("Next Hint button not found!");
        if (skipToAnswerButton) skipToAnswerButton.addEventListener('click', skipToAnswer);
        else console.error("Skip to Answer button not found!");
        if (pauseResumeButton) pauseResumeButton.addEventListener('click', togglePauseGame);
        else console.error("Pause/Resume button not found!");
        
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