# src/app.py

from flask import Flask, jsonify, render_template, send_from_directory, request # Added request
# Make sure your generator and connector classes are in the src directory
from model_connector import ModelConnector
from generator import PuzzleGenerator # This now has the new methods

app = Flask(__name__, template_folder='../templates', static_folder='../static')

try:
    # Initialize with the model you confirmed is available
    puzzle_gen_instance = PuzzleGenerator(model_name="gemma3:27b") #
    print("PuzzleGenerator instance created.") #
    # Initial check to see if Ollama is responsive through the connector
    if hasattr(puzzle_gen_instance, 'connector') and puzzle_gen_instance.connector: #
        models = puzzle_gen_instance.connector.refresh_models() # Refresh models on startup #
        if models and puzzle_gen_instance.model_name in models: #
            print(f"Confirmed model '{puzzle_gen_instance.model_name}' is available in Ollama: {models}") #
        elif models: #
            print(f"Warning: Model '{puzzle_gen_instance.model_name}' not in Ollama models: {models}. Puzzle generation may fail.") #
        else:
            print("Warning: Could not fetch model list from Ollama. Ensure Ollama is running.") #
except Exception as e:
    print(f"CRITICAL: Failed to initialize PuzzleGenerator: {e}") #
    puzzle_gen_instance = None #

@app.route('/api/generate-puzzle', methods=['GET']) #
def generate_puzzle_api():
    print("API: Received request for a new puzzle at /api/generate-puzzle") #
    if not puzzle_gen_instance: #
        print("API Error: PuzzleGenerator instance is not available.") #
        return jsonify({'error': 'Puzzle generator not initialized or failed to initialize.'}), 500 #

    try:
        # Use the new method that returns a dictionary of details
        puzzle_details = puzzle_gen_instance.generate_parsed_puzzle_details() #

        if puzzle_details and isinstance(puzzle_details, dict) and 'emojis_list' in puzzle_details: #
            print(f"API: Successfully generated puzzle details: {puzzle_details}") #
            # Send the whole dictionary to the frontend
            return jsonify(puzzle_details) #
        else:
            error_message = "API Error: Failed to generate valid puzzle details from PuzzleGenerator." #
            if puzzle_details and 'error' in puzzle_details: # If generator itself returned an error structure #
                 error_message = puzzle_details['error'] #
            print(error_message) #
            return jsonify({'error': error_message}), 500 #
    except Exception as e:
        # Catch any unexpected errors during the puzzle generation call
        print(f"API Exception: An unexpected error occurred during puzzle generation: {e}") #
        return jsonify({'error': f'An unexpected server error occurred: {str(e)}'}), 500 #

# --- NEW API ENDPOINT FOR LOGGING PUZZLE RESULTS ---
@app.route('/api/log-puzzle-result', methods=['POST'])
def log_puzzle_result_api():
    print("API: Received request to log puzzle result at /api/log-puzzle-result")
    if not puzzle_gen_instance:
        print("API Error: PuzzleGenerator instance is not available for logging.")
        return jsonify({'status': 'error', 'message': 'Puzzle generator not initialized.'}), 500

    try:
        data = request.get_json()
        if not data:
            print("API Error: No JSON data received for logging.")
            return jsonify({'status': 'error', 'message': 'No data received.'}), 400

        # Extract data from the frontend payload
        # Ensure these keys match what your frontend will send
        category = data.get('category')
        phrase = data.get('phrase')
        emojis_list = data.get('emojis_list') # Frontend sends a list of emojis
        solved_correctly = data.get('solvedCorrectly') # e.g., "yes" or "no"
        letter_hints_used = data.get('letterHintsUsed') # e.g., 0, 1, 2, 3
        puzzle_score = data.get('puzzleScore') # Score for this specific puzzle
        total_score_at_end = data.get('totalScoreAtEnd') # Total score after this puzzle

        # Validate required fields
        required_fields = {
            'category': category, 'phrase': phrase, 'emojis_list': emojis_list,
            'solvedCorrectly': solved_correctly, 'letterHintsUsed': letter_hints_used,
            'puzzleScore': puzzle_score, 'totalScoreAtEnd': total_score_at_end
        }
        missing_fields = [key for key, value in required_fields.items() if value is None]
        if missing_fields:
            print(f"API Error: Missing fields in log data: {', '.join(missing_fields)}")
            return jsonify({'status': 'error', 'message': f'Missing data: {", ".join(missing_fields)}'}), 400

        # Convert emojis_list to emojis_string for the logger
        emojis_string = " ".join(emojis_list)

        # Call the logging method in PuzzleGenerator
        puzzle_gen_instance._log_puzzle_to_csv(
            category=category,
            phrase=phrase,
            emojis_string=emojis_string,
            solved_correctly=str(solved_correctly), # Ensure it's a string for CSV consistency
            letter_hints_used=int(letter_hints_used), # Ensure it's an int
            puzzle_score=float(puzzle_score), # Ensure it's a number
            total_score_at_end=float(total_score_at_end) # Ensure it's a number
        )
        
        print(f"API: Successfully logged puzzle result: Category='{category}', Phrase='{phrase}'")
        return jsonify({'status': 'success', 'message': 'Puzzle result logged successfully.'}), 200

    except TypeError as te: # Catch errors if fields are not convertible (e.g. letterHintsUsed to int)
        print(f"API Error: Type error in data provided for logging: {te}")
        return jsonify({'status': 'error', 'message': f'Invalid data type provided: {str(te)}'}), 400
    except Exception as e:
        print(f"API Exception: An unexpected error occurred during logging: {e}")
        return jsonify({'status': 'error', 'message': f'An unexpected server error occurred during logging: {str(e)}'}), 500
# --- END NEW API ENDPOINT ---

@app.route('/', methods=['GET']) #
def index():
    print("Serving index.html") #
    return render_template('index.html') #

# Route to serve manifest.json for PWA
@app.route('/manifest.json') #
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json') #

# Route to serve service worker if you add one later
@app.route('/service-worker.js') #
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js') #

if __name__ == '__main__': #
    print("Starting Flask development server for ConcentrationGameWeb...") #
    app.run(debug=True, host='0.0.0.0', port=5006) # Using port 5006 #