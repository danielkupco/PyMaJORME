import os
import click
import pymajorme_config
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
import helpers.javatype as javatype
import generators.entity_gen as entity_gen
import generators.dao_gen as dao_gen
import generators.persistence_xml_gen as persistence_xml


@click.command()
@click.option('-e', '--entity', is_flag=True, help='Generate entity classes')
@click.option('-d', '--dao', is_flag=True, help='Generate Dao layer')
@click.option('-p', '--persistence', is_flag=True, help='Generate persistence.xml file')
@click.option('-a', '--all', 'all_above', is_flag=True, help='Generate all previous')     # apparently, "all" is reserved keyword in Python
@click.argument('source', nargs=1, type=click.Path(exists=True))
@click.argument('output_path', nargs=1, type=click.Path(exists=True))
def cli(entity, dao, persistence, all_above, source, output_path):
    current_dir = os.getcwd()
    gen_dir = os.path.join(current_dir, pymajorme_config.GEN_DIR)


    # Create output folder
    if not os.path.exists(pymajorme_config.GEN_DIR):
        os.mkdir(pymajorme_config.GEN_DIR)

    model = load_model(click.format_filename(source))

    # Create package structure
    # current_path = gen_dir
    packages = model.package.name.split('.')
    for package in packages:
        class_path = os.path.join(output_path, package)

    # kreiraju se folderi samo ako ne postoje
    os.makedirs(output_path, exist_ok=True)

    # passing model to specific generators
    if entity:
        entity_gen.generate(model, click.format_filename(class_path))
    elif dao:
        dao_gen.generate(model, click.format_filename(class_path))
    elif persistence:
        persistence_xml.generate(model, click.format_filename(os.path.join(output_path, packages[0])))
    elif all_above:
        entity_gen.generate(model, click.format_filename(class_path))
        dao_gen.generate(model, click.format_filename(class_path))
        persistence_xml.generate(model, click.format_filename(os.path.join(output_path, packages[0])))
        

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

    model = jorm_mm.model_from_file(os.path.join(current_dir, file_name))
 
    model_export(model, os.path.join(visualization_dir, 'jorm_model.dot'))

    return model

def prepare():
    current_dir = os.getcwd()
    gen_dir = os.path.join(current_dir, pymajorme_config.GEN_DIR)


    # Create output folder
    if not os.path.exists(pymajorme_config.GEN_DIR):
        os.mkdir(pymajorme_config.GEN_DIR)

    model = load_model('entities.jorm')

    # Create package structure
    current_path = gen_dir
    packages = model.package.name.split('.')
    for package in packages:
        current_path = os.path.join(current_path, package)

    # kreiraju se folderi samo ako ne postoje
    os.makedirs(current_path, exist_ok=True)


if __name__ == '__main__':
    cli()
