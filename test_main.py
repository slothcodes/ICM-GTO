import subprocess

def test_run():
    # Run the main script to ensure no exceptions are raised and it completes successfully
    result = subprocess.run(["python3", "main.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)

if __name__ == "__main__":
    test_run()
