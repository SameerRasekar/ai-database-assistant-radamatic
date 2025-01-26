import os
from string import Template

class PromptTemplateHelper:
    def __init__(self, logger):
          self.logger = logger

    def load_template(self, name="default"):
            # file path
            lib_path = os.path.dirname(__file__)
            parent_dir  = os.path.dirname(lib_path)
            file_path = "%s/templates/%s.txt" % (parent_dir, name)
            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Template {name} does not exist.")
                with open(file_path, 'r', encoding='utf-8') as f:
                    template = Template(f.read())
            except Exception as ex:
                self.logger.error(f"Exception while loading the template : {ex}")
                template = None
    
            return template