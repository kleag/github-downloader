'''
download_repos_parallel.py
Downloads all the repositories listed in repo_names.csv
'''

import argparse
import concurrent.futures
import csv
import os
import subprocess
import sys

from tqdm import tqdm

# Initialize the ArgumentParser
parser = argparse.ArgumentParser(
    description="Clone GitHub repositories based on criteria")
parser.add_argument('-f', '--repo-file', dest='repo_file',
                    help='Path to the CSV file containing repository info (repo,stars,language)',
                    default="github_repositories.csv")
parser.add_argument('-s', '--min_stars', type=int, default=100,
                    help='Minimum number of stars to consider')
parser.add_argument('-l', '--languages', action='append',
                    default=None,
                    help='List of accepted languages')
parser.add_argument('--output_dir', default='cloned_repos',
                    help='Directory to store the cloned repositories')
parser.add_argument('--error_log', default='error_log.txt',
                    help='Path to the error log file')
parser.add_argument('--num_threads', type=int, default=10,
                    help='Number of threads for parallel execution')
args = parser.parse_args()
print(f"min stars: {args.min_stars}", file=sys.stderr)
print(f"languages: {args.languages}", file=sys.stderr)
# Rest of the script remains the same
NUM_PARALLEL = args.num_threads
CLONE_DIR = args.output_dir
ERROR_LOG = args.error_log

my_env = os.environ.copy()
my_env["GIT_TERMINAL_PROMPT"] = "0"

def clone_repository(repo):
    try:
        repo_name, stars, language = repo
        repo_url = f"https://github.com/{repo_name}"
        clone_path = os.path.join(CLONE_DIR, repo_name)

        if os.path.exists(clone_path):
            return f"{repo_name}", f"{repo_name} (already present)"
        if int(stars) < args.min_stars:
            return None, f"Filtered {repo_name}, stars"
        if args.languages and language not in args.languages:
            return None, f"Filtered {repo_name}, language ({language})"

        os.makedirs(clone_path, exist_ok=True)

        with (open(f'{clone_path}_output.log', 'w') as stdout_file,
              open(f'{clone_path}_error.log', 'w') as stderr_file):
            result = subprocess.run(['git', 'clone', "--depth", "1", "--single-branch",
                                     repo_url, clone_path],
                                    stdout=stdout_file, stderr=stderr_file, text=True,
                                    env=my_env)
            if result.returncode == 0:
                return f"{repo_name}", f"Cloned {repo_name}"
            else:
                return None, f"Failed {repo_name}"
    except Exception as e:
        with open(ERROR_LOG, 'a') as error_log:
            error_log.write(f"Error cloning {repo_url}: {e}\n")
        return None, f"Error cloning {repo_url}: {e}"
    return None, "Nothing done"

with open(args.repo_file, 'r') as f:
    csv_reader = csv.reader(f)
    repositories = list(map(tuple, csv_reader))

os.makedirs(CLONE_DIR, exist_ok=True)
open(ERROR_LOG, 'w').close()

# Use a list to store the results of the cloning attempts
results = []

# Use tqdm to create a progress bar
with tqdm(total=len(repositories), desc="Cloning Repositories", leave=False) as pbar:
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PARALLEL) as executor:
        # Using 'map' with 'tqdm' to track progress
        for result, message in executor.map(clone_repository, repositories):
            if result:
                results.append(result)
            pbar.write(message)
            pbar.update(1)  # Increment the progress bar


print("Cloning complete. Check the error log for details.")
print("Successfully cloned repositories:", results)
