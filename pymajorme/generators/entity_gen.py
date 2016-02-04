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
    #
    # for entity in entities:
    #     part_pl = entity.namePiece.partname.lower() + pymajorme_config.PLURAL
    #     part_dir = os.path.join(pymajorme_config.GEN_DIR, part_pl)
    #     if not os.path.exists(part_dir):
    #         os.makedirs(part_dir)
    #
    #     env = Environment(trim_blocks=True, lstrip_blocks=True, loader=PackageLoader(pymajorme_config.TEMPLATES_DIR, '.'))
    #     template = env.get_template(TEMPLATE_NAME)
    #     rendered = template.render({'ModuleName': part_pl.capitalize(),
    #                                 'DBName': part_pl,
    #                                 'PartNamePlural': part_pl,
    #                                 'PartNameSingular': entity.namePiece.partname.lower()})
    #
    #     file_name = os.path.join(part_dir, TEMPLATE_NAME)
    #     with open(file_name, "w+") as f:
    #         f.write(rendered)
    #         print(mean_gen_config.GENERATED_MESSAGE + file_name)