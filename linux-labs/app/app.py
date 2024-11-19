from flask import Flask, send_from_directory, request, jsonify
import json
import os
import subprocess

app = Flask(__name__)

# Path to the questions and config file, mounted as a ConfigMap
QUESTIONS_FILE_PATH = '/app/config/questions.json'
CONFIG_FILE_PATH = '/app/config/title'

# Load questions from the ConfigMap file
def load_questions():
    try:
        with open(QUESTIONS_FILE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions.json: {e}")
        return []

# Load the config title from the ConfigMap file
def load_config():
    try:
        with open(CONFIG_FILE_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: title file not found.")
        return "Labs"
    except Exception as e:
        print(f"Error reading title: {e}")
        return "Labs"

# Initialize questions
questions = load_questions()
current_question_index = 0
score = 0

# Helper function to reset and set up the environment
def reset_environment():
    try:
        subprocess.run("sudo userdel -r developer", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo groupdel adminteam", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo groupadd adminteam", shell=True)
        subprocess.run("sudo useradd developer", shell=True)
        subprocess.run("echo 'developer:password123' | sudo chpasswd", shell=True)
    except Exception as e:
        print(f"Error resetting environment: {e}")

# Serve the initial HTML page
@app.route("/")
def home():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# Route to get the current question
@app.route("/question", methods=["GET"])
def get_question():
    global current_question_index, questions
    if current_question_index < len(questions):
        return jsonify({"question": questions[current_question_index]["question"]})
    else:
        return jsonify({"question": None, "message": "All questions completed!"})

# Route to handle command execution and validate the answer
@app.route("/execute", methods=["POST"])
def execute_command():
    global current_question_index, score, questions
    if current_question_index >= len(questions):
        return jsonify({"output": "All questions completed!", "done": True})

    data = request.get_json()
    user_command = data.get("command")
    expected_command = questions[current_question_index]["answer"]

    try:
        user_output = subprocess.run(user_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = user_output.stdout + user_output.stderr
        if user_output.returncode == 0 and user_command.strip() == expected_command.strip():
            score += 1
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. Expected: {expected_command}"
        current_question_index += 1
        return jsonify({"output": output + "\n" + feedback, "done": False})
    except Exception as e:
        return jsonify({"output": f"Error: {e}", "done": False}), 500

# Route to return the final score
@app.route("/score", methods=["GET"])
def get_score():
    global score, questions
    total_questions = len(questions)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    message = (
        f"Thumbs up! You passed with a score of {percentage:.2f}%!"
        if percentage >= 80
        else f"You scored {percentage:.2f}%. Please review and try again."
    )
    return jsonify({"score": percentage, "message": message})

# Route to restart the lab
@app.route("/restart", methods=["POST"])
def restart_lab():
    global current_question_index, score
    current_question_index = 0
    score = 0
    reset_environment()
    return jsonify({"message": "Lab restarted. Good luck!"})

# Route to get a hint
@app.route("/hint", methods=["GET"])
def get_hint():
    if current_question_index < len(questions):
        return jsonify({"hint": questions[current_question_index]["answer"]})
    else:
        return jsonify({"hint": None, "message": "No more questions available."})

# Route to view all questions
@app.route("/all-questions", methods=["GET"])
def view_all_questions():
    return jsonify({"questions": [q["question"] for q in questions]})

# Route to get the title
@app.route("/config", methods=["GET"])
def get_config():
    title = load_config()
    return jsonify({"title": title})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

