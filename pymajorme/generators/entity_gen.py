import os
import pymajorme_config
import jinja2
import helpers.javatype as javatype
import datetime
from helpers.pack import pack

TEMPLATE_NAME = 'entity.template'
imports = []


def initialize_imports():
    imports.clear()
    imports.append('java.io.Serializable')
    imports.append('javax.persistence.Entity')
    imports.append('javax.persistence.Table')
    imports.append('javax.persistence.Column')


def add_import(value):
    if not imports.__contains__(value):
        imports.append(value)


def relation_based_imports(relations, entity):

    def add_relation_imports(relation_side):
        if hasattr(relation_side, 'collection') and relation_side.collection is not None:
            add_import('java.util.{}'.format(filter_collection_generic(relation_side.collection)))
            add_import('java.util.{}'.format(filter_collection_concrete(relation_side.collection)))
        if hasattr(relation_side, 'fk_column_parameters'):
            for param in relation_side.fk_column_parameters:
                # cascade
                if param.name == 'cascade':
                    for cascade in param.values:
                        add_import('static javax.persistence.CascadeType.{}'.format(cascade))
                # fetch
                if param.name == 'fetch':
                    add_import('static javax.persistence.FetchType.{}'.format(param.value))

    for r in relations:
        if r.source.type.name == entity.name:
            add_import('javax.persistence.' + filter_source_types(r.relation_type))
            add_relation_imports(r.destination)
        if r.destination.type.name == entity.name:
            add_import('javax.persistence.' + filter_destination_types(r.relation_type))
            add_relation_imports(r.source)


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
    return collection_map.get(collection, collection)


def filter_collection_concrete(collection):
    collection_map = {'list': 'ArrayList',
                      'set': 'HashSet',
                      'map': 'HashMap'}
    return collection_map.get(collection, collection)


def filter_source_types(relation_type):
    relation_types = {'->': 'OneToMany',
                      '<->': 'ManyToMany',
                      '--': 'OneToOne'}
    return relation_types[relation_type]


def filter_destination_types(relation_type):
    relation_types = {'->': 'ManyToOne',
                      '<->': 'ManyToMany',
                      '--': 'OneToOne'}
    return relation_types[relation_type]


def filter_source_attribute(relation_side, relation_type):
    name = relation_side.type.name if relation_side.name == '' else relation_side.name
    relation_types = {'->': collection(relation_side),
                      '<->': collection(relation_side),
                      '--': single(relation_side)}
    return relation_types[relation_type]


def filter_destination_attribute(relation_side, relation_type):
    relation_types = {'->': single(relation_side),
                      '<->': collection(relation_side),
                      '--': single(relation_side)}
    return relation_types[relation_type]


def single(relation_side):
    name = relation_side.type.name if relation_side.name == '' else relation_side.name
    return relation_side.type.name + ' ' + decapitalize(name)


def collection(relation_side):
    if relation_side.name == '':
        name = relation_side.type.name + 's'
    else:
        name = relation_side.name
    clctn = 'set'
    if relation_side.collection is not None:
        clctn = relation_side.collection
    return '{0}<{2}> {3} = new {1}<{2}>()'.format(filter_collection_generic(clctn), filter_collection_concrete(clctn),
            relation_side.type.name, decapitalize(name))


def decapitalize(s):
    return s[0].lower() + s[1:]

@pack
def generate(model, package_path):

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
    jinja_env.filters['source'] = lambda relations, entity: [r for r in relations if entity.name == r.source.type.name]
    jinja_env.filters['destination'] = lambda relations, entity: [r for r in relations if entity.name == r.destination.type.name]
    jinja_env.filters['source_attribute'] = filter_source_attribute
    jinja_env.filters['destination_attribute'] = filter_destination_attribute
    jinja_env.filters['decapitalize'] = decapitalize

    # Load Java template
    template = jinja_env.get_template(TEMPLATE_NAME)

    # Create entity directory
    package_path = os.path.join(package_path, 'entity')
    if not os.path.exists(package_path):
        os.mkdir(package_path)

    date = datetime.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')

    for entity in entities:

        relations = model.relations

        # clear, initialize and resolve relation based imports
        initialize_imports()
        relation_based_imports(relations, entity)

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
