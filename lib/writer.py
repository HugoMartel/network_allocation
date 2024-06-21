from os import path, mkdir, remove
from datetime import datetime

output_folder = "output"
log_file = datetime.now().isoformat() + "_log.txt"

def reset_output_files(filenames:list[str]) -> None:
    # Create output folder if it doesn't exist
    if not path.isdir(output_folder):
        print(f"Creating output folder '{output_folder}'")
        mkdir(output_folder)

    # Reset defined output files
    for f in filenames:
        f = path.join(output_folder, f)
        if path.isfile(f):
            print(f"Removing existing file '{f}'")
            remove(f)

def write_log(log:str) -> None:
    with open(path.join(output_folder, log_file), "a") as f:
        f.write(f"{datetime.now().isoformat()} {log}\n")

def write_output(output:str, output_file:str) -> None:
    with open(path.join(output_folder, output_file), "a") as f:
        f.write(output)
