import nbformat
from rich import print
from achs_mlops_quality.utils import get_python_notebooks, get_python_scripts


class LibraryChecker:

    def __init__(self, src_path=".", **kwargs):
        self.source_path = src_path
        self._get_files()
        self.issues_detected = 0 
        self.issues_files = []
        self.analized_files = 0

    def _get_files(self) -> None:
        self.notebooks = get_python_notebooks(self.source_path)
        

    def analize_notebooks(self):
        for i, np in enumerate(self.notebooks):
            print(f"Analizando => {np}")
            self.read_notebook_cells(np)
            self.analized_files +=1

    def read_notebook_cells(self, notebook_path: str):
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
            cells = nb.cells
            for i, cell in enumerate(cells):
                if cell["cell_type"] == "code":
                    result, issues = self.check_pip_installs_from_lines(cell["source"])
                    if not result:
                        # print()
                        # print("Se detecto una libreria no fijada !")
                        # print(f"--- Cell {i} ({cell['cell_type']}) ---")
                        # print(issues)
                        self.issues_detected += 1
                        self.issues_files.append(
                            notebook_path
                        )
            
                        
    def check_pip_installs_from_lines(self, content: str):
        OPTIONS_WITH_ARG = [
            "-r",
            "--requirement",
            "-c",
            "--constraint",
            "-f",
            "--find-links",
            "--extra-index-url",
        ]
        lines = content.splitlines()  # convierte el string multilinea a lista de líneas
        violations = []
        check_pass = True

        for line_no, line in enumerate(lines, start=1):
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                continue
            if "pip install" not in line:
                continue

            # Ignorar comentarios en línea
            code_part = line.split("#", 1)[0].strip()
            tokens = code_part.split()

            # Soporte para pip, %pip, !pip
            for i, token in enumerate(tokens):
                if (
                    token in ("pip", "%pip", "!pip")
                    and i + 1 < len(tokens)
                    and tokens[i + 1] == "install"
                ):
                    args = tokens[i + 2 :]
                    packages = []
                    j = 0
                    while j < len(args):
                        token = args[j]
                        if token.startswith("-"):
                            if token in OPTIONS_WITH_ARG:
                                j += 2
                            elif token.startswith("--") and "=" in token:
                                j += 1
                            else:
                                j += 1
                        else:
                            packages.append(token)
                            j += 1
                    for spec in packages:
                        if "=" not in spec:
                            check_pass = False
                            violations.append((line_no, line.strip(), spec))
                    break  # ya procesamos esta línea

        return check_pass, violations
