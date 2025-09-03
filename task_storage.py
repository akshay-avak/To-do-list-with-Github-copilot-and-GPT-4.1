import json
import os

class TaskStorage:
    def __init__(self, filename="tasks.json"):
        # Always use the directory of this script for the tasks.json file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_tasks(self):
        self._ensure_file()
        with open(self.filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def save_tasks(self, tasks):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, task_dict):
        tasks = self.load_tasks()
        tasks.append(task_dict)
        self.save_tasks(tasks)

    def update_task(self, idx, task_dict):
        tasks = self.load_tasks()
        if 0 <= idx < len(tasks):
            tasks[idx] = task_dict
            self.save_tasks(tasks)

    def delete_task(self, idx):
        tasks = self.load_tasks()
        if 0 <= idx < len(tasks):
            del tasks[idx]
            self.save_tasks(tasks)
