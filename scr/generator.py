# src/generator.py

from model_connector import ModelConnector
import json
import random
import os
import csv # Added for CSV logging
from datetime import datetime # Added for timestamping

class PuzzleGenerator:
    def __init__(self, model_name="gemma3:27b"):
        self.connector = ModelConnector()
        self.model_name = model_name
        
        # --- CSV Logging Setup ---
        self.csv_log_file_path = "/Users/johnhuberd/PythonProjects/ConcentrationGameWeb/puzzle_log.csv"
        self.csv_header = ["Timestamp", "Category", "Phrase", "Emojis"]
        
        log_dir = os.path.dirname(self.csv_log_file_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True) # exist_ok=True prevents error if dir exists
                print(f"Created log directory: {log_dir}")
            except OSError as e:
                print(f"Warning: Could not create log directory {log_dir}. Error: {e}")
        # --- End CSV Logging Setup ---

        available_models = self.connector.refresh_models()
        if not available_models:
            print("Warning: No models reported by Ollama. Puzzle generation might fail.")
        elif self.model_name not in available_models:
            print(f"Warning: Model '{self.model_name}' not found in available models: {available_models}.")
            if available_models:
                print(f"Please ensure model '{self.model_name}' is available in Ollama, or choose from: {available_models}")
            else:
                 print("No models available from Ollama. Cannot proceed with puzzle generation.")

        self.categories = [
            "Toxic Relationship Red Flags", "Divorce Lawyer Gold", "Walk of Shame Essentials", "Tinder Bio Lies",
            "Quarantine Confessions", "Ex's New Partner Stalking", "Things You Google at 3AM",
            "Regrettable Tattoo Ideas", "Midlife Crisis Purchases", "College Blackout Stories",
            "Sugar Daddy Expectations", "OnlyFans Content Ideas", "Therapy Session Topics", "Drunk Text Regrets",
            "Friends with Benefits Rules", "Strip Club Stories", "Hangover Cures", "Bad Life Decisions",
            "Hookup Horror Stories", "Office Affair Drama", "Festival Drug Stories", "Booty Call Etiquette",
            "Breakup Revenge Plots", "Embarrassing Medical Questions", "Trust Issues Origins", "AI & Tech Buzzwords",
            "Awkward Social Situations", "Bedroom Activities", "Drunk Thoughts", "Guilty Pleasures",
            "Things You Do When Nobody's Watching", "Millennial Problems", "Gen Z Slang", "Reality TV Drama",
            "Conspiracy Theories", "Superhero Innuendos", "Awkward Family Holiday Moments", "Vegas Stories",
            "Bachelor Party Mishaps", "Dating App Disasters", "Workplace Gossip",
            "Passive Aggressive Notes From Neighbors", "Shower Thoughts", "Things Said During Labor",
            "Social Media Addictions", "Things You've Secretly Judged People For", "Things That Make You Go Hmm",
            "Forbidden Love Stories", "Guilty Netflix Binges", "Regrettable Fashion Choices",
            "Conspiracy Theories That Are Almost Believable", "The Art of the Subtle Shade",
            "Pet Peeves That Make You Question Humanity", "Wine Mom Wisdom", "First World Problems",
            "Zoom Meeting Fails", "Influencer Scandals", "Hashtag Fails", "Viral TikTok Challenges",
            "Meme Overlords", "Doomscrolling Habits", "Autocorrect Fails", "Spam Email Gems",
            "Forgotten Social Media Platforms", "Unsubscribe Reasons", "Password Struggles",
            "Wifi Password Requests", "Reply All Disasters", "Selfie Gone Wrong", "Cancelled Celebrities",
            "Streaming Service Overload", "Fake News Headlines", "Online Dating Profile Cliches",
            "Urban Dictionary Gems", "Bad Excuses", "Awkward Silences", "Public Transport Nightmares",
            "Parenting Fails", "Bad Gift Reactions", "Jury Duty Thoughts", "DIY Disasters",
            "Overheard Conversations", "Telemarketer Trolling", "Group Chat Drama", "Wedding Guest Complaints",
            "Things Found Under the Couch", "Reasons to Call in Sick", "Gym Fails", "Cooking Disasters",
            "Kids Say the Darndest Things (Modern)", "Terrible Pick-Up Lines", "Misheard Song Lyrics",
            "Running Late Excuses", "Things You Pretend to Understand", "Bad Date Stories",
            "Reasons Your Ex is an Ex", "Things Your Therapist Judges You For", "Bachelorette Party Secrets",
            "Dirty Laundry (Figurative)", "Bar Fight Starters", "Designated Driver Woes", "Spring Break Regrets",
            "Reasons to Break Up", "Skeletons in the Closet", "Worst Nightmares", "Questionable Life Choices",
            "Shady Business Practices", "Things Overheard in a Bar Bathroom", "Last Call Regrets",
            "Craigslist Missed Connections", "Black Market Bargains", "Secrets From Your Bartender",
            "Ways to Get Fired", "Retro Gaming Nostalgia", "90s Kid Problems", "Forgotten TV Shows",
            "Reality TV Villains", "Catchphrases That Won't Die", "One Hit Wonders", "Childhood Toys You Miss",
            "Boy Band Obsessions", "Movie Quotes You Use Daily", "Things That Were Cool in High School",
            "Boomer Complaints", "Gen X Angst", "Internet Challenges of Yesteryear", "Old Tech Struggles",
            "Things That Peaked in the 2000s", "Cult Classic Movies", "Annoying Jingles",
            "Unpopular Opinions (Pop Culture)", "Things Overhyped by Media", "Celebrity Couple Nicknames",
            "Late Night Snack Cravings", "Diet Fails", "Brunch Obsessions", "Craft Beer Snobbery",
            "Exotic Food Challenges", "Reasons to Order Takeout", "Bad Restaurant Experiences",
            "Things You Shouldn't Microwave", "Food Coma Symptoms", "Weird Food Combinations",
            "Potluck Disasters", "Office Fridge Violations", "Hangry Confessions", "Complaints to the Chef",
            "Things You Only Eat When Drunk", "Things That Sound Dirty But Aren't", "Unspoken Rules",
            "Daily Annoyances", "Small Victories", "Reasons to Stay in Bed", "Florida Man Headlines",
            "If Animals Could Talk", "Signs You're Getting Old", "Pet Shaming Reasons",
            "Things That Need a Warning Label", "Useless Superpowers", "Ways to Annoy People",
            "What Your Car Says About You", "Things That Are Overpriced"
        ]

        self.focus_strings = [
            "Focus the puzzle on humor.", "Focus the puzzle on a pet.", "Focus the puzzle on eating.",
            "Emphasize a surprising element in the puzzle.",
            "Consider a common daily activity for the puzzle's theme.",
            "Make the puzzle thought-provoking or clever."
        ]

        self.recently_used_phrases = []
        self.max_recent_phrases = 15
        self.max_retry_attempts = 3

    def _add_to_recent_phrases(self, phrase):
        if not phrase:
            return
        if phrase in self.recently_used_phrases:
            self.recently_used_phrases.remove(phrase)
        self.recently_used_phrases.append(phrase)
        if len(self.recently_used_phrases) > self.max_recent_phrases:
            self.recently_used_phrases.pop(0)

    def _log_puzzle_to_csv(self, category, phrase, emojis_string):
        """Appends the successfully generated puzzle details to a CSV log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_to_log = [timestamp, category, phrase, emojis_string]
        
        file_exists = os.path.isfile(self.csv_log_file_path)
        
        try:
            with open(self.csv_log_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists or os.path.getsize(self.csv_log_file_path) == 0:
                    writer.writerow(self.csv_header) # Write header if new file or empty
                writer.writerow(row_to_log)
        except IOError as e:
            print(f"Error writing to CSV log file {self.csv_log_file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV logging: {e}")

    def _create_emoji_puzzle_prompt_v2(self, category, previous_phrases=None):
        dynamic_focus_hint = random.choice(self.focus_strings)
        if previous_phrases is None: previous_phrases = []
        avoid_phrases_instruction = ""
        if previous_phrases:
            avoid_phrases_list = ", ".join([f"'{p}'" for p in previous_phrases])
            avoid_phrases_instruction = (
                f"\n**CRITICAL INSTRUCTION: To ensure variety, you MUST NOT generate any of the "
                f"following phrases that have been used recently: {avoid_phrases_list}. "
                "You MUST provide a completely new and unique phrase not on this list. Generate a 5 digit random number and use that for the seed**"
            )
        prompt = (
            f"Creative Hint for this request: \"{dynamic_focus_hint}\"\n"
            f"Your task is to generate a puzzle based on a common phrase from the category: '{category}'.\n"
            "The phrase must consist of 3 words or less (e.g., 1, 2, or 3 words).\n"
            "**The phrase absolutely MUST be common, widely known, and popular saying. No obscure or niche terms, "
            "especially if the category is broad. Focus on phrases that a general audience would recognize.**\n"
            f"**It is absolutely ESSENTIAL that you provide a new, unique, and creative example each time you are called (especially considering this hint: \"{dynamic_focus_hint}\").**"
            f"{avoid_phrases_instruction}\n\n"
            "Provide your response exclusively in a VALID JSON format with the following keys:\n"
            "1. 'phrase': The full solution phrase (string).\n"
            "2. 'words': A list of strings, where each string is a word from the phrase.\n"
            "3. 'category': This MUST be exactly '{category}' (string). Do not change this value.\n"
            "4. 'emojis': A sequence of 3 to 5 emojis that represent the phrase, as a single string with emojis separated by spaces.\n"
            "\nExample JSON output format (if the category requested was 'Idiom'):\n"
            "```json\n{\n  \"phrase\": \"A blessing in disguise\",\n  \"words\": [\"A\", \"blessing\", \"in\", \"disguise\"],\n  \"category\": \"Idiom\",\n  \"emojis\": \"🙏 🎭 ✨\"\n}\n```\n"
            f"Remember, the 'category' field in your JSON response must be exactly '{category}'. Only output the JSON object, nothing else before or after."
        )
        return prompt

    def _generate_single_puzzle_attempt(self, current_category):
        prompt_text = self._create_emoji_puzzle_prompt_v2(current_category, self.recently_used_phrases)
        response_text = self.connector.enhance_prompt(self.model_name, prompt_text, prompt_type="general")

        # Note: Raw LLM response logging is removed as per new request.
        # CSV logging will happen after successful parsing.

        if response_text and not response_text.startswith("Error:") and not response_text.startswith("No response from model"):
            print(f"Raw LLM response for puzzle details:\n'{response_text}'")
            try:
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"): cleaned_response = cleaned_response[len("```json"):].strip()
                elif cleaned_response.startswith("```"): cleaned_response = cleaned_response[len("```"):].strip()
                if cleaned_response.endswith("```"): cleaned_response = cleaned_response[:-len("```")].strip()

                puzzle_data = json.loads(cleaned_response)
                required_keys = ['phrase', 'words', 'category', 'emojis']
                if not all(key in puzzle_data for key in required_keys):
                    print(f"Error: LLM response JSON is missing one or more required keys. Data: {puzzle_data}")
                    return None
                if puzzle_data.get('category') != current_category:
                    print(f"Warning: LLM returned category '{puzzle_data.get('category')}' but category '{current_category}' was requested. Using requested category.")
                    puzzle_data['category'] = current_category
                if not isinstance(puzzle_data['words'], list) or not puzzle_data['words']:
                    print(f"Error: 'words' field is not a non-empty list. Data: {puzzle_data}")
                    return None
                if not all(isinstance(word, str) for word in puzzle_data['words']):
                    print(f"Error: Not all items in 'words' field are strings. Data: {puzzle_data}")
                    return None
                generated_phrase = puzzle_data.get('phrase')
                if not generated_phrase:
                     print(f"Error: 'phrase' field is missing or empty. Data: {puzzle_data}")
                     return None
                emoji_char_list = [emoji for emoji in puzzle_data['emojis'].split(' ') if emoji]
                if not emoji_char_list:
                    print(f"Warning: LLM response had an empty emoji string after parsing: '{puzzle_data['emojis']}'")
                    return None
                parsed_details = {
                    'phrase': puzzle_data['phrase'], 'words': puzzle_data['words'],
                    'category': puzzle_data['category'], 'emojis_list': emoji_char_list
                }
                return parsed_details
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from LLM response: {e}\nProblematic response text: '{cleaned_response}'")
                return None
            except Exception as e:
                print(f"An unexpected error occurred during puzzle parsing: {e}")
                return None
        else:
            print(f"Failed to generate puzzle details. LLM Response: {response_text}")
            return None

    def generate_parsed_puzzle_details(self):
        if not self.model_name and (not self.connector or not self.connector.get_models()):
            print("Error: No LLM model is configured or ModelConnector not properly initialized.")
            return None
        if not self.categories:
            print("Error: No categories defined for puzzle generation.")
            return None

        current_category = random.choice(self.categories)
        print(f"Requesting puzzle for randomly selected category: '{current_category}'")
        print(f"Will instruct LLM to avoid these recent phrases (up to {self.max_recent_phrases}): {self.recently_used_phrases}")

        for attempt in range(self.max_retry_attempts):
            print(f"\nGeneration attempt {attempt + 1}/{self.max_retry_attempts}")
            parsed_details = self._generate_single_puzzle_attempt(current_category)
            
            if parsed_details is None:
                print(f"Attempt {attempt + 1} failed to generate valid puzzle details.")
                continue
            
            generated_phrase = parsed_details['phrase']
            
            if generated_phrase in self.recently_used_phrases:
                print(f"⚠️  Duplicate detected! Phrase '{generated_phrase}' is already in recent history.")
                if attempt == self.max_retry_attempts - 1:
                    print(f"Max retries reached. Using duplicate phrase: {generated_phrase}")
                    self._add_to_recent_phrases(generated_phrase)
                    # --- Log to CSV ---
                    emojis_string = " ".join(parsed_details['emojis_list'])
                    self._log_puzzle_to_csv(parsed_details['category'], parsed_details['phrase'], emojis_string)
                    # --- End Log to CSV ---
                    print(f"Successfully parsed puzzle details (with duplicate warning): {parsed_details}")
                    return parsed_details
                else:
                    print("Retrying to get a unique phrase...")
                    continue
            else:
                print(f"✅ Unique phrase generated: {generated_phrase}")
                self._add_to_recent_phrases(generated_phrase)
                # --- Log to CSV ---
                emojis_string = " ".join(parsed_details['emojis_list'])
                self._log_puzzle_to_csv(parsed_details['category'], parsed_details['phrase'], emojis_string)
                # --- End Log to CSV ---
                print(f"Successfully parsed puzzle details: {parsed_details}")
                return parsed_details
        
        print(f"Failed to generate a valid puzzle after {self.max_retry_attempts} attempts.")
        return None

# --- Main execution for testing (optional) ---
if __name__ == "__main__":
    print("Starting Puzzle Generator Test (CSV Logging Version)...")
    generator = PuzzleGenerator(model_name="gemma3:27b")

    if not generator.connector or not generator.connector.get_models():
         print("Could not connect to Ollama or no models available.")
    else:
        num_test_puzzles = 3
        print(f"Total categories available: {len(generator.categories)}")
        print(f"Will attempt to generate {num_test_puzzles} puzzles.")
        print(f"Puzzle details will be logged to CSV: {generator.csv_log_file_path}")

        for i in range(num_test_puzzles):
            print(f"\n--- Generating puzzle attempt {i+1}/{num_test_puzzles} ---")
            puzzle_details = generator.generate_parsed_puzzle_details()
            if puzzle_details:
                print("\nSuccessfully generated and parsed puzzle details (also logged to CSV):")
                print(f"  Category: {puzzle_details['category']}")
                print(f"  Phrase: {puzzle_details['phrase']}")
                print(f"  Words: {puzzle_details['words']}")
                print(f"  Emojis: {puzzle_details['emojis_list']}")
            else:
                print("\nCould not generate or parse puzzle details.")
            print("--------------------------------------")
    print("\nPuzzle Generator Test (CSV Logging Version) Finished.")