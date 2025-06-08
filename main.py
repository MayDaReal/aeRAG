"""
main.py
An interactive script that prompts the user to choose actions dynamically.
"""

import os
from dotenv import load_dotenv
import sys

# Import managers and classes
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_collector import GitHubCollector
from metadata.metadata_manager import MetadataManager

import multiprocessing
from server.local_storage_server import LocalStorageServer

# from models.llm_manager import LLMManager
# from models.llm_interface import ILLM

# Global variable to track server process
server_process = None

def interactive_menu():
    """
    Displays a menu and returns user's choice as an integer.
    """
    print("\n=== Archethic RAG Interactive Menu ===")
    print("1) Configure/Change LLM Model (not implemented yet)")
    print("2) List GitHub repositories (Test OK)")
    print("3) Update all data for an organization (Don't use and test while validation on the first repo is not completed)")
    print("4) Update all data for selected repositories (Test OK)")
    print("5) Update specific data for multiple repositories (Test OK)")
    print("6) List collections in the database (Test OK)")
    print("7) Start local storage server (Test OK)")
    print("8) Stop local storage server (Test OK)")
    print("9) Show last 10 lines of local server log (Test OK)")
    print("10) Generate/Update metadata for selected repositories and selected collections (TODO test)")
    print("11) Run unit tests (not implemented yet)")
    print("12) Start chat with the LLM (not implemented yet)")
    print("0) Exit (Test OK)")
    choice = input("Enter your choice: ")
    return choice.strip()

def load_configuration():
    """
    Loads environment variables and ensures required ones are set.
    """
    load_dotenv()
    
    required_vars = ["MONGO_URI", "DB_NAME", "LOCAL_STORAGE_PATH", "BASE_URL", "PORT"]
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"Warning: Environment variable {var} is not set!")

    print("Environment variables loaded successfully.")

def run_main_loop():
    """
    Main interactive loop handling user choices dynamically.
    """
    # Load environment variables
    load_configuration()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "archethic_rag")

    # Initialize FileStorageManager once
    local_storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("LOCAL_STORAGE_PATH", "local_storage"))
    base_url = os.getenv("BASE_URL", f"http://localhost:{os.getenv('PORT', 8000)}")
    storage_manager = FileStorageManager(base_storage_path=local_storage_path, base_url=base_url)

    try:
        while True:
            choice = interactive_menu()

            if choice == "1":
                # cmd_configure_llm()
                pass
            elif choice == "2":
                cmd_list_github_repos(mongo_uri, db_name, storage_manager)
            elif choice == "3":
                cmd_update_org_data(mongo_uri, db_name, storage_manager)
            elif choice == "4":
                cmd_update_repos_data(mongo_uri, db_name, storage_manager)
            elif choice == "5":
                cmd_update_multiple_repos_specific_data(mongo_uri, db_name, storage_manager)
            elif choice == "6":
                cmd_list_collections(mongo_uri, db_name)
            elif choice == "7":
                cmd_start_local_server()
            elif choice == "8":
                cmd_stop_local_server()
            elif choice == "9":
                cmd_view_local_server_logs()
            elif choice == "10":
                cmd_update_metadata_multiple_repos_specific_data(mongo_uri, db_name, storage_manager)
            elif choice == "11":
                cmd_run_tests()
            elif choice == "12":
                cmd_start_chat()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("[!] Invalid choice.")
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt detected. Stopping all processes...")
    finally:
        cmd_stop_local_server()  # Ensure the server stops before exit

# def cmd_configure_llm(current_llm: ILLM) -> ILLM:
#     """
#     Configures the LLM model, using environment variables if available.
#     """
#     print("\nChoose a model backend:")
#     print("1) Local LLM (dummy or local model)")
#     print("2) OpenAI GPT-3.5 or GPT-4 (API)")

#     choice = os.getenv("LLM_MODEL_CHOICE", input("Model choice: ").strip())

#     if choice == "1":
#         model_path = os.getenv("LLM_LOCAL_PATH", input("Enter local model path (dummy for now): ").strip())
#         new_llm = LLMManager.load_llm("local", {"model_path": model_path})
#         print("[LLM] Switched to local model.")
#         return new_llm
#     elif choice == "2":
#         api_key = os.getenv("OPENAI_API_KEY", input("Enter OpenAI API Key: ").strip())
#         model_name = os.getenv("OPENAI_MODEL_NAME", input("Enter model name (e.g. gpt-3.5-turbo): ").strip())
#         new_llm = LLMManager.load_llm("openai", {"api_key": api_key, "model_name": model_name})
#         print("[LLM] Switched to OpenAI model.")
#         return new_llm
#     else:
#         print("Invalid choice, keeping current LLM.")
#         return current_llm


def cmd_list_github_repos(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Lists GitHub repositories, using the token from `.env` if available.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    repos = collector.fetch_repositories()

    if repos:
        print(f"\n Retrieved {len(repos)} repositories for '{org}':")
        for r in repos:
            print(" -", r)
    else:
        print(f"\n No repositories found for '{org}' or an error occurred.")


def cmd_update_org_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates all repositories of a given GitHub organization.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"Updating all repositories in {org}...")
    collector.update_all_repos()
    print("Organization data update complete.")

def cmd_update_repos_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates all selected repositories from a given GitHub organization.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"Updating selected repositories: {repos}")
    collector.update_selected_repos(repos)
    print("Repository data update complete.")

