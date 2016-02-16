import os
import pymajorme_config
import jinja2
import generators.javatype as javatype
import datetime
TEMPLATE_NAME = "entity.html"

def filter_javatype(s):
        """
        Maps type names from model to Java.
        """
        if isinstance(s, javatype.JavaType):
            s = s.name

        return {
                'integer': 'Integer',
                'string': 'String'
        }.get(s, s)

def filter_collectionGeneric(collection):
        return {
                'list': 'List',
                'set': 'Set',
                'map': 'Map'
        }.get(collection, collection)

def filter_collectionConcrete(collection):
        return {
                'list': 'ArrayList',
                'set': 'HashSet',
                'map': 'HashMap'
        }.get(collection, collection)

def filter_relations(entity_name, relations, node_filter, relation_type_filter):
    '''Filter out relations using lambda expressions for source/destination relations and relationship types'''

    return [r for r in relations if node_filter(entity_name, r) and relation_type_filter(r.relation_type)]
    

def generate(model):

    entities = model.entities

    # Create output folder
    if not os.path.exists(pymajorme_config.GEN_DIR):
        os.mkdir(pymajorme_config.GEN_DIR)

    # Initialize template engine.
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                pymajorme_config.TEMPLATES_DIR))))

    # Register filter for mapping Entity type names to Java type names.
    jinja_env.filters['javatype'] = filter_javatype
    jinja_env.filters['collectionGeneric'] = filter_collectionGeneric
    jinja_env.filters['collectionConcrete'] = filter_collectionConcrete

    # Load Java template
    template = jinja_env.get_template('entity.template')

    date = datetime.datetime.now().strftime("%d.%m.%Y. %H:%M:%S")

    for entity in entities:

        relations = model.relations

        source_filter = lambda entity_name, r: entity_name == r.source.name
        destination_filter = lambda entity_name, r: entity_name == r.destination.name
        # for attr in entity.attributes:
        #     print("atribut {}:".format(attr.name))
        #     if hasattr(attr, 'column_parameters'):
        #         for prm in attr.column_parameters:
        #             if hasattr(prm, 'value'):
        #                 print("param name:{} and value:{}".format(prm.name, prm.value))
        #             else:
        #                 print("param name:{}".format(prm.name))

        rendered = template.render({'entity': entity,
                                    'internal_single' : filter_relations(entity.name, relations, destination_filter, lambda rt: rt == '--' or rt == '->'),
                                    'internal_collection' : filter_relations(entity.name, relations, destination_filter, lambda rt: rt == '<->'),
                                    'external_single' : filter_relations(entity.name, relations, source_filter, lambda rt: rt == '--'),
                                    'external_collection' : filter_relations(entity.name, relations, source_filter, lambda rt: rt == '->' or rt == '<->'),
                                    'date': date})
        # For each entity generate java file
        with open(os.path.join(pymajorme_config.GEN_DIR, "%s.java" % entity.name.capitalize()), 'w') as f:
            f.write(rendered)
