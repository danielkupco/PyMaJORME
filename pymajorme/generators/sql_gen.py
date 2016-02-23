import os
import jinja2
import helpers.javatype as javatype
import datetime
import pymajorme_config
import hashlib
from helpers.pack import pack
from helpers.constraints import *

TEMPLATE_NAME = 'sql.template'


def filter_sql_type(attribute_type):
    sql_types = { 'Integer' : 'INT',
                  'String'  : 'VARCHAR',
                }

    return sql_types[attribute_type]

def filter_tuple(attribute):
    return attribute.name + ' ' + filter_sql_type(attribute.type.name) + '(255)'

def filter_primary_keys(attributes, value):
    return [a.name for a in attributes for c in a.column_parameters if c.name == value]

@pack
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
                                 'constraints': constraints(entities, relations)
                              })

    with(open(os.path.join(output_path, 'initDB.sql'), 'w')) as f:
        f.write(rendered)

def encode(name):
    return hashlib.md5(bytes(name, 'utf-8')).hexdigest().upper()

def constraints(entities, relations):
    primary_keys = [(e,'PK' + encode(e.name))  for e in entities]
    foreign_keys = [(e, r, 'FK' + encode(r.source.type.name + r.destination.type.name)) for r in relations 
                    for e in entities if e.name == r.source.type.name or e.name == r.destination.type.name]

    return Constraints(primary_keys, foreign_keys)
 

