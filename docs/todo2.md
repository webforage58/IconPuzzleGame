# TODO2.md - Major Gameplay Update: Step-Based Progression System

## Overview
Transform the current time-based puzzle game into a user-controlled, step-by-step progression system with visual timeline, step-based scoring, and enhanced user experience.

## 1. Backend Changes

### 1.1. Update Game State Management
- [ ] **Add new game state variables to track progression:**
  ```javascript
  let currentStep = 1; // Steps 1-8
  let maxAvailablePoints = 100; // Decreases with each step
  let gamePhase = 'playing'; // 'playing', 'completed', 'abandoned'
  let stepsCompleted = []; // Array to track which steps are done
  ```

- [ ] **Create step configuration object:**
  ```javascript
  const GAME_STEPS = {
    1: { name: 'New Puzzle', points: 100, type: 'start' },
    2: { name: '1st Letter Hint', points: 90, type: 'letter' },
    3: { name: '2nd Letter Hint', points: 80, type: 'letter' },
    4: { name: '3rd Letter Hint', points: 70, type: 'letter' },
    5: { name: '1st Word Hint', points: 60, type: 'word' },
    6: { name: '2nd Word Hint', points: 50, type: 'word' },
    7: { name: '3rd Word Hint', points: 40, type: 'word' },
    8: { name: 'Reveal Answer', points: 0, type: 'reveal' }
  };
  ```

### 1.2. Modify Scoring System
- [ ] **Remove time-based scoring logic**
- [ ] **Implement step-based scoring:**
  - Points awarded = current step's available points
  - No time bonuses or penalties
  - 0 points if answer is revealed (step 8)

### 1.3. Update Logging System
- [ ] **Add step tracking to CSV logging:**
  - Add `stepSolved` column (1-8, or 0 if abandoned)
  - Add `stepsUsed` column (how many hints were revealed)

## 2. Frontend UI Changes

### 2.1. Create Progress Timeline Component
- [ ] **Add progress timeline HTML structure:**
  ```html
  <div class="progress-timeline">
    <div class="step" data-step="1">New Puzzle</div>
    <div class="step" data-step="2">1st Letter</div>
    <div class="step" data-step="3">2nd Letter</div>
    <div class="step" data-step="4">3rd Letter</div>
    <div class="step" data-step="5">1st Word</div>
    <div class="step" data-step="6">2nd Word</div>
    <div class="step" data-step="7">3rd Word</div>
    <div class="step" data-step="8">Answer</div>
  </div>
  ```

- [ ] **Add CSS for progress timeline:**
  ```css
  .progress-timeline {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    padding: 10px;
    background: linear-gradient(to right, #e0e0e0, #f5f5f5);
    border-radius: 8px;
  }
  
  .step {
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    transition: all 0.3s ease;
  }
  
  .step.completed { background-color: #4CAF50; color: white; }
  .step.current { background-color: #2196F3; color: white; }
  .step.upcoming { background-color: #e0e0e0; color: #666; }
  ```

### 2.2. Create Step Status Panel
- [ ] **Add step status display:**
  ```html
  <div class="step-status-panel">
    <div class="current-step">
      <strong>Current:</strong> <span id="current-step-name">New Puzzle</span>
    </div>
    <div class="next-step">
      <strong>Next:</strong> <span id="next-step-name">1st Letter Hint</span>
    </div>
    <div class="points-available">
      <strong>Points Available:</strong> <span id="points-available">100</span>
    </div>
  </div>
  ```

- [ ] **Add dynamic background colors for game state:**
  ```css
  .step-status-panel.playing { background-color: #e3f2fd; }
  .step-status-panel.completed { background-color: #e8f5e8; }
  .step-status-panel.abandoned { background-color: #ffebee; }
  ```

### 2.3. Update Button Layout
- [ ] **Replace old hint controls with new progression buttons:**
  ```html
  <div class="progression-controls">
    <button id="next-hint-button" class="primary-button">Next Hint</button>
    <button id="skip-to-answer-button" class="secondary-button">Skip to Answer</button>
    <button id="pause-resume-button" class="tertiary-button">Pause Game</button>
  </div>
  ```

