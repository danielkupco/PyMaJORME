class JavaType(object):
    """
    We are registering JavaType class to support
    primitive types (integer, string) in our entity models
    Thus, user does not need to provide integer and string
    JavaType in the model but can reference them in attribute types
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __str__(self):
        return self.name


def get_java_builtins():
    """
    Builds and returns a Java built-in types for language.
    """
    # Built-in primitive types
    # Each model will have this entities during reference resolving but
    # these entities will not be a part of `entities` list of EntityModel.
    java_builtins = {
            'integer': JavaType(None, 'integer'),
            'string': JavaType(None, 'string')
    }

    return java_builtins