def cmd_update_multiple_repos_specific_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates selected data types for multiple repositories.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()
        
    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    options = {
        "1": "repository info",
        "2": "commits",
        "3": "pull requests",
        "4": "issues"
    }

    print("\nSelect the data to update:")
    for key, value in options.items():
        print(f"{key}) {value}")

    choices = input("Enter numbers separated by spaces (e.g., '1 3'): ").split()
    selected_data = [options[choice] for choice in choices if choice in options]

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"Updating {selected_data} for repositories: {repos}")
    collector.update_multiple_repos_specific_data(repos, selected_data)
    print("Data update complete.")

def cmd_update_metadata_multiple_repos_specific_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates metadata for a specified repository and collections.
    Uses `.env` variables when available.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()
        
    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    options = {
        "1": "files",
        "2": "main_files",
        "3": "last_release_files",
        "4": "commits",
        "5": "pull_requests",
        "6": "issues"
    }

    print("\nSelect the data to update:")
    for key, value in options.items():
        print(f"{key}) {value}")

    choices = input("Enter numbers separated by spaces (e.g., '1 3'): ").split()
    selected_data = [options[choice] for choice in choices if choice in options]

    db_manager = DatabaseManager(mongo_uri, db_name)
    metadata_manager = MetadataManager(db_manager, storage_manager)
    metadata_manager.update_metadata_multiple_repos_specific_data(repos, selected_data)

def cmd_list_collections(mongo_uri: str, db_name: str):
    """
    Lists all collections in the database.
    """
    db_manager = DatabaseManager(mongo_uri, db_name, create_indexes=False)
    cols = db_manager.list_collections()

    print("\nCollections in the DB:")
    for c in cols:
        print(" -", c)

def cmd_start_local_server():
    """
    Starts the local storage server in a separate process so it doesn't block the main script.
    Uses `.env` values when available.
    """
    global server_process

    if server_process and server_process.is_alive():
        print("Local storage server is already running.")
        return
    
    # Retrieve port from .env, ensuring it is a valid integer
    port_env = os.getenv("PORT")
    port = None

    if port_env and port_env.isdigit():
        port = int(port_env)
    
    # Ask user only if PORT was not found in .env or is invalid
    if port is None:
        port_input = input("Port to serve on (default: 8000): ").strip()
        if not port_input or not port_input.isdigit(): 
            port = 8000
            print("Invalid port. So default port 8000 applied.")

    storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("LOCAL_STORAGE_PATH", "local_storage"))

    print(f"\nStarting local storage server on port {port}, serving '{storage_path}' ...")
    print("Server logs are being saved to 'local_server.log'. You can check logs anytime.")

    # Start server process without passing the log file
    server_process = multiprocessing.Process(target=start_server_process, args=(port, storage_path))
    server_process.start()
    
    print("[OK] Local storage server started in the background.")

def start_server_process(port, storage_directory):
    """
    Function to start the local storage server in a separate process and redirect logs.
    """
    log_file_path = "local_server.log"
    with open(log_file_path, "a", buffering=1) as log_file:
        sys.stdout = log_file  # Redirect standard output
        sys.stderr = log_file  # Redirect error output

        print(f"[LocalStorageServer] Starting server on port {port}, serving '{storage_directory}'")

        server = LocalStorageServer(port=port, storage_directory=storage_directory)
        server.start_server()

def cmd_stop_local_server():
    """
    Stops the local storage server if it is running.
    """
    global server_process

    if server_process and server_process.is_alive():
        print("Stopping local storage server...")
        server_process.terminate()
        server_process.join()
        server_process = None
        print("[OK] Local storage server stopped.")
    else:
        print("No active local storage server to stop.")

def cmd_view_local_server_logs():
    """
    Displays the last few lines of the local storage server log file.
    """
    log_file_path = "local_server.log"

    if not os.path.exists(log_file_path):
        print("No log file found. The server may not have been started yet.")
        return

    print("\nLast 10 lines of 'local_server.log':\n")
    
    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()
        for line in lines[-10:]:  # Show last 10 lines
            print(line.strip())

    print("\n(Use 'tail -f local_server.log' in a terminal to follow logs in real-time.)")

def cmd_run_tests():
    """
    Runs unit tests.
    """
    print("\nRunning unit tests...")
    os.system("pytest archethic_rag/tests")

# def cmd_start_chat(llm: ILLM):
def cmd_start_chat(llm):
    """
    Starts a simple chat with the chosen LLM. 
    (We store interactions in logs if desired).
    """
    print("\n[Chat] Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting chat.")
            break

        # Optionally we could pass context from RAG retrieval, etc.
        answer = llm.chat(user_input, context=None)
        print("Bot:", answer)

# def cmd_analyze_logs(llm: ILLM):
def cmd_analyze_logs(llm):
    """
    Example usage of the LLM to analyze logs and propose improvements.
    """
    # For the demo, let's just ask the user for some logs:
    logs = []
    print("\nEnter lines of logs (type 'done' to finish):")
    while True:
        line = input("> ")
        if line.strip().lower() == "done":
            break
        logs.append(line)
    
    if not logs:
        print("No logs provided.")
        return

    analysis = llm.analyze_logs(logs)
    print("\n[Analysis Result]\n", analysis)

def main():
    print("Welcome to the Archethic RAG Interactive System.")
    run_main_loop()

if __name__ == "__main__":
    main()
