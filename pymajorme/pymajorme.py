import os
import click
import pymajorme_config
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
import helpers.javatype as javatype
import generators.entity_gen as entity_gen
import generators.dao_gen as dao_gen
import generators.persistence_xml_gen as persistence_xml
import generators.sql_gen as sql_gen

@click.command()
@click.option('-e', '--entity', is_flag=True, help='Generate entity classes')
@click.option('-d', '--dao', is_flag=True, help='Generate Dao layer')
@click.option('-p', '--persistence', is_flag=True, help='Generate persistence.xml file')
@click.option('-s', '--sql', is_flag=True, help='Generate SQL script')
@click.option('-a', '--all', 'all_above', is_flag=True, help='Generate all previous')     # apparently, "all" is reserved keyword in Python
@click.option('-r', '--root', is_flag=True, help='Make a root directory for generated code')
@click.argument('source', nargs=1, type=click.Path(exists=True))
@click.argument('output_path', nargs=1, type=click.Path(exists=True))
def cli(entity, dao, persistence, sql, all_above, root, source, output_path):

    model = load_model(click.format_filename(source))

    if root:
        output_path = packaging(output_path, model)

    # passing model to specific generators
    if entity:
        entity_gen.generate(model, output_path)
    elif dao:
        dao_gen.generate(model, output_path)
    elif persistence:
        persistence_xml.generate(model, output_path)
    elif sql:
        sql_gen.generate(model, output_path)
    elif all_above:
        entity_gen.generate(model, output_path)
        dao_gen.generate(model, output_path)
        persistence_xml.generate(model, output_path)
        sql_gen.generate(model, output_path)

def load_model(file_name):
    """Generates program model from '/examples' and returns it."""

    # current_dir = os.path.dirname(__file__)
    # __file__ is unbound in interactive mode

    current_dir = os.path.dirname(os.path.realpath(__file__)) 
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

if __name__ == '__main__':
    cli()
