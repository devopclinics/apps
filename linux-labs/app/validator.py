# validator.py
import subprocess

def validate_command(user_command, correct_command):
    try:
        # Execute the user's command in a safe environment
        user_output = subprocess.run(user_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Execute the correct command for comparison
        correct_output = subprocess.run(correct_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Compare outputs
        return user_output.stdout == correct_output.stdout and user_output.stderr == correct_output.stderr
    except Exception as e:
        print(f"Error validating command: {str(e)}")
        return False
