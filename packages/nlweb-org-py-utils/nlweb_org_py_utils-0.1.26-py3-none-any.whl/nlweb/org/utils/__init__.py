class LOADER:

    @classmethod
    def AppendFolderToPath(cls, folder:str):
        '''👉️ Appends a folder to the system path.'''
        import sys
        from pathlib import Path

        # Path to the folder containing this __init__.py
        current_dir = Path(__file__).resolve().parent

        # Path to the 'tests' folder (child folder)
        folder_dir = current_dir / folder

        # Add to sys.path if not already there
        if str(folder_dir) not in sys.path:
            sys.path.append(str(folder_dir))


    @classmethod
    def LoadImports(cls):
        '''👉 Loads the imports.'''
        cls.AppendFolderToPath('init')
        from IMPORTS import IMPORTS 
        

LOADER.LoadImports()