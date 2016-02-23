import os
import jinja2
import helpers.javatype as javatype
import datetime
import pymajorme_config
import hashlib 

TEMPLATE_NAME = 'sql.template'


def filter_sql_type(attribute_type):
    sql_types = { 'Integer' : 'INT',
                  'String'  : 'VARCHAR',
                }

    return sql_types[attribute_type]

def filter_tuple(attribute):
    return attribute.name + ' ' + filter_sql_type(attribute.type.name)

def filter_primary_keys(attributes):
    return [a.name for a in attributes for c in a.column_parameters if c.name == 'GUID']

def generate(model, output_path):

    entities = model.entities
    relations = model.relations

    # Initialize template engine.
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,        
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 
                pymajorme_config.TEMPLATES_DIR))))

    jinja_env.filters['sql_type'] = filter_sql_type
    jinja_env.filters['tuple'] = filter_tuple
    jinja_env.filters['primary_keys'] = filter_primary_keys

    # Load SQL template
    template = jinja_env.get_template(TEMPLATE_NAME)

    date = datetime.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')

    rendered = template.render({ 'entities' : entities,
                                 'relations': relations,
                                 'date'     : date,
                                 'constraints': constraint_names(entities, relations)
                              })

    with(open(os.path.join(output_path, 'initDB.sql'), 'w')) as f:
        f.write(rendered)

def constraint_names(entities, relations):
    primary_keys = ['PK' + hashlib.md5(bytes(e.name, 'utf-8')).hexdigest().upper() for e in entities]

    return dict(zip(entities, primary_keys))

