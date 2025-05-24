# src/app.py

from flask import Flask, jsonify, render_template
# Make sure your generator and connector classes are in the src directory
from model_connector import ModelConnector
from generator import PuzzleGenerator # This now has the new methods

app = Flask(__name__, template_folder='../templates', static_folder='../static')

try:
    # Initialize with the model you confirmed is available
    puzzle_gen_instance = PuzzleGenerator(model_name="gemma3:4b")
    print("PuzzleGenerator instance created.")
    # Initial check to see if Ollama is responsive through the connector
    if hasattr(puzzle_gen_instance, 'connector') and puzzle_gen_instance.connector:
        models = puzzle_gen_instance.connector.refresh_models() # Refresh models on startup
        if models and puzzle_gen_instance.model_name in models:
            print(f"Confirmed model '{puzzle_gen_instance.model_name}' is available in Ollama: {models}")
        elif models:
            print(f"Warning: Model '{puzzle_gen_instance.model_name}' not in Ollama models: {models}. Puzzle generation may fail.")
        else:
            print("Warning: Could not fetch model list from Ollama. Ensure Ollama is running.")
except Exception as e:
    print(f"CRITICAL: Failed to initialize PuzzleGenerator: {e}")
    puzzle_gen_instance = None

@app.route('/api/generate-puzzle', methods=['GET'])
def generate_puzzle_api():
    print("API: Received request for a new puzzle at /api/generate-puzzle")
    if not puzzle_gen_instance:
        print("API Error: PuzzleGenerator instance is not available.")
        return jsonify({'error': 'Puzzle generator not initialized or failed to initialize.'}), 500

    try:
        # Use the new method that returns a dictionary of details
        puzzle_details = puzzle_gen_instance.generate_parsed_puzzle_details()

        if puzzle_details and isinstance(puzzle_details, dict) and 'emojis_list' in puzzle_details:
            print(f"API: Successfully generated puzzle details: {puzzle_details}")
            # Send the whole dictionary to the frontend
            return jsonify(puzzle_details)
        else:
            error_message = "API Error: Failed to generate valid puzzle details from PuzzleGenerator."
            if puzzle_details and 'error' in puzzle_details: # If generator itself returned an error structure
                 error_message = puzzle_details['error']
            print(error_message)
            return jsonify({'error': error_message}), 500
    except Exception as e:
        # Catch any unexpected errors during the puzzle generation call
        print(f"API Exception: An unexpected error occurred during puzzle generation: {e}")
        return jsonify({'error': f'An unexpected server error occurred: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    print("Serving index.html")
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting Flask development server for ConcentrationGameWeb...")
    app.run(debug=True, host='0.0.0.0', port=5006) # Using port 5006