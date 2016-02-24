import os
from functools import wraps

def pack(f):
    @wraps(f)
    def wrapper(model, output_path):
        '''makes a path with all directories added to form
           user defined package structure'''

        if model.package is not None:
            packages = model.package.name.split('.')
            for package in packages:
                path = os.path.join(output_path, package)
        else:
            path = output_path

        os.makedirs(path, exist_ok=True)
        generator = f(model, path)

        return generator

    return wrapper


def package_path_for_template(full_path):
    index = full_path.index(os.path.sep) + 1
    package_path = full_path[index:]
    return package_path.replace(os.path.sep, '.')