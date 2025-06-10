# Icon Puzzle Game

Welcome to **Icon Puzzle Game**, a browser-based emoji puzzle game that challenges your logic and creativity! This project leverages the power of local Large Language Models (LLMs) via Ollama to generate unique and thought-provoking emoji rebuses for you to solve.

This is a Progressive Web App (PWA), meaning you can "install" it on your desktop or mobile device for a native-app-like experience.

![Game Screenshot](https://i.imgur.com/gKfrChJ.png)

## 🎮 How to Play

The goal of the game is simple: guess the hidden phrase represented by a sequence of emojis.

1.  **Start a New Game**: A new puzzle is automatically generated when you load the page. Press the "New Puzzle" button at any time to get a new challenge.
2.  **Analyze the Emojis**: Look at the emojis and the category clue. They form a rebus that represents a common phrase, a movie title, a person, or a concept.
3.  **Guess the Phrase**: Type your answer into the input field. The game provides real-time feedback by filling in correctly guessed letters.
4.  **Use Hints**: If you're stuck, you can request letter hints to help you solve the puzzle, but each hint will cost you points.
5.  **Scoring**: You start with a base score for each puzzle. Solving it correctly adds to your total score, while using hints deducts from it.

## ✨ Features

* **Dynamic Puzzle Generation**: Never play the same game twice! Puzzles are generated on-the-fly by a local LLM.
* **LLM-Powered**: Connects to an Ollama instance to generate creative and challenging emoji rebuses.
* **Progressive Web App (PWA)**: Installable on desktop and mobile for a seamless, offline-first experience.
* **Responsive Design**: A clean, intuitive interface that works beautifully on any screen size.
* **Scoring System**: Tracks your total score and penalizes for hints to add a competitive edge.
* **Puzzle Logging**: Captures game data to a local `puzzle_log.csv` for analysis and fine-tuning puzzle quality.

## 🛠️ Tech Stack

* **Backend**: Python with Flask
* **LLM Integration**: Ollama
* **Frontend**: HTML5, CSS3, vanilla JavaScript
* **Deployment**: Can be run locally or deployed to any server that supports Python.

## 📂 Project Structure
## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

1.  **Python 3.8+**: Make sure you have a modern version of Python installed.
    ```sh
    python3 --version
    ```
2.  **Ollama**: The game relies on a running Ollama instance for puzzle generation.
    * [Download and install Ollama](https://ollama.com/download).
    * Pull the model used by the game (the default is `gemma3:27b`). Open your terminal and run:
        ```sh
        ollama pull gemma3:27b
        ```
    * Ensure the Ollama application is running before you start the Flask server.

### Installation

1.  **Clone the Repository**:
    ```sh
    git clone [https://github.com/your-username/Icon-Puzzle-Game.git](https://github.com/your-username/Icon-Puzzle-Game.git)
    cd Icon-Puzzle-Game
    ```

2.  **Set up a Python Virtual Environment** (Recommended):
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    A `requirements.txt` file is included to manage dependencies.
    ```sh
    pip install -r requirements.txt
    ```

    *For reference, the contents of `requirements.txt` are:*
    ```txt
    Flask
    requests
    ```

4.  **Run the Application**:
    ```sh
    python src/app.py
    ```
    You should see output indicating that the Flask server is running and has connected to the puzzle generator.

5.  **Play the Game**:
    * Open your web browser and navigate to `http://127.0.0.1:5000`.

### Configuration

* **LLM Model**: To use a different Ollama model, change the `model_name` variable in `src/app.py` and `src/generator.py`. Make sure you have pulled the new model with `ollama pull <your-model-name>`.
* **Log File Path**: The path for the `puzzle_log.csv` is hardcoded in `src/generator.py`. You can change the `self.csv_log_file_path` variable if you wish to store it elsewhere.

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**. In short, this means you are free to use, study, share, and improve the software. If you run a modified version of this software on a publicly accessible server, you must also offer the complete source code of your version to your users.

### Commercial Licensing

For individuals and non-commercial open-source projects, the AGPLv3 license is straightforward.

If you wish to include this software in a **proprietary or closed-source commercial application**, please contact me to arrange for a commercial license. This will grant you the right to use the software without the copyleft restrictions of the AGPLv3.