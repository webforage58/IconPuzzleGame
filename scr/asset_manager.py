# src/asset_manager.py

import os
from pathlib import Path

# Determine the project root directory.
# This assumes asset_manager.py is in a 'src' subdirectory of the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the path to the assets and fonts directory
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
EMOJI_FONT_FILENAME = "NotoColorEmoji-Regular.ttf"

# The full path to your Noto Color Emoji font file
DEFAULT_EMOJI_FONT_PATH = FONT_DIR / EMOJI_FONT_FILENAME

class AssetManager:
    def __init__(self, font_path=DEFAULT_EMOJI_FONT_PATH):
        """
        Initializes the AssetManager.

        Args:
            font_path (Path, optional): The path to the emoji font file. 
                                        Defaults to DEFAULT_EMOJI_FONT_PATH.
        """
        self.font_path = Path(font_path)

    def get_emoji_font_path(self):
        """
        Verifies that the emoji font file exists and returns its path.

        Returns:
            Path | None: The Path object to the font file if it exists, otherwise None.
        """
        if self.font_path.exists() and self.font_path.is_file():
            print(f"Font file found: {self.font_path}")
            return self.font_path
        else:
            print(f"Error: Font file not found at {self.font_path}")
            print(f"Please ensure '{EMOJI_FONT_FILENAME}' is in the '{FONT_DIR}' directory.")
            return None

# --- Main execution for testing ---
if __name__ == "__main__":
    print("Starting Asset Manager Test...")
    
    # This uses the default path defined in this file.
    # If your NotoColorEmoji-Regular.ttf is at:
    # /Users/johnhuberd/PythonProjects/ConcentrationGameLocal/assets/fonts/NotoColorEmoji-Regular.ttf
    # and this script (asset_manager.py) is in:
    # /Users/johnhuberd/PythonProjects/ConcentrationGameLocal/src/asset_manager.py
    # then the relative path calculation should work.
    
    manager = AssetManager()
    verified_font_path = manager.get_emoji_font_path()

    if verified_font_path:
        print(f"Successfully verified font path: {verified_font_path}")
    else:
        print("Font path verification failed.")
        print(f"Expected location: {DEFAULT_EMOJI_FONT_PATH}")
        # Additional debug information:
        print(f"PROJECT_ROOT determined as: {PROJECT_ROOT}")
        print(f"ASSETS_DIR determined as: {ASSETS_DIR}")
        print(f"FONT_DIR determined as: {FONT_DIR}")


    print("\nAsset Manager Test Finished.")