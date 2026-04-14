import json
from pathlib import Path

class ProjectManager:

    def __init__(self, project_path: str):
        super().__init__()

        self.project_path = Path(project_path)
        # Dictionaries for dataset and preprocessing.
        self.dataset = {}
        self.preprocessing = {}

        # Load the project.
        self.load_project()


    def save_project(self) -> None:
        """
        This function takes care of saving the project data to the .gcimsp file.
        =============================================================================
        :return: None.
        """

        # Setup the dictionary which will be saved.
        save_data = {
            "version": "1.0",
            "datasets": self.dataset,
            "preprocessing": self.preprocessing
        }

        # Try to save the project.
        try:
            with open(self.project_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)

        except Exception as e:
            print(f"Saving Error: {e}")


    def save_dataset(self,
                     dataset: dict) -> None:
        """
        This function updates the dataset dictionary and calls the save project function.
        =============================================================================
        :param dataset: The new dataset which should be saved.
        :return: None.
        """

        # Clear the old dataset state and update it with the new one.
        self.dataset.clear()
        self.dataset.update(dataset)
        self.save_project()


    def save_preprocessing(self, preprocessing: dict):
        """
        This function updates the preprocessing dictionary and calls the save project function.
        =============================================================================
        :param preprocessing: The new preprocessing region of interest values which should be saved.
        :return: None.
        """

        # Clear the old preprocessing data and update it with the new one.
        self.preprocessing.clear()
        self.preprocessing.update(preprocessing)
        self.save_project()


    def load_project(self) -> None:
        """
        This function loads the project file and saves the dataset and preprocessing data into dictionaries.
        =============================================================================
        :return: None.
        """

        # Try to load the project file.
        try:
            with open(self.project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear the dataset dictionary and load the new data.
            self.dataset.clear()
            self.dataset.update(data.get("datasets", {}))
            # Clear the preprocessing dictionary and load the new data.
            self.preprocessing.clear()
            self.preprocessing.update(data.get("preprocessing", {}))

        except Exception as e:
            print(f"Loading error: {e}")


    def get_dataset(self) -> dict:
        """
        Returns the dataset dictionary.
        =============================================================================
        :return: Dictionary of the dataset.
        """

        return self.dataset


    def get_preprocessing(self) -> dict:
        """
        Returns the preprocessing dictionary.
        =============================================================================
        :return: Dictionary of the preprocessing region of interest values.
        """

        return self.preprocessing