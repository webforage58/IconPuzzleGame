# src/generator.py

from model_connector import ModelConnector # Assuming model_connector.py is in the same directory
import json # For potentially parsing structured LLM output

class PuzzleGenerator:
    def __init__(self, model_name="gemma3:4b"): # Ensure this model is available
        self.connector = ModelConnector()
        self.model_name = model_name

        available_models = self.connector.refresh_models()
        if not available_models:
            print("Warning: No models reported by Ollama. Puzzle generation might fail.")
        elif self.model_name not in available_models:
            print(f"Warning: Model '{self.model_name}' not found in available models: {available_models}.")
            # Suggest other available models or remind to pull the chosen one

    def _create_emoji_puzzle_prompt_v2(self): # Renamed for clarity
        """
        Creates a prompt for the LLM to generate an emoji puzzle with solution, words, and category.
        Asks for JSON output for easier parsing.
        """
        prompt = (
            "Generate a common phrase, idiom, movie title, book title, or well-known saying consisting of 3 to 6 words. "
            "Provide the following information in a VALID JSON format:\n"
            "1. 'phrase': The full solution phrase (string).\n"
            "2. 'words': A list of strings, where each string is a word from the phrase.\n"
            "3. 'category': A short category for the phrase (e.g., 'Idiom', 'Movie Title', 'Proverb') (string).\n"
            "4. 'emojis': A sequence of 3 to 5 emojis that represent the phrase, as a single string with emojis separated by spaces.\n"
            "\n"
            "Example JSON output format:\n"
            "{\n"
            "  \"phrase\": \"Curiosity killed the cat\",\n"
            "  \"words\": [\"Curiosity\", \"killed\", \"the\", \"cat\"],\n"
            "  \"category\": \"Idiom\",\n"
            "  \"emojis\": \"🤔 ➡️ 💀 🐈\"\n"
            "}\n"
            "Ensure the JSON is well-formed. Only return the JSON object."
        )
        return prompt

    def generate_parsed_puzzle_details(self): # Renamed for clarity
        """
        Generates an emoji puzzle with details (phrase, words, category, emojis)
        and parses it from the expected JSON output.

        Returns:
            dict | None: A dictionary with puzzle details if successful, otherwise None.
                         Expected dict keys: 'phrase', 'words', 'category', 'emojis_list'
        """
        if not self.model_name and not self.connector.get_models():
            print("Error: No LLM model is configured or available.")
            return None

        prompt_text = self._create_emoji_puzzle_prompt_v2()
        response_text = self.connector.enhance_prompt(self.model_name, prompt_text, prompt_type="general")

        if response_text and not response_text.startswith("Error:") and not response_text.startswith("No response from model"):
            print(f"Raw LLM response for puzzle details:\n'{response_text}'")
            try:
                # Attempt to clean up the response if it includes markdown/code block indicators
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:] # Remove ```json
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3] # Remove ```
                cleaned_response = cleaned_response.strip()

                puzzle_data = json.loads(cleaned_response)

                # Validate the structure of the parsed JSON
                required_keys = ['phrase', 'words', 'category', 'emojis']
                if not all(key in puzzle_data for key in required_keys):
                    print(f"Error: LLM response JSON is missing one or more required keys. Data: {puzzle_data}")
                    return None
                if not isinstance(puzzle_data['words'], list) or not puzzle_data['words']:
                    print(f"Error: 'words' field is not a non-empty list. Data: {puzzle_data}")
                    return None

                # Parse the emoji string into a list
                emoji_char_list = [emoji for emoji in puzzle_data['emojis'].split(' ') if emoji]
                if not emoji_char_list:
                    print(f"Warning: LLM response had an empty emoji string after parsing: '{puzzle_data['emojis']}'")
                    return None

                # Return a well-structured dictionary
                # Storing emojis as 'emojis_list' to distinguish from the raw string if needed
                parsed_details = {
                    'phrase': puzzle_data['phrase'],
                    'words': puzzle_data['words'],
                    'category': puzzle_data['category'],
                    'emojis_list': emoji_char_list # This will be sent to the frontend
                }
                print(f"Successfully parsed puzzle details: {parsed_details}")
                return parsed_details

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from LLM response: {e}")
                print(f"Problematic response text: '{cleaned_response}'")
                return None
            except Exception as e:
                print(f"An unexpected error occurred during puzzle parsing: {e}")
                return None
        else:
            print(f"Failed to generate puzzle details. LLM Response: {response_text}")
            return None

# --- Main execution for testing (optional, can be commented out) ---
if __name__ == "__main__":
    print("Starting Puzzle Generator Test (V2)...")
    # Make sure your Ollama server is running and the model is available
    generator = PuzzleGenerator(model_name="gemma3:4b") # Or your preferred model

    if not generator.connector.get_models():
         print("No models seem to be available from Ollama.")
    else:
        puzzle_details = generator.generate_parsed_puzzle_details()
        if puzzle_details:
            print("\nSuccessfully generated and parsed puzzle details:")
            print(f"  Phrase: {puzzle_details['phrase']}")
            print(f"  Words: {puzzle_details['words']}")
            print(f"  Category: {puzzle_details['category']}")
            print(f"  Emojis: {puzzle_details['emojis_list']}")
        else:
            print("\nCould not generate or parse puzzle details.")
    print("\nPuzzle Generator Test (V2) Finished.")