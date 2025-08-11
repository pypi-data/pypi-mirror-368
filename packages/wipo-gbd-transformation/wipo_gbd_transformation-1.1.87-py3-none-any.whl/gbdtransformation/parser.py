import json
import xmltodict
import xml
import os
from munch import munchify, DefaultMunch
import inspect
from jinja2 import FileSystemLoader, Environment
from gbdtransformation import renders
from gbdtransformation.common import SilentUndefined, YAMLEverythingExtension
from gbdvalidation.engine import RuleEngine
import gzip


def trim_nulls(value):
    if hasattr(value, '__value'):
        return trim_nulls(value['__value'])
    return value if value is not None else ''


class Parser:

    """Class to parse input using the configuration render"""
    def __init__(self, template_name, type=None):
        """Constructor
        @param template_name: the name of the template to be used
        @param render: the render function that should be used
        """

        self.template = template_name
        self.type = type

        # fallback to guessing: it is used for migration and
        # gbd-transform cli
        if not self.type:
            # brands special cases ugly hack
            if template_name == 'woao':
                self.type = 'brands'
            elif template_name == 'wo6ter':
                self.type = 'brands'
            elif template_name == 'whoinn':
                self.type = 'brands'
            elif template_name.endswith('tm'):
                self.type = 'brands'
            elif template_name.endswith('id'):
                self.type = 'designs'
            elif template_name == 'emap' or template_name == 'emrp':
                self.type = 'commons'
            else:
                self.type = 'common'
        self.render = self.get_render()

        templates_path = [
            # brands/xxtm
            os.path.join(os.path.dirname(__file__),
                         self.type,
                         self.template),

            # brands | designs
            os.path.join(os.path.dirname(__file__),
                         self.type),

            # common
            os.path.join(os.path.dirname(__file__), 'common')
        ]
        for template_path in templates_path:
            if not os.path.exists(template_path):
                raise IOError("%s not found" % template_path)

        # Create the jinja2 enviroment and load the general and template
        # specific filter
        ext = []
        if self.render != 'XML':
            ext = (YAMLEverythingExtension,)
        self.env = Environment(autoescape=False,
                               undefined=SilentUndefined,
                               extensions=ext,
                               lstrip_blocks=True,
                               finalize=trim_nulls,
                               loader=FileSystemLoader(
                                   templates_path))
        self.load_filters()

    def load_data(self, input_file=None, input_string=None):
        """
        @param input_string: the input data as string
        @param input_file: the input data as filename
        """
        # either one should be passed
        if not((input_file is None) ^ (input_string is None)):
            raise Exception(
                "You must provide either an input_file or an input_string")

        if input_file:
            if input_file.endswith('.gz'):
                with gzip.open(input_file, 'rb') as f:
                    input_string = f.read()
            else:
                _, extension = os.path.splitext(input_file)
                if extension not in ['.json', '.xml']:
                    raise Exception('input_file can be only be JSON or XML')

                with open(input_file, 'r') as f:
                    input_string = ''.join(f.readlines())

        # Decide if the input string is a JSON or XML
        try:
            data = json.loads(input_string)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as _:
            try:
                # namespaces to ignore
                namespaces = {
                    ns: None for ns in self.env.filters.get(
                        'ignore_namespace', [])}
                data = json.loads(
                    json.dumps(xmltodict.parse(input_string,
                                               process_namespaces=True,
                                               namespaces=namespaces,
                                               namespace_separator='_',
                                               attr_prefix='_',
                                               cdata_key='__value')))
            except xml.parsers.expat.ExpatError as _:
                raise Exception("Data can be only JSON or XML")
        except Exception as e:
            raise e
        # Convert the python dict to python object for the input data
        return munchify(data, factory=EmptyNoneMunch)


    def load_filters(self):
        """Jinja filter loader"""
        modules = ['gbdtransformation.common.filters', 'gbdtransformation.%s.filters' % self.type,
                   'gbdtransformation.%s.%s.filters' % (self.type, self.template)]
        for tmp in modules:
            try:
                module = tmp.split('.')[-1]
                module_tmp = __import__(tmp, globals(), locals(), [module])
                filters_raw = [
                    x for x in inspect.getmembers(module_tmp)
                    if not str(x[0]).startswith('_')]
                for filter in filters_raw:
                    self.env.filters[filter[0]] = filter[1]
            except ModuleNotFoundError as e:
                print(e)
                continue

    def get_render(self):
        module = 'gbdtransformation.%s.%s' % (self.type, self.template)
        module_tmp = module.split('.')[-1]
        module_tmp = __import__(module, globals(), locals(), [module_tmp])
        return getattr(module_tmp, 'render')

    def run(self, input_data, raise_errors=False):
        """Excecutor function for the parser"""
        if os.path.exists(input_data):
            data = self.load_data(input_file=input_data)
        else:
            data = self.load_data(input_string=input_data)
        template = self.env.get_template('template.yml')
        res = template.render(data)
        res = renders.sanitize(res)
        render = getattr(renders, self.render)
        if raise_errors:
            return render(res, raise_errors=True)
        return render(res)

    def run_with_object(self, *args, **kwargs):
        template = self.env.get_template('template.yml')
        res = template.render(kwargs)
        res = renders.sanitize(res)
        render = getattr(renders, self.render)
        return render(res)

    def validate(self, input_data, gbd_format=None):
        """Validates an input xml against GDB-Validation"""
        if gbd_format is None:
            gbd_format = self.run(input_data)
        validator = RuleEngine()
        validation_errors = validator.validate(input_string=gbd_format)
        return gbd_format, validation_errors


class EmptyNoneMunch(DefaultMunch):
    """
    A Munch that returns a None value for missing keys.
    """

    def __init__(self, *args, **kwargs):
        default = None
        super(DefaultMunch, self).__init__(*args, **kwargs)
        self.__default__ = default
