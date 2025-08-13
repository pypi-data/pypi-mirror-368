import os
from typing import List

"""utils for python and notebooks"""


def get_python_notebooks(path: str) -> List[str]:
    files_to_analyze = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".ipynb"):
                files_to_analyze.append(os.path.join(root, file))

    return files_to_analyze


def get_python_scripts(path: str) -> List[str]:
    files_to_analyze = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                files_to_analyze.append(os.path.join(root, file))

    return files_to_analyze
