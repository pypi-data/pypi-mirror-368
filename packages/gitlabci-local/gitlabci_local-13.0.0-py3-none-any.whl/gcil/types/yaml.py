#!/usr/bin/env python3

# Standard libraries
from copy import deepcopy
from io import TextIOWrapper
from re import fullmatch as regex_fullmatch, sub as regex_sub
from sys import maxsize
from typing import Any, Dict, List, Optional, Union

# Modules libraries
from yaml import dump as yaml_dump, load_all as yaml_load_all
from yaml import SafeLoader as yaml_SafeLoader, YAMLError as yaml_Error
from yaml.nodes import SequenceNode as yaml_SequenceNode

# YAML class
class YAML:

    # Data type
    Data = Dict[str, Any]

    # Error type
    Error = yaml_Error

    # Input type, pylint: disable=too-few-public-methods
    class Input:

        # Constants
        TYPE_ARRAY: str = 'array'
        TYPE_BOOLEAN: str = 'boolean'
        TYPE_NUMBER: str = 'number'
        TYPE_STRING: str = 'string'

        # Members
        default: Optional[Union[float, int, str]] = None
        description: Optional[str] = None
        options: Optional[List[str]] = None
        regex: Optional[str] = None
        value: Optional[Union[float, int, str]] = None
        value_type: str = TYPE_STRING

        # Set description
        def set_description(self, description: str) -> None:
            self.description = description

        # Set type
        def set_type(self, value: str) -> None:
            if value not in [
                    # YAML.Input.TYPE_ARRAY,
                    YAML.Input.TYPE_BOOLEAN,
                    YAML.Input.TYPE_NUMBER,
                    YAML.Input.TYPE_STRING,
            ]:
                raise TypeError(f'\'{value}\': Input type unknown value')
            self.value_type = value

        # Set options
        def set_options(self, options: List[Any]) -> None:
            if not options:
                raise ValueError('Options cannot be empty for input')
            if self.value_type not in [YAML.Input.TYPE_NUMBER, YAML.Input.TYPE_STRING]:
                raise TypeError(
                    f'\'{self.value_type}\': Options can only be used with string and number inputs'
                )
            for option in options:
                if self.value_type == YAML.Input.TYPE_NUMBER and not isinstance(
                        option, (float, int)):
                    raise TypeError(
                        f'\'{option}\': Options can only be numbers for inputs')
                if self.value_type in YAML.Input.TYPE_STRING and not isinstance(
                        option, str):
                    raise TypeError(
                        f'\'{option}\': Options can only be strings for inputs')
                if self.regex and not regex_fullmatch(self.regex, option):
                    raise ValueError(f'\'{option}\': Option value does not match'
                                     f' required RegEx pattern \'{self.regex}\'')
            self.options = options[:]

        # Set regex
        def set_regex(
            self,
            regex: str,
        ) -> None:
            if self.value_type not in [YAML.Input.TYPE_STRING]:
                raise TypeError(
                    f'\'{self.value_type}\': RegEx validation can only be used with string inputs'
                )
            self.regex = regex

        # Set default
        def set_default(
            self,
            default: Union[bool, float, int, str],
        ) -> None:
            self.default = self.parse_value(default)

            # Validate input default
            if self.options and self.default not in self.options:
                raise ValueError(
                    f'\'{self.default}\': Default value not allowed in options'
                    f': {", ".join(self.options)})')
            if self.regex and not regex_fullmatch(self.regex, str(self.default)):
                raise ValueError(f'\'{self.default}\': Default value does not match'
                                 f' required RegEx pattern \'{self.regex}\'')

        # Set value
        def set_value(
            self,
            value: Union[bool, float, int, str],
        ) -> None:
            self.value = self.parse_value(value)

            # Validate input value
            if self.options and self.value not in self.options:
                raise ValueError(
                    f'\'{self.value}\': Value not allowed in options: {", ".join(self.options)})'
                )
            if self.regex and not regex_fullmatch(self.regex, str(self.value)):
                raise ValueError(f'\'{self.value}\': Value does not match'
                                 f' required RegEx pattern \'{self.regex}\'')

        # Parse value, pylint: disable=too-many-branches,too-many-return-statements
        def parse_value(
            self,
            value: Union[bool, float, int, str],
        ) -> Union[bool, float, int, str]:

            # Set boolean value
            if self.value_type == YAML.Input.TYPE_BOOLEAN:
                if isinstance(value, bool):
                    return str(value).lower()
                if isinstance(value, int) and value in [1]:
                    return 'true'
                if isinstance(value, int) and value in [0]:
                    return 'false'
                if isinstance(value, str) and value.lower() in ['true', '1']:
                    return 'true'
                if isinstance(value, str) and value.lower() in ['false', '0']:
                    return 'false'
                raise ValueError(f'\'{value}\': Value is not a boolean')

            # Set number value
            if self.value_type == YAML.Input.TYPE_NUMBER:
                if isinstance(value, bool):
                    raise ValueError(f'\'{value}\': Value is not a number')
                if isinstance(value, (float, int)):
                    return value
                if isinstance(value, str):
                    try:
                        if '.' in value:
                            return float(value)
                        return int(value)
                    except ValueError:
                        raise ValueError(f"'{value}': Value is not a number") # pylint: disable=raise-missing-from

            # Set string value
            if self.value_type == YAML.Input.TYPE_STRING:
                if isinstance(value, (float, int, list)):
                    return str(value)
                if isinstance(value, str):
                    return value

            # Invalid value type
            raise TypeError(f'\'{value}\': Value type \'{self.value_type}\' supported'
                            ) # pragma: no cover

    # Reference class
    class Reference:

        # Constants
        NESTED_LIMIT: int = 10
        TAG: str = '!reference'

        # Constructor
        def __init__(self, values: List[str]):
            self._values = values

        # Values
        @property
        def values(self) -> List[str]:
            return self._values

        # Add constructor
        @staticmethod
        def add_constructor(
            loader: yaml_SafeLoader,
            node: yaml_SequenceNode,
        ) -> 'YAML.Reference':
            return YAML.Reference(loader.construct_sequence(node))

        # Resolve, pylint: disable=too-many-branches
        @staticmethod
        def resolve(data: Any, node: Any) -> bool:

            # Variables
            changed: bool = False

            # Dictionnaries
            if isinstance(node, dict):
                for key in node.keys():
                    if isinstance(node[key], YAML.Reference):
                        references = list(node[key].values)
                        referenced_node = data
                        for reference in references:
                            if reference in referenced_node:
                                referenced_node = referenced_node[reference]
                            else: # pragma: no cover
                                referenced_node = None
                                break
                        changed = True
                        if referenced_node:
                            node[key] = deepcopy(referenced_node)
                        else: # pragma: no cover
                            del node[key]
                    elif YAML.Reference.resolve(data, node[key]):
                        changed = True

            # Lists
            elif isinstance(node, list):
                for index in reversed(range(len(node))):
                    if isinstance(node[index], YAML.Reference):
                        references = list(node[index].values)
                        referenced_node = data
                        for reference in references:
                            if reference in referenced_node:
                                referenced_node = referenced_node[reference]
                            else: # pragma: no cover
                                referenced_node = None
                                break
                        changed = True
                        if referenced_node:
                            node[index:index + 1] = deepcopy(referenced_node)
                        else: # pragma: no cover
                            del node[index]
                    elif YAML.Reference.resolve(data, node[index]):
                        changed = True # pragma: no cover

            # Standard types
            # else:
            #     pass

            # Result
            return changed

    # Parse spec inputs
    @staticmethod
    def parse_spec_inputs(
        spec: Data,
        file_path: str,
        file_inputs: Dict[str, str],
    ) -> Dict[str, Input]:

        # Variables
        inputs: Dict[str, YAML.Input] = {}

        # Validate YAML spec syntax
        if 'spec' not in spec or 'inputs' not in spec['spec']:
            return inputs

        # Parse YAML spec inputs
        for key, item in spec['spec']['inputs'].items():

            # Prepare input
            inputs[key] = YAML.Input()
            if isinstance(item, dict):
                if 'description' in item and isinstance(item['description'], str):
                    inputs[key].set_description(item['description'])
                if 'type' in item and isinstance(item['type'], str):
                    inputs[key].set_type(item['type'])
                if 'regex' in item and isinstance(item['regex'], str):
                    inputs[key].set_regex(item['regex'])
                if 'options' in item and isinstance(item['options'], list):
                    inputs[key].set_options(list(item['options']))
                if 'default' in item and isinstance(item['default'],
                                                    (bool, float, int, str)):
                    inputs[key].set_default(item['default'])

            # Prepare input value
            if isinstance(item,
                          dict) and key in file_inputs and file_inputs[key] is not None:
                inputs[key].set_value(file_inputs[key])
            elif inputs[key].default is not None:
                inputs[key].set_value(inputs[key].default) # type: ignore[arg-type]

            # Validate input value
            if inputs[key].value is None:
                raise SyntaxError(f'Missing value for input \'{key}\' in \'{file_path}\'')

        # Result
        return inputs

    # Evaluate string
    @staticmethod
    def evaluate_spec_field(field: str, inputs: Dict[str, Input]) -> str:

        # Variables
        result: str = field

        # Evaluate inputs
        for variable, node in inputs.items():
            assert node.value is not None
            result = regex_sub(fr'\$\[\[\s*inputs\.{variable}\s*\]\]', str(node.value),
                               result)

        # Result
        return result

    # Evaluate spec
    @staticmethod
    def evaluate_spec(data: Data, inputs: Dict[str, Input]) -> Data:

        # Recurse on keys
        if isinstance(data, dict):
            return {
                YAML.evaluate_spec_field(key, inputs): YAML.evaluate_spec(value, inputs)
                for key, value in data.items()
            }

        # Recurse on items
        if isinstance(data, list):
            return [YAML.evaluate_spec(value, inputs) for value in data]

        # Evaluate string items
        if isinstance(data, str):
            return YAML.evaluate_spec_field(data, inputs)

        # Fallback
        return data # pragma: no cover

    # Load, pylint: disable=too-many-branches
    @staticmethod
    def load(
        stream: TextIOWrapper,
        inputs: Dict[str, str],
        configure: bool,
    ) -> Optional[Data]:

        # Variables
        data: Optional[YAML.Data]
        documents: List[YAML.Data]
        file_inputs: Dict[str, YAML.Input]

        # Prepare loader class
        loader = yaml_SafeLoader
        loader.add_constructor(YAML.Reference.TAG, YAML.Reference.add_constructor)

        # Load YAML documents
        documents = list(yaml_load_all(stream, Loader=loader))

        # Empty YAML data
        if not documents:
            data = None

        # Acquire YAML configuration data
        elif len(documents) == 1:
            data = documents[0]

        # Acquire YAML component data
        elif len(documents) == 2:

            # Parse spec inputs
            file_inputs = YAML.parse_spec_inputs(
                documents[0],
                stream.name,
                file_inputs=inputs,
            )

            # Configure spec inputs
            if configure:
                from ..features.menus import MenusFeature # pylint: disable=cyclic-import,import-outside-toplevel
                configure_inputs: Dict[str, Dict[str, Union[bool, List[str], str]]] = {}
                for key, node in file_inputs.items():
                    configure_inputs[key] = {}
                    configure_inputs[key]['help'] = node.description \
                        if node.description else 'Configure variable value'
                    if node.value_type == YAML.Input.TYPE_ARRAY: # pragma: no cover
                        raise TypeError(f'\'{key}\': Input type unknown value')
                    if node.value_type == YAML.Input.TYPE_BOOLEAN:
                        configure_inputs[key]['type'] = 'boolean'
                    elif node.options:
                        configure_inputs[key]['type'] = 'choice'
                        configure_inputs[key]['values'] = node.options
                    elif node.value_type == YAML.Input.TYPE_STRING:
                        configure_inputs[key]['type'] = 'input'
                    configure_inputs[key]['set'] = key in inputs
                    if key in inputs:
                        configure_inputs[key]['default'] = str(node.value)
                    elif node.default:
                        configure_inputs[key]['default'] = str(node.default)
                    else:
                        configure_inputs[key]['default'] = ''
                configured_variables: Dict[str, str] = \
                        MenusFeature.configure(configure_inputs)
                for key, value in configured_variables.items():
                    file_inputs[key].set_value(value)

            # Evaluate spec inputs
            data = YAML.evaluate_spec(
                documents[1],
                inputs=file_inputs,
            )

        # Unsupport YAML data
        else:
            raise SyntaxError(
                f'Unsupported documents count ({len(documents)}) in \'{stream.name}\'')

        # Result
        return data

    # Dump
    @staticmethod
    def dump(data: Data) -> str:

        # Dump YAML data
        return str(yaml_dump(
            data,
            indent=2,
            sort_keys=False,
            width=maxsize,
        ))

    # Resolve
    @staticmethod
    def resolve(data: Dict[Any, Any]) -> None:

        # Resolve references
        for _ in range(YAML.Reference.NESTED_LIMIT):
            if not YAML.Reference.resolve(data, data):
                break
        else: # pragma: no cover
            # error
            pass
