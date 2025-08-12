"""A module to replace tomli and tomli_w for simple cases."""
import re
import ast

from psi_toml._version import __version__

version = __version__

VALID_KEYS_RE = [
    r'^\[\w{1,}(\-{0,1}\w{1,}){0,}\]$',
    r'^[A-Za-z0-9_-]{1,}$',
    r'^".{1,}"$',
    r"^'.{1,}'$",
]

VALID_TABLE_RE = [
    r'^\[\w{1,}(-{0,1}\w{1,})\]$',
    r'^\["\w{1,}(-{0,1}\w{1,})"]$',
    r"""^\['\w{1,}(-{0,1}\w{1,})']$""",
]

NESTED_TABLE_RE = [
    r"^\w{1,}\s{0,}=\s{0,}\[\{(.{1,}\s{0,}=s{0,}.{1,})\}{1,}]$",
]

VALID_EQUALS_RE = [
    r'^\w{1,}=\w{1,}$',
    r'^\w{1,}\s{0,}=\s{0,}\w{0,}\s{0,}"\w{0,}\s{0,}=\w{0,}"',
    r"^\w{1,}\s{0,}=\s{0,}\w{0,}\s{0,}'\w{0,}\s{0,}=\w{0,}'",
    r'^".{0,}=.{0,}"$',
    r"^'.{0,}=.{0,}'$",
]

QUOTED_HASH_RE = [
    r"\w{0,}'\w{0,}#\w{0,}'\w{0,}",
    r'\w{0,}"\w{0,}#\w{0,}"\w{0,}',
]

VALID_NUMBER_RE = r'^-{0,1}[0-9]{0,}\.{0,1}[0-9]{0,}$'

MULTI_LINE_RE = r'^\"{3}.{0,}\"{3}$'

LIST_LINE_RE = r'^(\[.{0,}\])$'

DICT_RE = r'^(\{.{0,}\})$'


class TOMLDecodeError(Exception):
    """Exception raised for custom error in the application."""

    def __init__(self, message: str = '') -> None:
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'TOMLDecodeError: {self.message}'


