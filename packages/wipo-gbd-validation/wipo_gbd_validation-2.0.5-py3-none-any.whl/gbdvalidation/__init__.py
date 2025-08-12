from jinja2 import Undefined, Template
import jinja2.ext
from jinja2.lexer import Token

class ChangeMunch(jinja2.ext.Extension):
    """
    Insert a `|demunch_filter` filter at the end of every variable substitution.

    This will ensure that all injected values are converted to YAML.
    """
    def filter_stream(self, stream):
        tokens = []
        tokens_name = []
        for token in stream:
            if token.type == 'variable_begin':
                tokens = []
                tokens_name = []
            if token.type == 'variable_end':
                if not('lparen' in tokens and 'pipe' not in tokens):
                    if 'field_name' not in tokens_name:
                        yield Token(token.lineno, 'pipe', '|')
                        yield Token(token.lineno, 'name', 'demunch_filter')
            tokens.append(token.type)
            tokens_name.append(token.value)
            yield token
