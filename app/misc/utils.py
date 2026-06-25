import sys
import os
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """
    This function loads ressources from the parent directory of the programm.
    If this code is run from an IDE the path differs from the path used in the final application.
    This function makes sure that the correct path is used.

    :param relative_path: Path to the desired file.

    :return: Corrected path to the desired file.
    """

    try:
        # Try to get the temporary _MEIPASS which was created by the pyinstaller.
        base_path = Path(sys._MEIPASS)
    except Exception:
        # If inside the IDE use this path!
        base_path = Path(os.path.abspath("."))

    return base_path / relative_path