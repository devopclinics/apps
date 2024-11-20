from flask import Flask, send_from_directory, request, jsonify
import subprocess
import json
import os
import yaml  # Import the yaml module to parse YAML

app = Flask(__name__)

# Paths to the questions and config file, mounted as a ConfigMap
QUESTIONS_FILE_PATH = '/app/config/questions.json'  # This refers to the YAML content from the ConfigMap
CONFIG_FILE_PATH = '/app/config/title'

# Load questions from the ConfigMap file
def load_questions():
    try:
        with open(QUESTIONS_FILE_PATH) as f:
            # Parse the YAML content to convert it into a list of dictionaries
            questions = yaml.safe_load(f)
            if not isinstance(questions, list):
                print("Error: Questions are not in the expected list format.")
                return []
            print(f"Loaded {len(questions)} questions successfully.")
            return questions
    except FileNotFoundError:
        print("Error: questions.json file not found.")
        return []
    except yaml.YAMLError:
        print("Error: Failed to parse questions.yaml content.")
        return []

# Initialize questions and state variables
questions = load_questions()
current_question_index = 0
score = 0

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

# Helper function to reset and set up the environment
def reset_environment():
    try:
        subprocess.run("sudo userdel -r developer", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo groupdel adminteam", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo groupadd adminteam", shell=True)
        subprocess.run("sudo useradd developer", shell=True)
        subprocess.run("echo 'developer:password123' | sudo chpasswd", shell=True)
    except Exception as e:
        print(f"Error resetting environment: {str(e)}")

# Serve the initial HTML page
@app.route("/")
def home():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# Route to get the current question
@app.route("/question", methods=["GET"])
def get_question():
    global current_question_index, questions
    questions = load_questions()  # Reload questions dynamically
    if len(questions) == 0:
        print("Error: No questions available.")
        return jsonify({"question": None, "message": "No questions available."})

    print(f"Current question index: {current_question_index}, Total questions: {len(questions)}")
    if current_question_index < len(questions):
        return jsonify({"question": questions[current_question_index]["question"]})
    else:
        return jsonify({"question": None, "message": "All questions completed!"})

# Route to handle command execution and validate the answer
@app.route("/execute", methods=["POST"])
def execute_command():
    global current_question_index, score, questions
    questions = load_questions()  # Reload questions dynamically

    if len(questions) == 0:
        return jsonify({"output": "No questions available!", "done": True})

    if current_question_index >= len(questions):
        return jsonify({"output": "All questions completed!", "done": True})

    data = request.get_json()
    user_command = data.get("command")
    expected_command = questions[current_question_index]["answer"]

    try:
        # Run the user's command
        user_output = subprocess.run(user_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = user_output.stdout + user_output.stderr

        # Check if the command is correct
        if user_output.returncode == 0 and user_command.strip() == expected_command.strip():
            score += 1
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. Expected: {expected_command}"

        # Move to the next question
        current_question_index += 1
        print(f"Score: {score}, Current question index: {current_question_index}")
        return jsonify({"output": output + "\n" + feedback, "done": False})
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return jsonify({"output": f"Error: {str(e)}", "done": False}), 500

# Route to calculate and return the final score
@app.route("/score", methods=["GET"])
def get_score():
    global score, questions
    total_questions = len(questions)
    if total_questions == 0:
        print("No questions available to calculate score.")
        return jsonify({"score": 0, "message": "No questions available to calculate score."})

    percentage = (score / total_questions) * 100
    if percentage >= 80:
        message = "Thumbs up! You passed with a score of {:.2f}%!".format(percentage)
    else:
        message = "You scored {:.2f}%. Please review and try again.".format(percentage)
    print(f"Score calculated: {percentage}%")
    return jsonify({"score": percentage, "message": message})

# Route to restart the lab
@app.route("/restart", methods=["POST"])
def restart_lab():
    global current_question_index, score
    current_question_index = 0
    score = 0
    print("Lab restarted. Current question index reset to 0.")
    reset_environment()  # Reset the environment
    return jsonify({"message": "Lab restarted. Good luck!"})

# Route to get a hint (expected answer) for the current question
@app.route("/hint", methods=["GET"])
def get_hint():
    global current_question_index, questions
    questions = load_questions()  # Reload questions dynamically
    if len(questions) == 0:
        return jsonify({"hint": None, "message": "No questions available."})

    if current_question_index < len(questions):
        hint = questions[current_question_index]["answer"]
        return jsonify({"hint": hint})
    else:
        return jsonify({"hint": None, "message": "No more questions available."})

# Route to view all questions
@app.route("/all-questions", methods=["GET"])
def view_all_questions():
    questions = load_questions()  # Reload questions dynamically
    if len(questions) == 0:
        return jsonify({"questions": [], "message": "No questions available."})

    question_list = [q["question"] for q in questions]
    return jsonify({"questions": question_list})

# Route to get the title
@app.route("/config", methods=["GET"])
def get_config():
    title = load_config()
    print(f"Config title: {title}")
    return jsonify({"title": title})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
