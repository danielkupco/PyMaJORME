import os
import pymajorme_config
import jinja2
import generators.entity as entity

TEMPLATE_NAME = "entity.html"

def javatype(s):
        """
        Maps type names from Entity to Java.
        """
        if isinstance(s, entity.Entity):
            s = s.name

        return {
                'integer': 'Integer',
                'string': 'String'
        }.get(s, s)

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
    jinja_env.filters['javatype'] = javatype

    # Load Java template
    template = jinja_env.get_template('java.template')

    for entity in entities:
        rendered = template.render({'entity': entity})
        # For each entity generate java file
        with open(os.path.join(pymajorme_config.GEN_DIR, "%s.java" % entity.name.capitalize()), 'w') as f:
            f.write(rendered)