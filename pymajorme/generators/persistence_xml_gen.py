import os
import pymajorme_config
import jinja2
import datetime
from helpers.pack import pack

TEMPLATE_NAME = 'persistence_xml.template'

@pack
def generate(model, output_path):

    # Initialize template engine.
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                pymajorme_config.TEMPLATES_DIR))))

    # Load Java template
    template = jinja_env.get_template(TEMPLATE_NAME)

    date = datetime.datetime.now().strftime('%d.%m.%Y. %H:%M:%S')

    rendered = template.render({'date': date,
                                'context': model.context.name,
                                'db_name': model.db_name.name,
                                'username': model.username.name,
                                'password': model.password.name})

    meta_inf_dir = os.path.join(output_path, 'META-INF')
    if not os.path.exists(meta_inf_dir):
        os.mkdir(meta_inf_dir)

    # For each entity generate java file
    with open(os.path.join(meta_inf_dir, 'persistence.xml'), 'w') as f:
        f.write(rendered)
