
def main():
    print("Hello, world!")

def main():
    cli_arguments()
    """Entry point of the program.

    Calls the cli_arguments() function to process user input.
    """

"""
Tasklist Simple — A command-line task manager tool.

Developed by Barbara Hanna Silva dos Santos for the CSD110 – Introduction to Programming course at Sault College.

This program allows users to manage tasks via terminal commands or an interactive menu.
Features include adding, completing, removing, viewing, and clearing tasks.
Tasks are stored persistently in a text file (tasks.txt).

"""

import os           # Interacts with the operating system (files, directories)
import sys          # Controls program flow (exit, version info)
import argparse     # Parses command-line arguments

VERSION = "1.0"
TASKS_FILE = "tasks.txt"

# Persistence: Load tasks from file
def load_tasks():
    """Loads tasks from the tasks.txt file.

    Returns:
        list: A list of task strings. If the file does not exist or an error occurs, returns an empty list.
        """
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"⚠️ Error loading tasks: {e}")
        return []

# Persistence: Save tasks to file
def save_tasks(tasks):
    """ Saves the list of tasks to the tasks.txt file.

    Args:
        tasks (list): A list of task strings to be written to the file.
    """
    try:
        with open(TASKS_FILE, "w") as f:
            for task in tasks:
                f.write(task + "\n")
    except Exception as e:
        print(f"⚠️ Error saving tasks: {e}")

# Display: Show tasks in terminal
def show_tasks(tasks):
    """Displays the list of tasks in the terminal.

    Args:
        tasks (list): A list of task strings to be displayed.
    """
    print("\n📂 Your Tasks:")
    if not tasks:
        print("No tasks found.")
    else:
        for i, task in enumerate(tasks):
            print(f"{i+1}. {task}")

# Optional: Interactive menu mode
def menu_mode():
    """Launches the interactive menu mode.

    Allows users to manage tasks through numbered options:
    Add, complete, remove, view tasks, or exit the program.
    """
    tasks = load_tasks()
    while True:
        print("\n📋 Task Manager Menu")
        print("1. Add task")
        print("2. Mark task as completed")
        print("3. Remove task")
        print("4. Show tasks")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            desc = input("Enter task description: ").strip()
            if not desc:
                print("⚠️ Task description cannot be empty.")
            elif any(desc in task for task in tasks):
                print("⚠️ Task already exists.")
            else:
                tasks.append(f"[ ] {desc}")
                save_tasks(tasks)
                print("✅ Task added.")

        elif choice == "2":
            show_tasks(tasks)
            try:
                idx = int(input("Enter task number to mark as completed: ")) - 1
                if 0 <= idx < len(tasks):
                    tasks[idx] = tasks[idx].replace("[ ]", "[✔]")
                    save_tasks(tasks)
                    print("✅ Task marked as completed.")
                else:
                    print("⚠️ Invalid task number.")
            except ValueError:
                print("⚠️ Please enter a valid number.")

        elif choice == "3":
            show_tasks(tasks)
            try:
                idx = int(input("Enter task number to remove: ")) - 1
                if 0 <= idx < len(tasks):
                    removed = tasks.pop(idx)
                    save_tasks(tasks)
                    print(f"❌ Removed: {removed}")
                else:
                    print("⚠️ Invalid task number.")
            except ValueError:
                print("⚠️ Please enter a valid number.")

        elif choice == "4":
            show_tasks(tasks)

        elif choice == "5":
            print("👋 Exiting. See you next time!")
            break

        else:
            print("⚠️ Invalid option. Try again.")

# Main logic: Handle command-line arguments
def cli_arguments():
    """Parses and handles command-line arguments using argparse.

    Supports the following options:
        --add: Add a new task
        --complete: Mark a task as completed
        --remove: Remove a task
        --show: Display all tasks
        --clear: Delete all tasks
        --version: Show program version
        --menu: Launch interactive menu mode
        """
    parser = argparse.ArgumentParser(
        description="📝 Tasklist Simple — Manage your tasks!",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Supported arguments
    parser.add_argument("--add", type=str, help="➕ Add a new task")
    parser.add_argument("--complete", type=int, help="✔️ Mark task as completed by number")
    parser.add_argument("--remove", type=int, help="❌ Remove task by number")
    parser.add_argument("--show", action="store_true", help="📂 Show all tasks")
    parser.add_argument("--clear", action="store_true", help="🧹 Clear all tasks")
    parser.add_argument("--version", action="store_true", help="📦 Show program version")
    parser.add_argument("--menu", action="store_true", help="🎯 Launch the interactive menu")

    args = parser.parse_args()
    tasks = load_tasks()

    # Show version
    if args.version:
        print(f"🛠️ Task Manager v{VERSION} by Bahanna-01")
        sys.exit()

    # Clear all tasks
    if args.clear:
        save_tasks([])
        print("🧹 All tasks cleared.")
        sys.exit()

    # Add a new task
    if args.add:
        desc = args.add.strip()
        if not desc:
            print("⚠️ Task description cannot be empty.")
        elif any(desc in task for task in tasks):
            print("⚠️ Task already exists.")
        else:
            tasks.append(f"[ ] {desc}")
            save_tasks(tasks)
            print("✅ Task added.")

    # Mark task as completed
    if args.complete is not None:
        idx = args.complete - 1
        if 0 <= idx < len(tasks):
            tasks[idx] = tasks[idx].replace("[ ]", "[✔]")
            save_tasks(tasks)
            print("✅ Task marked as completed.")
        else:
            print("⚠️ Invalid task number.")

    # Remove a task
    if args.remove is not None:
        idx = args.remove - 1
        if 0 <= idx < len(tasks):
            removed = tasks.pop(idx)
            save_tasks(tasks)
            print(f"❌ Removed: {removed}")
        else:
            print("⚠️ Invalid task number.")

    # Show all tasks
    if args.show:
        show_tasks(tasks)

    # Launch interactive menu
    if args.menu:
        menu_mode()

    # No arguments provided
    if not any(vars(args).values()):
        print("🚀 No arguments provided. Use --help to see available options.")
        sys.exit()

# Entry point
if __name__ == "__main__":
    cli_arguments()