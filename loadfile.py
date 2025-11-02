import os

def resource_path(filename):
    return os.path.join(os.path.dirname(__file__), 'resource', filename)