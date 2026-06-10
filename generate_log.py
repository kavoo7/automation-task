import argparse
import json
import os
from datetime import datetime
import requests
from rich.console import Console
from rich.table import Table

# Initialize rich console for professional terminal output
console = Console()


class Task:
    """Models a single task item."""
    def __init__(self, task_id, title, completed=False):
        self.id = task_id
        self.title = title
        self.completed = completed

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed}


class UserAccount:
    """Manages the user's tasks, files, and external API requests."""
    def __init__(self, username="default_user"):
        self.username = username
        self.tasks = []
        self.state_file = f"{self.username}_tasks.json"
        self.load_state()

    def add_task(self, title):
        task_id = len(self.tasks) + 1
        new_task = Task(task_id, title)
        self.tasks.append(new_task)
        console.print(f"[green]✓[/green] Task added successfully: '[bold]{title}[/bold]' (ID: {task_id})")
        self._write_to_log(f"Added task: '{title}' (ID: {task_id})")
        self.save_state()

    def complete_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                if task.completed:
                    console.print(f"[yellow]![/yellow] Task ID {task_id} is already complete.")
                    return

                task.completed = True
                console.print(f"[green]✓[/green] Task ID {task_id} ('{task.title}') marked as [bold]Complete[/bold]!")
                self._write_to_log(f"Completed task ID: {task_id}")
                self.save_state()
                return

        console.print(f"[red]✗[/red] Error: Task ID {task_id} not found.", style="bold red")

    def fetch_external_task(self):
        console.print("[yellow]Fetching data from external API...[/yellow]")
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

            if response.status_code == 200:
                post_data = response.json()
                api_title = post_data.get("title", "Untitled External Task")
                formatted_title = f"API Sync: {api_title.title()}"
                console.print(f"[green]✓[/green] Successfully fetched post title.")
                self.add_task(formatted_title)
            else:
                console.print(f"[red]✗[/red] Failed to fetch API data. Status: {response.status_code}")
        except requests.RequestException as e:
            console.print(f"[red]✗[/red] API Connection Error: {e}")

    def display_tasks(self):
        if not self.tasks:
            console.print(f"[yellow]No tasks found for user '{self.username}'.[/yellow]")
            return

        table = Table(title=f"Task Manager - Account: {self.username}")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Task Title", style="magenta")
        table.add_column("Status", justify="center")
        for task in self.tasks:
            status = "[green]Complete[/green]" if task.completed else "[bold yellow]Pending[/bold yellow]"
            table.add_row(str(task.id), task.title, status)
        console.print(table)

    def _write_to_log(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datestamp = datetime.now().strftime("%Y%m%d")
        filename = f"log_{datestamp}.txt"
        try:
            with open(filename, "a") as file:
                file.write(f"[{timestamp}] {action}\n")
        except IOError:
            pass

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=4)

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.tasks = [Task(t['id'], t['title'], t['completed']) for t in data]
            except:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lightweight Automation CLI Tool")
    parser.add_argument("--user", default="default_user")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-task")
    add_parser.add_argument("title", type=str)

    complete_parser = subparsers.add_parser("complete-task")
    complete_parser.add_argument("id", type=int)

    subparsers.add_parser("show")
    subparsers.add_parser("sync")

    args = parser.parse_args()
    user_account = UserAccount(username=args.user)

    if args.command == "add-task":
        user_account.add_task(args.title)
    elif args.command == "complete-task":
        user_account.complete_task(args.id)
    elif args.command == "show":
        user_account.display_tasks()
    elif args.command == "sync":
        user_account.fetch_external_task()
