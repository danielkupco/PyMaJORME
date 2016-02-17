import os
import pymajorme_config
import jinja2
import helpers.javatype as javatype
import datetime

TEMPLATE_NAME = 'entity.template'
imports = []


def add_import(value):
    if not imports.__contains__(value):
        imports.append(value)


def filter_javatype(s):
        '''
        Maps type names from model to Java.
        '''
        if isinstance(s, javatype.JavaType):
            s = s.name

        return {
                'integer': 'Integer',
                'string': 'String'
        }.get(s, s)

def filter_collection_generic(collection):
    collection_map = {'list': 'List',
                      'set': 'Set',
                      'map': 'Map'}
    add_import('java.util.' + collection_map.get(collection, collection))
    return collection_map.get(collection, collection)

def filter_collection_concrete(collection):
    collection_map = {'list': 'ArrayList',
                      'set': 'HashSet',
                      'map': 'HashMap'}
    add_import('java.util.' + collection_map.get(collection, collection))
    return collection_map.get(collection, collection)

def filter_source_types(relation_type):
    relation_types = {'->' : 'OneToMany',
                      '<->': 'ManyToMany',
                      '--' : 'OneToOne'}

    add_import('javax.persistence.' + relation_types[relation_type])
    return relation_types[relation_type]

def filter_destination_types(relation_type):
    relation_types = {'->' : 'ManyToOne',
                      '<->': 'ManyToMany',
                      '--' : 'OneToOne'}

    add_import('javax.persistence.' + relation_types[relation_type])
    return relation_types[relation_type]

def filter_source_attribute(name, relation_type):
    relation_types = {'->' : collection(name),
                      '<->': collection(name),
                      '--' : single(name)}

    return relation_types[relation_type]

def filter_destination_attribute(name, relation_type):
    relation_types = {'->' : single(name),
                      '<->': collection(name),
                      '--' : single(name)}

    return relation_types[relation_type]

def single(name):
    decapitalize = lambda s: s[0].lower() + s[1:]
    return name + ' ' + decapitalize(name)

def collection(name):
    decapitalize = lambda s: s[0].lower() + s[1:]
    return 'List<' + name + '> ' + decapitalize(name) + 's'  

def generate(model, package_path):

    imports.append('java.io.Serializable')
    imports.append('javax.persistence.Entity')
    imports.append('javax.persistence.Table')
    imports.append('javax.persistence.Column')

    entities = model.entities

    # Initialize template engine.
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                pymajorme_config.TEMPLATES_DIR))))

    # Register filter for mapping Entity type names to Java type names.
    jinja_env.filters['javatype'] = filter_javatype
    jinja_env.filters['collectionGeneric'] = filter_collection_generic
    jinja_env.filters['collectionConcrete'] = filter_collection_concrete
    jinja_env.filters['source_types'] = filter_source_types
    jinja_env.filters['destination_types'] = filter_destination_types
    jinja_env.filters['source'] = lambda relations, entity: [r for r in relations if entity.name == r.source.name]
    jinja_env.filters['destination'] = lambda relations, entity: [r for r in relations if entity.name == r.destination.name]
    jinja_env.filters['source_attribute'] = filter_source_attribute
    jinja_env.filters['destination_attribute'] = filter_destination_attribute

    # Load Java template
    template = jinja_env.get_template(TEMPLATE_NAME)

    # Create entity directory
    package_path = os.path.join(package_path, 'entity')
    if not os.path.exists(package_path):
        os.mkdir(package_path)

    date = datetime.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')

    for entity in entities:

        relations = model.relations

        source_filter = lambda entity_name, r: entity_name == r.source.name
        destination_filter = lambda entity_name, r: entity_name == r.destination.name

        for attr in entity.attributes:
            if hasattr(attr, 'column_parameters'):
                for prm in attr.column_parameters:
                    if prm.name == 'GUID':
                        add_import('javax.persistence.Id')
                        add_import('javax.persistence.GeneratedValue')
                        add_import('static javax.persistence.GenerationType.IDENTITY')

        rendered = template.render({'entity': entity,
                                    'relations': relations,
                                    'date': date,
                                    'package': model.package.name,
                                    'imports': imports})

        # For each entity generate java file
        with open(os.path.join(package_path, '{}.java'.format(entity.name)), 'w') as f:
            f.write(rendered)
