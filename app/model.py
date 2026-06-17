from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QFont
from ModelWidget import Ui_ModelWidget
from dialogs import CustomYesNoDialog, CustomProgressDialog, RenameLabelDialog, CustomMessageDialog
import sqlite3
from pathlib import Path
import torch
import vae_model
import plot
import re
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


class ModelPage(QtWidgets.QWidget, Ui_ModelWidget):
    def __init__(self, project_path: Path):
        super().__init__()
        self.setupUi(self)

        # Project save path.
        self.project_path = Path(project_path)
        # Database path.
        self.db_path = self.project_path.parent / "database" / "project_database.db"
