import json
import xmltodict
import xml
import os
import re
import inspect
from jinja2 import FileSystemLoader, Environment
from munch import munchify, DefaultMunch

from gbdvalidation.rules import get_error_from_code
from gbdvalidation import ChangeMunch
from gbdvalidation.rules import WIPOST3CodeType, ISOLanguageCodeType, ISOFormerCountryCodeType

class RuleEngine:

    def __init__(self):
        templates_path = os.path.join(os.path.dirname(__file__),
                                      'rules', 'definitions')
        self.templates = [
           f for f in os.listdir(templates_path) if f.endswith('.tmpl')
        ]

        self.env = Environment(autoescape=False,
                               lstrip_blocks=True,
                               extensions=(ChangeMunch,),
                               loader=FileSystemLoader(
                                   templates_path))
        try:
            module = 'filters'
            module_tmp = __import__('gbdvalidation.rules.filters', globals(), locals(), [module])
            filters_raw = [
                x for x in inspect.getmembers(module_tmp)
                if not str(x[0]).startswith('_')]
            for filter in filters_raw:
                self.env.filters[filter[0]] = filter[1]
        except ModuleNotFoundError as e:
            print(e)

    def load_data(self, input_file=None, input_string=None):
        if not((input_file is None) ^ (input_string is None)):
            raise Exception(
                "You must provide either an input_file or an input_string")

        if input_file:
            _, extension = os.path.splitext(input_file)
            if extension not in ['.json']:
                raise Exception('input_file can be only be JSON')

            with open(input_file, 'r') as f:
                input_string = ''.join(f.readlines())

        # Decide if the input string is a JSON or XML
        try:
            data = json.loads(input_string)
        except json.decoder.JSONDecodeError as e:
            raise e
        # Convert the python dict to python object for the input data
        return munchify(data, factory=EmptyNoneMunch)

    def convert_rules(self, loaded_rules):
        regex = r'\[(\d+)\] (.*)'
        to_return = []
        matches = re.findall(regex, loaded_rules)
        for match in matches:
            try:
                rule_passed = eval(match[1])
            except Exception as e:
                print("Exception in[%s] %s: %s" % (
                    match[0], match[1], e))
                rule_passed = False
            to_return.append({
                'code': match[0],
                'rule': match[1],
                'rule_passed': rule_passed
            })
        return to_return

    def validate(self, input_file=None, input_string=None):
        data = self.load_data(input_file=input_file, input_string=input_string)
        return self._validate(data)

    def validate_with_dict(self, data):
        data = munchify(data, factory=EmptyNoneMunch)
        return self._validate(data)

    def _validate(self, data):
        # deleted documents have minimum validation (only st13)
        if data.gbdStatus == 'Delete':
            template_name = 'deleted.tmpl'
        else:
            template_name = '%s.tmpl' % data.type.lower()

        if template_name not in self.templates:
            raise IOError("%s not found" % template_name)

        template = self.env.get_template(template_name)
        loaded_rules = self.convert_rules(template.render(doc=data,
                                                          CC=WIPOST3CodeType+ISOFormerCountryCodeType,
                                                          LC=ISOLanguageCodeType))
        errors = []
        for rule in loaded_rules:
            if not rule['rule_passed']:
                errors.append(get_error_from_code(rule['code']))
        return errors

    def flatten(self, list_of_lists):
        to_return = []
        for el in list_of_lists:
            to_return.extend(el)
        return to_return

    def flatten_dict(self, dict_of_lists):
        to_return = []
        for el in dict_of_lists:
            for key in el.keys():
                if isinstance(el[key], list):
                    to_return.extend(el[key])
        return to_return

class EmptyNoneMunch(DefaultMunch):
    """
    A Munch that returns a None value for missing keys.
    """

    def __init__(self, *args, **kwargs):
        default = None
        super(DefaultMunch, self).__init__(*args, **kwargs)
        self.__default__ = default
