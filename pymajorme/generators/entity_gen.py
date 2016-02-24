import os
import pymajorme_config
import jinja2
import helpers.javatype as javatype
import datetime
from helpers.pack import pack
from helpers.pack import package_path_for_template

TEMPLATE_NAME = 'entity.template'
imports = []


def initialize_imports():
    imports.clear()
    imports.append('java.io.Serializable')
    imports.append('javax.persistence.Entity')
    imports.append('javax.persistence.Table')
    imports.append('javax.persistence.Column')
    imports.append('javax.persistence.JoinColumn')


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
            add_import('javax.persistence.' + filter_relation_name(r.relation_type, False))
            add_relation_imports(r.destination)
            if filter_relation_name(r.relation_type, False) == 'OneToMany' or filter_relation_name(r.relation_type, False) == 'ManyToMany':
                add_import('java.util.Set')
                add_import('java.util.HashSet')

        if r.destination.type.name == entity.name:
            add_import('javax.persistence.' + filter_relation_name(r.relation_type, True))
            add_relation_imports(r.source)
            if filter_relation_name(r.relation_type, False) == 'ManyToOne' or filter_relation_name(r.relation_type, False) == 'ManyToMany':
                add_import('java.util.Set')
                add_import('java.util.HashSet')

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


def filter_collection_generic(collection_value):
    collection_map = {'list': 'List',
                      'set': 'Set'}
    return collection_map.get(collection_value, 'Set')


def filter_collection_concrete(collection_value):
    collection_map = {'list': 'ArrayList',
                      'set': 'HashSet'}
    return collection_map.get(collection_value, 'HashSet')


def filter_relation_symbol(relation_type, flip=False):
    src_max = relation_type.src_max_cardinality
    dst_max = relation_type.dst_max_cardinality

    if src_max == '1' and dst_max == '1':
        relation_symbol = '--'
    elif src_max == '1' and dst_max == 'N':
        relation_symbol = '->' if not flip else '<-'
    elif src_max == 'N' and dst_max == '1':
        relation_symbol = '<-' if not flip else '->'
    elif src_max == 'N' and dst_max == 'N':
        relation_symbol = '<->'
    else:
        relation_symbol = '--'

    return relation_symbol


def filter_relation_name(relation_type, flip):
    relation_symbol = filter_relation_symbol(relation_type, flip)
    relation_names = {'--': 'OneToOne',
                      '->': 'OneToMany',
                      '<-': 'ManyToOne',
                      '<->': 'ManyToMany'}
    return relation_names[relation_symbol]


def filter_relation_attribute(relation_side, relation_type, flip):
    relation_symbol = filter_relation_symbol(relation_type, flip)
    relation_attributes = {'--': single(relation_side),
                           '->': single(relation_side),
                           '<-': collection(relation_side),
                           '<->': collection(relation_side)}
    return relation_attributes[relation_symbol]


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


def capitalize(s):
    return s[0].upper() + s[1:]


def decapitalize(s):
    return s[0].lower() + s[1:]


def singularize(s):
    return s[:-1]


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
    jinja_env.filters['relation_name'] = filter_relation_name
    jinja_env.filters['source'] = lambda relations, entity: [r for r in relations if entity.name == r.source.type.name]
    jinja_env.filters['destination'] = lambda relations, entity: [r for r in relations if entity.name == r.destination.type.name]
    jinja_env.filters['relation_attribute'] = filter_relation_attribute
    jinja_env.filters['capitalize'] = capitalize
    jinja_env.filters['decapitalize'] = decapitalize
    jinja_env.filters['singularize'] = singularize

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
                                    'package': package_path_for_template(package_path),
                                    'imports': imports})

        # For each entity generate java file
        with open(os.path.join(package_path, '{}.java'.format(entity.name)), 'w') as f:
            f.write(rendered)
