import json
from pathlib import Path
import os

class ProjectManager:

    def __init__(self, project_path: str):
        super().__init__()

        self.project_path = Path(project_path)
        self.dataset = {}
        self.preprocessing = {}
        # Load the project.
        self.load_project()


    def save_project(self):

        save_data = {
            "version": "1.0",
            "datasets": self.dataset,
            "preprocessing": self.preprocessing
        }

        try:
            with open(self.project_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            return True

        except Exception as e:
            print(f"Saving Error: {e}")
            return False


    def save_dataset(self, datasets: dict):
        self.dataset.clear()
        self.dataset.update(datasets)
        self.save_project()


    def save_preprocessing(self, preprocessing: dict):
        self.preprocessing.clear()
        self.preprocessing.update(preprocessing)
        self.save_project()


    def load_project(self):

        try:
            with open(self.project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.dataset.clear()
            self.dataset.update(data.get("datasets", {}))

            self.preprocessing.clear()
            self.preprocessing.update(data.get("preprocessing", {}))

        except Exception as e:
            print(f"Loading error: {e}")


    def get_dataset(self):
        return self.dataset


    def get_preprocessing(self):
        return self.preprocessing