- [ ] **Style new buttons:**
  ```css
  .progression-controls {
    display: flex;
    gap: 10px;
    margin: 20px 0;
    justify-content: center;
  }
  
  .primary-button { background-color: #2196F3; }
  .secondary-button { background-color: #FF9800; }
  .tertiary-button { background-color: #9E9E9E; }
  ```

## 3. Game Logic Updates

### 3.1. Implement Step Progression Functions
- [ ] **Create core progression functions:**
  ```javascript
  function advanceToNextStep() {
    if (currentStep < 8) {
      currentStep++;
      executeCurrentStep();
      updateUI();
    }
  }
  
  function executeCurrentStep() {
    switch(currentStep) {
      case 2: case 3: case 4: // Letter hints
        revealNextLetter();
        break;
      case 5: case 6: case 7: // Word hints
        revealNextWord();
        break;
      case 8: // Reveal answer
        revealFullAnswer();
        break;
    }
  }
  ```

### 3.2. Update Hint Revelation Logic
- [ ] **Modify letter hint system:**
  - Remove automatic timing
  - Trigger only on user action
  - Ensure proper step tracking

- [ ] **Modify word hint system:**
  - Remove automatic timing
  - Integrate with step progression
  - Handle puzzles with fewer than 3 words

### 3.3. Implement Pause/Resume Functionality
- [ ] **Add game pause state:**
  ```javascript
  let gamePaused = false;
  
  function togglePauseGame() {
    gamePaused = !gamePaused;
    updatePauseUI();
    // Disable/enable progression buttons
  }
  ```

### 3.4. Add Skip to Answer Functionality
- [ ] **Implement skip mechanism:**
  ```javascript
  function skipToAnswer() {
    currentStep = 8;
    maxAvailablePoints = 0;
    revealFullAnswer();
    gamePhase = 'completed';
    updateUI();
  }
  ```

## 4. Animation and Visual Feedback

### 4.1. Implement Hint Reveal Animations
- [ ] **Add CSS animations for letter reveals:**
  ```css
  .letter-revealed {
    animation: letterPop 0.5s ease-out;
  }
  
  @keyframes letterPop {
    0% { transform: scale(1); background-color: transparent; }
    50% { transform: scale(1.2); background-color: #ffeb3b; }
    100% { transform: scale(1); background-color: #fff3e0; }
  }
  ```

- [ ] **Add CSS animations for word reveals:**
  ```css
  .word-revealed {
    animation: wordSlideIn 0.6s ease-out;
  }
  
  @keyframes wordSlideIn {
    0% { opacity: 0; transform: translateY(-10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  ```

### 4.2. Implement Success Celebrations
- [ ] **Add celebration animation for correct guesses:**
  ```css
  .celebration {
    animation: celebrate 1s ease-out;
  }
  
  @keyframes celebrate {
    0% { transform: scale(1); }
    25% { transform: scale(1.05) rotate(1deg); }
    50% { transform: scale(1.1) rotate(-1deg); }
    75% { transform: scale(1.05) rotate(1deg); }
    100% { transform: scale(1) rotate(0deg); }
  }
  ```

### 4.3. Update Progress Timeline Animations
- [ ] **Add smooth transitions for step changes:**
  ```css
  .step {
    transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
  }
  ```

## 5. Updated UI Functions

### 5.1. Create New UI Update Functions
- [ ] **Function to update progress timeline:**
  ```javascript
  function updateProgressTimeline() {
    // Update step classes (completed, current, upcoming)
    // Animate transitions between states
  }
  ```

- [ ] **Function to update step status panel:**
  ```javascript
  function updateStepStatusPanel() {
    // Update current step name
    // Update next step name
    // Update available points
    // Update background color for game state
  }
  ```

- [ ] **Function to update button states:**
  ```javascript
  function updateButtonStates() {
    // Enable/disable Next Hint button based on current step
    // Show/hide Skip to Answer button
    // Update pause/resume button text
  }
  ```

