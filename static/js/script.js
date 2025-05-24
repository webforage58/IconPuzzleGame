// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const puzzleDisplay = document.getElementById('puzzle-display');
    const newPuzzleButton = document.getElementById('new-puzzle-button');

    async function fetchAndDisplayPuzzle() {
        if (!puzzleDisplay) {
            console.error("Error: puzzleDisplay element not found in HTML.");
            return;
        }
        puzzleDisplay.textContent = 'Loading puzzle...';

        try {
            const response = await fetch('/api/generate-puzzle');

            if (!response.ok) {
                let errorMsg = `HTTP error! Status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) {
                    errorMsg = response.statusText || errorMsg;
                }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            // *** MODIFIED SECTION START ***
            // Check for the new 'emojis_list' property
            if (data.emojis_list && data.emojis_list.length > 0) {
                puzzleDisplay.textContent = data.emojis_list.join(' ');
                // For debugging, let's also log the other data to the console
                console.log("Received puzzle data:", data);
            } else if (data.error) {
                puzzleDisplay.textContent = `Error: ${data.error}`;
            } else {
                // This case should ideally not be hit if the backend is sending correct data or an error
                puzzleDisplay.textContent = 'No puzzle found or data format incorrect. Try again!';
                console.log("Received unexpected data structure:", data);
            }
            // *** MODIFIED SECTION END ***

        } catch (error) {
            console.error('Error fetching or displaying puzzle:', error);
            puzzleDisplay.textContent = `Error: ${error.message}`;
        }
    }

    if (newPuzzleButton) {
        newPuzzleButton.addEventListener('click', fetchAndDisplayPuzzle);
    } else {
        console.error("Error: New Puzzle button (new-puzzle-button) not found in HTML.");
    }

    fetchAndDisplayPuzzle();
});