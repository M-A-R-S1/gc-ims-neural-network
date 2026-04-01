import json
import os

class ProjectManager:
    @staticmethod
    def save_project(file_path, datasets, preprocessing_settings):
        """Sammelt alle Puzzleteile und schreibt sie in die Datei."""
        save_data = {
            "version": "1.0",
            "datasets": datasets,
            "preprocessing": preprocessing_settings
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            return True

        except Exception as e:
            print(f"Saving Error: {e}")
            return False

    @staticmethod
    def load_project(file_path):
        """Liest die Datei und gibt die Teile strukturiert zurück."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Ladefehler: {e}")
            return None