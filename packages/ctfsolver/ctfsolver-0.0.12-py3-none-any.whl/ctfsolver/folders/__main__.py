from ctfsolver.managers.manager_folder import ManagerFolder


def create_folders():
    """
    Creates the necessary parent folder structure for the application.
    This function initializes a ManagerFolder instance and calls its method to
    create the required parent folder. It is typically used to set up the initial
    directory structure before performing further operations.
    Returns:
        None

    """
    # s = CTFSolver()
    s = ManagerFolder()
    s.create_parent_folder()


if __name__ == "__main__":
    create_folders()