class TomlParser():
    """
    Provide basic functionality for TOML: load, dump, parse.
    """
    def __init__(self):
        self.parsing_table = False
        self.parsing_list = False
        self.list = []

    def load(self, file_handle) -> dict:
        """Read and parse a text file and return a dict."""
        try:
            text = file_handle.read()
            return self.parse(text.split('\n'))
        except Exception as err:
            raise TOMLDecodeError(err.args[0]) from err

    def dump(self, data: dict, file_handle) -> None:
        """Write dict in TOML format."""
        if not isinstance(data, dict):
            raise TOMLDecodeError('Invalid data format')
        try:
            text = self._dict_to_list(data)
            file_handle.write(text)
        except FileNotFoundError as err:
            raise FileNotFoundError(err.args[0]) from err

    def parse(self, data: list) -> dict:
        """Parse the list of text to generate a dict."""
        result = {}
        table_dict = {}
        table_name = ''
        key = ''
        for line, text in enumerate(data):
            try:
                if self.parsing_list:
                    item = data
                else:
                    (key, item) = self._parse(line, text)

                # Handle (multi-line) table
                if self.parsing_table:
                    # Handle start of a table
                    if (text and isinstance(text, str)
                            and text[0] == '['):
                        # save previous table
                        if table_dict and table_name:
                            result[table_name] = table_dict
                        table_name = text[1:-1]
                        table_dict = {}
                        result[table_name] = table_dict
                    else:
                        table_dict[key] = item

                # Handle (multi-line) lists
                # Handle start of a list
                if (item and isinstance(item, str)
                        and item[0] == '[' and not self.parsing_list):
                    text = self._start_list(line, item)
                    if isinstance(text, list):
                        item = text
                    else:
                        continue

                # End of a list
                if (text and isinstance(text, str)
                        and text[-1] == ']' and self.parsing_list):
                    item = self._end_list(line, text)
                    if table_name:
                        result[table_name][key] = item

                # A list item
                if self.parsing_list:
                    if text:
                        self._process_list_item(line, text)
                    continue

                # Continue with process
                if self.parsing_table and table_dict and table_name:
                    result[table_name] = table_dict
                elif key:
                    if key in result:
                        raise TOMLDecodeError(
                            f'Key defined multiple times: line {line+1}')
                    result[key] = item

            except TOMLDecodeError as err:
                raise TOMLDecodeError(err.args[0]) from err
        return result

    def _start_list(self, line: int, item: str) -> str:
        if item[-1] == ']':
            try:
                return ast.literal_eval(item)
            except SyntaxError as err:
                message = f'Invalid syntax in structure: line {line+1}'
                raise TOMLDecodeError(message) from err

        self.list = []
        self.parsing_list = True
        return item

    def _end_list(self, line: int, item: str) -> list:
        item = item.strip()
        if len(item) > 1:
            item = item[:-1]
            self._process_list_item(line, item)
        item = self.parsing_list
        self.parsing_list = False
        return self.list

    def _process_list_item(self, line: int, text: str) -> None:
        if ',' in text:
            for sub_text in text.split(','):
                if sub_text:
                    sub_text = self._get_item(line, sub_text.strip())
                    self.list.append(sub_text)
        else:
            sub_text = self._get_item(line, text.strip())
            self.list.append(sub_text)

    def _parse(self, line: int, text: str) -> tuple:
        (key, item) = ('', '')
        if not text:
            return (key, item)

        # Comment lines
        if text[0] == '#':
            return (key, item)
        if '#' in text:
            for test in QUOTED_HASH_RE:
                if re.search(test, text):
                    break
            else:  # after or no break
                text = text[:text.index('#')]

        # Tables
        for test in NESTED_TABLE_RE:
            if re.search(test, text):
                return self._nested_table(line, text)

        key_portion = text
        if '=' in text:
            key_portion = self._strip(text[:text.index('=')])
            item = text[text.index('=')+1:].strip()
        if '[' in key_portion or ']' in key_portion or '=' not in text:
            self._validate_tables(line, key_portion)
        # Standard items
        if '=' in text:
            if text.count('=') > 1:
                self._validate_equals(line, item)
            return self._get_key_item(line, text)
        return (key, item)

    def _get_key_item(self, line: int, text: str) -> tuple:
        index = text.index('=')
        key = self._get_key(line, text[:index])
        item_text = text[index+1:].strip()
        item = self._get_item(line, item_text)
        return (key, item)

    def _get_key(self, line: int, key: str) -> str:
        key = key.strip()
        for test in VALID_KEYS_RE:
            if re.search(test, key):
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid key definition: line {line+1}')
        return self._strip(key)

    def _get_item(self, line: int, item: str) -> any:
        if not item:
            raise TOMLDecodeError(f'Invalid value definition: line {line+1}')

        if re.search(DICT_RE, item):
            print(f'*** Dictionary in toml at line {line+1}. ***')
        if re.search(LIST_LINE_RE, item) or re.search(DICT_RE, item):
            try:
                item = ast.literal_eval(item)
            except SyntaxError as err:
                message = f'Invalid syntax in structure: line {line+1}'
                raise TOMLDecodeError(message) from err

        elif re.search(MULTI_LINE_RE, item):
            item = item.replace('"""', '')
        elif (item[0] == '"' and item[-1] == '"'
                or item[0] == "'" and item[-1] == "'"):
            return item[1:-1]
        elif re.search(VALID_NUMBER_RE, item):
            return float(item) if '.' in item else int(item)
        elif item == 'true':
            return True
        elif item == 'false':
            return False
        return item

    def _validate_equals(self, line: int, text: str) -> None:
        for test in VALID_EQUALS_RE:
            if re.search(test, text):
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid equals definition: line {line+1}')

    def _validate_tables(self, line: int, text: str) -> None:
        for test in VALID_TABLE_RE:
            if re.search(test, text):
                self.parsing_table = True
                break
        else:  # after or no break
            raise TOMLDecodeError(f'Invalid table definition: line {line+1}')

    def _nested_table(self, line: int, text: str) -> tuple:
        key = self._strip(text[:text.index('=')])
        text = text[text.index('[')+2:-2].split(',')
        output = {}
        for part in text:
            (part_key, item) = self._get_key_item(line, part)
            output[part_key] = item
        return (key, output)

    def _dict_to_list(self, raw_dict: dict) -> str:
        toml = []
        dicts = []
        for key, item in raw_dict.items():
            if isinstance(item, dict):
                item = self._dict_to_table(item)
                dicts.append(f'[{key}]\n{item}')
                continue
            if isinstance(item, str):
                item = f'"{item}"'
            elif item is True:
                item = 'true'
            elif item is False:
                item = 'false'
            toml.append(f'{key} = {item}')
        toml.append('\n'.join(dicts))
        return '\n'.join(toml)

    def _dict_to_table(self, raw_dict: dict):
        output = []
        for key, item in raw_dict.items():
            if not key:
                continue
            if item is True:
                output.append(f'{key} = true')
            elif item is False:
                output.append(f'{key} = false')
            elif isinstance(item, (int, float)):
                output.append(f'{key} = {item}')
            else:
                output.append(f'{key} = "{item}"')
        return '\n'.join(output)

    @staticmethod
    def _strip(text: str) -> str:
        text = text.strip()
        text = text.strip('"')
        return text.strip("'")
