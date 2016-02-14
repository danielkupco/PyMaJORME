import os
import pymajorme_config
import jinja2
import datetime

CLASS_TEMPLATE_NAME = 'dao_class.template'
INTERFACE_TEMPLATE_NAME = 'dao_interface.template'
GENERIC_DAO_CLASS_TEMPLATE_NAME = 'generic_dao_class.template'
GENERIC_DAO_INTERFACE_TEMPLATE_NAME = 'generic_dao_interface.template'
imports = []


def add_import(value):
    if not imports.__contains__(value):
        imports.append(value)


def generate(model):

    entities = model.entities

    # Initialize template engine.
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                pymajorme_config.TEMPLATES_DIR, 'dao'))))

    # Load Dao templates
    class_template = jinja_env.get_template(CLASS_TEMPLATE_NAME)
    interface_template = jinja_env.get_template(INTERFACE_TEMPLATE_NAME)

    generic_dao_class_template = jinja_env.get_template(GENERIC_DAO_CLASS_TEMPLATE_NAME)
    generic_dao_interface_template = jinja_env.get_template(GENERIC_DAO_INTERFACE_TEMPLATE_NAME)

    date = datetime.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')

    # Generic dao
    generic_dao_class_rendered = generic_dao_class_template.render({'package': model.package.name,
                                                                    'date': date})
    generic_dao_interface_rendered = generic_dao_interface_template.render({'package': model.package.name,
                                                                            'date': date})
    # generate java file
    with open(os.path.join(pymajorme_config.GEN_DIR, 'GenericDao.java'), 'w') as f:
        f.write(generic_dao_class_rendered)
    with open(os.path.join(pymajorme_config.GEN_DIR, 'IGenericDao.java'), 'w') as f:
        f.write(generic_dao_interface_rendered)

    id_type = ''

    for entity in entities:
        for attr in entity.attributes:
            found = False
            if hasattr(attr, 'column_parameters'):
                for prm in attr.column_parameters:
                    if prm.name == 'GUID':
                        id_type = attr.type.name
                        found = True
                        break
            if found:
                break

        class_rendered = class_template.render({'entity': entity.name,
                                                'id_type': id_type,
                                                'date': date,
                                                'package': model.package.name})

        interface_rendered = interface_template.render({'entity': entity.name,
                                                        'id_type': id_type,
                                                        'date': date,
                                                        'package': model.package.name})

        # For each entity generate java file
        with open(os.path.join(pymajorme_config.GEN_DIR, '{}Dao.java'.format(entity.name)), 'w') as f:
            f.write(class_rendered)

        with open(os.path.join(pymajorme_config.GEN_DIR, 'I{}Dao.java'.format(entity.name)), 'w') as f:
            f.write(interface_rendered)