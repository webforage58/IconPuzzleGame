# src/generator.py

from model_connector import ModelConnector # Ensures ModelConnector is imported
import json

class PuzzleGenerator:
    def __init__(self, model_name="gemma3:4b"): # Ensure this model is available in your Ollama
        self.connector = ModelConnector() # This line requires the import above
        self.model_name = model_name

        # Check model availability (optional, but good for diagnosing issues)
        available_models = self.connector.refresh_models()
        if not available_models:
            print("Warning: No models reported by Ollama. Puzzle generation might fail.")
        elif self.model_name not in available_models:
            print(f"Warning: Model '{self.model_name}' not found in available models: {available_models}.")
            if available_models:
                print(f"Please ensure model '{self.model_name}' is available in Ollama, or choose from: {available_models}")
            else:
                 print("No models available from Ollama. Cannot proceed with puzzle generation.")

        # --- NEW: For category cycling and preventing repeats ---
        self.categories = [
            "Idiom",
            "Movie Title",
            "Book Title",
            "Well-known Saying",
            "Song Title",
            "Historical Quote",
            "Common Object",
            "Famous Landmark"
        ]
        self.current_category_index = 0
        self.recently_used_phrases = [] # Stores the last N phrases (e.g., last 5)
        self.max_recent_phrases = 5     # How many recent phrases to track and tell the LLM to avoid
        # --- END NEW ---

    # --- NEW: Helper method to manage recently used phrases ---
    def _add_to_recent_phrases(self, phrase):
        """Adds a phrase to the list of recently used phrases, maintaining max size."""
        if not phrase:
            return
        # Remove if already present to move it to the end (most recent)
        if phrase in self.recently_used_phrases:
            self.recently_used_phrases.remove(phrase)
        self.recently_used_phrases.append(phrase)
        # Keep the list at the maximum allowed size
        if len(self.recently_used_phrases) > self.max_recent_phrases:
            self.recently_used_phrases.pop(0) # Remove the oldest phrase
    # --- END NEW ---

    def _create_emoji_puzzle_prompt_v2(self, category, previous_phrases=None): # MODIFIED: Added category and previous_phrases parameters
        """
        Creates a prompt for the LLM to generate an emoji puzzle for a specific category.
        Asks for JSON output and strongly encourages variety, avoiding specified previous phrases.
        """
        if previous_phrases is None:
            previous_phrases = []

        avoid_phrases_instruction = ""
        if previous_phrases:
            # Create a string listing phrases to avoid
            avoid_phrases_list = ", ".join([f"'{p}'" for p in previous_phrases])
            avoid_phrases_instruction = (
                f"\n**CRITICAL INSTRUCTION: To ensure variety, you MUST NOT generate any of the "
                f"following phrases that have been used recently: {avoid_phrases_list}. "
                "You MUST provide a completely new and unique phrase not on this list.**"
            )

        prompt = (
            f"Your task is to generate a puzzle based on a common phrase from the category: '{category}'.\n"
            "The phrase must consist of 3 to 6 words.\n"
            "**It is absolutely ESSENTIAL that you provide a new, unique, and creative example each time you are called.**"
            f"{avoid_phrases_instruction}\n\n"
            "Provide your response exclusively in a VALID JSON format with the following keys:\n"
            "1. 'phrase': The full solution phrase (string).\n"
            "2. 'words': A list of strings, where each string is a word from the phrase.\n"
            "3. 'category': This MUST be exactly '{category}' (string). Do not change this value.\n"
            "4. 'emojis': A sequence of 3 to 5 emojis that represent the phrase, as a single string with emojis separated by spaces.\n"
            "\n"
            "Example JSON output format (if the category requested was 'Idiom'):\n"
            "```json\n" # Added ```json for better parsing chances if LLM includes it
            "{\n"
            "  \"phrase\": \"A blessing in disguise\",\n"
            "  \"words\": [\"A\", \"blessing\", \"in\", \"disguise\"],\n"
            "  \"category\": \"Idiom\",\n"
            "  \"emojis\": \"🙏 🎭 ✨\"\n"
            "}\n"
            "```\n"
            f"Remember, the 'category' field in your JSON response must be exactly '{category}'. "
            "Only output the JSON object, nothing else before or after."
        )
        return prompt

    def generate_parsed_puzzle_details(self): # MODIFIED: To use categories and track phrases
        """
        Generates an emoji puzzle with details (phrase, words, category, emojis)
        and parses it from the expected JSON output, cycling through categories
        and avoiding recently used phrases.

        Returns:
            dict | None: A dictionary with puzzle details if successful, otherwise None.
                         Expected dict keys: 'phrase', 'words', 'category', 'emojis_list'
        """
        if not self.model_name and (not self.connector or not self.connector.get_models()):
            print("Error: No LLM model is configured or ModelConnector not properly initialized.")
            return None

        # --- MODIFIED: Select next category and create prompt ---
        if not self.categories:
            print("Error: No categories defined for puzzle generation.")
            return None
            
        current_category = self.categories[self.current_category_index]
        # Cycle to the next category for the next call
        self.current_category_index = (self.current_category_index + 1) % len(self.categories)

        print(f"Requesting puzzle for category: '{current_category}'")
        print(f"Will instruct LLM to avoid these recent phrases: {self.recently_used_phrases}")

        prompt_text = self._create_emoji_puzzle_prompt_v2(current_category, self.recently_used_phrases)
        # --- END MODIFIED ---

        response_text = self.connector.enhance_prompt(self.model_name, prompt_text, prompt_type="general")

        if response_text and not response_text.startswith("Error:") and not response_text.startswith("No response from model"):
            print(f"Raw LLM response for puzzle details:\n'{response_text}'")
            try:
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[len("```json"):].strip()
                elif cleaned_response.startswith("```"): # Handle if only ``` is present
                    cleaned_response = cleaned_response[len("```"):].strip()
                
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-len("```")].strip()

                puzzle_data = json.loads(cleaned_response)

                required_keys = ['phrase', 'words', 'category', 'emojis']
                if not all(key in puzzle_data for key in required_keys):
                    print(f"Error: LLM response JSON is missing one or more required keys. Data: {puzzle_data}")
                    return None
                
                # --- NEW: Validate category returned by LLM ---
                if puzzle_data.get('category') != current_category:
                    print(f"Warning: LLM returned category '{puzzle_data.get('category')}' but category '{current_category}' was requested. Using requested category.")
                    puzzle_data['category'] = current_category # Enforce the category
                # --- END NEW ---

                if not isinstance(puzzle_data['words'], list) or not puzzle_data['words']:
                    print(f"Error: 'words' field is not a non-empty list. Data: {puzzle_data}")
                    return None
                
                if not all(isinstance(word, str) for word in puzzle_data['words']):
                    print(f"Error: Not all items in 'words' field are strings. Data: {puzzle_data}")
                    return None

                # --- MODIFIED: Add successfully generated phrase to recent list ---
                generated_phrase = puzzle_data.get('phrase')
                if not generated_phrase:
                     print(f"Error: 'phrase' field is missing or empty. Data: {puzzle_data}")
                     return None
                self._add_to_recent_phrases(generated_phrase)
                # --- END MODIFIED ---

                emoji_char_list = [emoji for emoji in puzzle_data['emojis'].split(' ') if emoji]
                if not emoji_char_list:
                    print(f"Warning: LLM response had an empty emoji string after parsing: '{puzzle_data['emojis']}'")
                    # Consider if an empty emoji list is acceptable or should be an error
                    # For now, let's treat it as an error if no emojis are provided, as per prompt.
                    return None 

                parsed_details = {
                    'phrase': puzzle_data['phrase'],
                    'words': puzzle_data['words'],
                    'category': puzzle_data['category'],
                    'emojis_list': emoji_char_list 
                }
                print(f"Successfully parsed puzzle details: {parsed_details}")
                return parsed_details

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from LLM response: {e}")
                print(f"Problematic response text: '{cleaned_response}'") # Print the text that failed to parse
                return None
            except Exception as e:
                print(f"An unexpected error occurred during puzzle parsing: {e}")
                return None
        else:
            print(f"Failed to generate puzzle details. LLM Response: {response_text}")
            return None

# --- Main execution for testing (optional) ---
if __name__ == "__main__":
    print("Starting Puzzle Generator Test (JSON version with Category Cycling)...")
    
    generator = PuzzleGenerator(model_name="gemma3:4b") #

    if not generator.connector or not generator.connector.get_models(): #
         print("Could not connect to Ollama or no models available.")
    else:
        for i in range(10): # Test generating a few puzzles to see category cycling
            print(f"\n--- Generating puzzle attempt {i+1} ---")
            puzzle_details = generator.generate_parsed_puzzle_details()
            if puzzle_details:
                print("\nSuccessfully generated and parsed puzzle details:")
                print(f"  Phrase: {puzzle_details['phrase']}")
                print(f"  Words: {puzzle_details['words']}")
                print(f"  Category: {puzzle_details['category']}")
                print(f"  Emojis: {puzzle_details['emojis_list']}")
                print(f"  Generator's current recent phrases: {generator.recently_used_phrases}")
            else:
                print("\nCould not generate or parse puzzle details.")
            print("--------------------------------------")
    print("\nPuzzle Generator Test (JSON version with Category Cycling) Finished.")