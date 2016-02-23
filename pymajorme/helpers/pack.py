import os
from functools import wraps

def pack(f):
    @wraps(f)
    def wrapper(model, output_path):
        '''makes a path with all directories added to form
           user defined package structure'''
 
        packages = model.package.name.split('.')
        for package in packages:
            path = os.path.join(output_path, package)
 
        os.makedirs(path, exist_ok=True)
        generator = f(model, path)

        return generator

    return wrapper
