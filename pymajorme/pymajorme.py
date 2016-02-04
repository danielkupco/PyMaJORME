import os
import pymajorme_config
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
import generators.javatype as javatype
import generators.entity_gen as entity_gen


def load_model(file_name):
    """Generates program model from '/examples' and returns it."""

    # current_dir = os.path.dirname(__file__)
    # __file__ is unbound in interactive mode

    current_dir = os.getcwd()
    visualization_dir = os.path.join(current_dir, pymajorme_config.VISUALIZATION_DIR)
    if not os.path.exists(visualization_dir):
        os.makedirs(visualization_dir)

    # jorm_mm = entity_mm.get_entity_mm()

    jorm_mm = metamodel_from_file(os.path.join(current_dir, 'languages', 'pymajorme_language.tx'),
                                    classes=[javatype.JavaType],  # Register Entity class
                                    builtins=javatype.get_java_builtins(),
                                    debug=False)

    metamodel_export(jorm_mm, os.path.join(visualization_dir, 'jorm_metamodel.dot'))

    model = jorm_mm.model_from_file(os.path.join(current_dir, 'examples',
                                               file_name))
    model_export(model, os.path.join(visualization_dir, 'jorm_model.dot'))

    return model

current_dir = os.getcwd()
gen_dir = os.path.join(current_dir, pymajorme_config.GEN_DIR)

if not os.path.exists(gen_dir):
    os.makedirs(gen_dir)

model = load_model('entities.jorm')
entity_gen.generate(model)


