import sys
import zipfile
import tempfile
import subprocess

def process_zip_file(archive, main_file, temp_dir):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the zip file into the temporary directory
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Start a subprocess with the temporary directory as the cwd
        process = subprocess.Popen(
            [sys.executable, "-m", "opensees", main_file],  # Replace with the command you want to run
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the process to complete and get the output
        stdout, stderr = process.communicate()
        
        # Print the output for debugging purposes
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())