### 5.2. Modify Existing Functions
- [ ] **Update `renderPhraseDisplay()` function:**
  - Remove old hint timing logic
  - Integrate with new step-based reveals
  - Add animation triggers

- [ ] **Update `handleSubmitGuess()` function:**
  - Use step-based scoring
  - Track which step puzzle was solved on
  - Trigger appropriate celebration animations

- [ ] **Update `resetForNewPuzzle()` function:**
  - Reset step counter to 1
  - Reset available points to 100
  - Reset game phase to 'playing'
  - Clear step completion tracking

## 6. Event Listeners and Interactions

### 6.1. Add New Event Listeners
- [ ] **Next Hint button:**
  ```javascript
  nextHintButton.addEventListener('click', advanceToNextStep);
  ```

- [ ] **Skip to Answer button:**
  ```javascript
  skipToAnswerButton.addEventListener('click', skipToAnswer);
  ```

- [ ] **Updated Pause/Resume button:**
  ```javascript
  pauseResumeButton.addEventListener('click', togglePauseGame);
  ```

### 6.2. Remove Old Event Listeners
- [ ] **Remove automatic timing event listeners**
- [ ] **Remove old letter hint button logic**
- [ ] **Clean up time-based hint system**

## 7. Mobile Responsiveness Updates

### 7.1. Update Mobile CSS
- [ ] **Responsive progress timeline:**
  ```css
  @media (max-width: 768px) {
    .progress-timeline {
      flex-wrap: wrap;
      gap: 5px;
    }
    
    .step {
      flex: 1 1 45%;
      font-size: 10px;
    }
  }
  ```

- [ ] **Mobile-friendly button layout:**
  ```css
  @media (max-width: 768px) {
    .progression-controls {
      flex-direction: column;
      gap: 15px;
    }
    
    .progression-controls button {
      width: 100%;
      padding: 15px;
    }
  }
  ```

## 8. Testing and Validation

### 8.1. Functionality Testing
- [ ] **Test step progression:**
  - Verify each step advances correctly
  - Test with puzzles of different word counts
  - Ensure proper point calculation at each step

- [ ] **Test user interactions:**
  - Next Hint button functionality
  - Skip to Answer functionality
  - Pause/Resume functionality
  - Guess submission at different steps

### 8.2. UI/UX Testing
- [ ] **Test progress timeline:**
  - Verify visual states (completed, current, upcoming)
  - Test animations and transitions
  - Ensure mobile responsiveness

- [ ] **Test step status panel:**
  - Verify information accuracy
  - Test background color changes
  - Ensure readability at all states

### 8.3. Cross-browser Testing
- [ ] **Test on Safari (primary target)**
- [ ] **Test on Chrome**
- [ ] **Test on Firefox**
- [ ] **Test mobile Safari on iOS**

## 9. Final Integration and Polish

### 9.1. Code Cleanup
- [ ] **Remove deprecated time-based code**
- [ ] **Consolidate CSS files**
- [ ] **Add comprehensive comments**
- [ ] **Optimize JavaScript performance**

### 9.2. Documentation Updates
- [ ] **Update README.md with new gameplay description**
- [ ] **Document new game mechanics**
- [ ] **Update API documentation if needed**

### 9.3. Analytics Updates
- [ ] **Update logging to capture new metrics:**
  - Step where puzzle was solved
  - Number of hints used before solving
  - Skip-to-answer usage
  - Pause/resume patterns

---

## Priority Order
1. **Backend Changes (1.1, 1.2)** - Core game state management
2. **UI Structure (2.1, 2.2, 2.3)** - Visual framework
3. **Game Logic (3.1, 3.2)** - Step progression mechanics
4. **Event Listeners (6.1, 6.2)** - User interactions
5. **Animations (4.1, 4.2)** - Visual polish
6. **Testing (8.1, 8.2)** - Validation
7. **Mobile/Polish (7.1, 9.1)** - Final optimization

Estimated total development time: 2-3 days for core functionality, 1-2 additional days for polish and testing.