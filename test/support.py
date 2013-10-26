import os
import sys

class ProjectImportManager(object):
    """ContextManager: Allows for imports from the project in tests."""
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.path.remove(self.path)
        if exc_type is not None:
            return False
        return True

def project_imports():
    return ProjectImportManager()
