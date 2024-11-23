from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import subprocess

app = FastAPI()

# In-memory stores
sessions = {}
scores = {}

# Load ConfigMap data
CONFIG_PATH = "/config"  # Path where ConfigMap is mounted
with open(f"{CONFIG_PATH}/questions", "r") as f:
    questions = json.loads(f.read())
with open(f"{CONFIG_PATH}/title", "r") as f:
    title = f.read().strip()

class Answer(BaseModel):
    question_id: int
    user_answer: str

@app.get("/title")
def get_title():
    return {"title": title}

@app.get("/questions")
def get_questions():
    return {"questions": questions}

@app.post("/start-session/{user_id}")
def start_session(user_id: str):
    container_name = f"lab-{user_id}"
    try:
        subprocess.run([
            "docker", "run", "-d", "--name", container_name,
            "-v", f"/labs/{user_id}:/user-environment",
            "lab-image:latest"
        ], check=True)
        sessions[user_id] = container_name
        scores[user_id] = 0
        return {"message": "Session started", "container_name": container_name}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to start session")

@app.post("/reset-session/{user_id}")
def reset_session(user_id: str):
    container_name = sessions.get(user_id)
    if not container_name:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        subprocess.run(["docker", "rm", "-f", container_name], check=True)
        start_session(user_id)
        scores[user_id] = 0
        return {"message": "Session reset"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to reset session")

@app.post("/submit-answer/{user_id}")
def submit_answer(user_id: str, answer: Answer):
    if user_id not in scores:
        raise HTTPException(status_code=404, detail="Session not found")
    question = next((q for q in questions if q["id"] == answer.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question["answer"] == answer.user_answer.strip():
        scores[user_id] += 10
        return {"message": "Correct answer!", "score": scores[user_id]}
    return {"message": "Incorrect answer. Try again.", "score": scores[user_id]}

@app.get("/score/{user_id}")
def get_score(user_id: str):
    if user_id not in scores:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"score": scores[user_id]}
