from ctfsolver.managers.manager_folder import ManagerFolder
from ctfsolver.error.manager_error import ManagerError


def find_usage():
    """
    Searches for the usage of a specific import statement within the project files.
    This function initializes folder and error managers, then searches for files containing
    the specified import statement, excluding certain directories. Results are displayed.
    Args:
        None
    Returns:
        None
    Raises:
        Any exceptions raised by `ManagerFolder.search_files` are handled by `ManagerError.try_function`.

    """
    solver = ManagerFolder()
    handler = ManagerError()

    search_string = "from ctfsolver import CTFSolver"
    exclude_dirs = ["app_venv", ".git"]
    current_directory = "."

    handler.try_function(
        function=solver.search_files,
        directory=current_directory,
        exclude_dirs=exclude_dirs,
        search_string=search_string,
        display=True,
    )


if __name__ == "__main__":
    find_usage()
