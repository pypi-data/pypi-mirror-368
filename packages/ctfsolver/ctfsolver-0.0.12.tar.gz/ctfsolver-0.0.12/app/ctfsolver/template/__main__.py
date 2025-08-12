from pathlib import Path
from ctfsolver.managers.manager_file import ManagerFile


class Templater(ManagerFile):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_attempt = 1
        self.verbose = False

    def find_folder_in_frame(self, folder_name: str) -> Path | None:
        """
        Description:
            Searches for a folder with the specified name within the file paths stored in the `file_called_frame` attribute.
        Args:
            folder_name (str): The name of the folder to search for.
        Returns:
            Path or None: The Path object representing the parent folder if found,
                          otherwise None if no matching folder is found.
        """
        # This function should be added to the manager files
        for i in range(len(self.file_called_frame)):
            file_called_path = Path(self.file_called_frame[i].filename)
            parent = Path(file_called_path).parent
            if parent.name == folder_name:
                return parent
        return None

    def create_attempts(self):
        """
        Description:
            Creates a folder for attempts and initializes it with a solution template.
        """
        self.folder_attempts = Path(self.folder_payloads, "attempts")
        self.folder_attempts.mkdir(parents=True, exist_ok=True)

        # Read the titles of the files inside the folder_attempts
        self.files_attempts = [
            f.name for f in self.folder_attempts.iterdir() if f.is_file()
        ]

        # Cleanup of the file_attempts_names

        self.files_attempts = [
            f.strip(".py").strip("attempt_")
            for f in self.files_attempts
            if f.endswith(".py") and f.startswith("attempt_")
        ]

        self.files_attempts = sorted(map(int, self.files_attempts))

        if len(self.files_attempts) > 0:
            self.next_attempt = max(self.files_attempts) + 1

        # Create the next attempt file
        self.file_attempt = Path(
            self.folder_attempts, f"attempt_{self.next_attempt}.py"
        )

    def main(self):

        # Find the folder that called this script
        parent = self.find_folder_in_frame("template")
        solution = Path(self.folder_payloads, "solution.py")
        if parent is None:
            raise Exception(
                "Could not find the template folder that called this script"
            )

        file = Path(parent, "solution_template.py")
        with open(file, "r") as f:
            template = f.read()

        # with open(Path(self.folder_payloads, "solution.py"), "w") as f:
        #     f.write(template)

        if solution.exists():
            self.create_attempts()
            if self.verbose:
                print(
                    f"Solution file already exists, creating the attempt {self.next_attempt}"
                )
            with open(self.file_attempt, "w") as f:
                with open(solution, "r") as solution_file:
                    content = solution_file.read()
                    f.write(content)
            if self.verbose:
                print(f"Attempt file created: {self.file_attempt}")

        if self.verbose:
            print("Creating the solution file")
        with open(solution, "w") as f:
            f.write(template)


if __name__ == "__main__":
    templater = Templater()
    templater.main()
