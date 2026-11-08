#!/usr/bin/env python3

import argparse, sys, os, re
from mimetypes import guess_type
from pathlib import Path
from typing import Final

NAME: Final[str] = 'generate-github-wiki'
VERSION: Final[str] = '0.1.0'

class __DocumentFunction:
    def __init__(self, signature: str, description: str = "", args: dict[str, str] = {}, returns: dict[str, str] = ""):
        self.signature: dict[str, str] = signature
        self.description: dict[str, str] = description
        self.args: list[dict[str, str]] = args
        self.returns: dict[str, str] = returns

class __Document:
    def __init__(self, class_name: str, description: str = "", functions: tuple[__DocumentFunction] = ()):
        self.class_name: str = class_name
        self.description: str = description
        self.functions: tuple[__DocumentFunction] = functions

def __is_python_file(file: Path) -> bool:
    return guess_type(file)[0] == 'text/x-python'

def __parse_file(file: Path) -> list[__Document]:
    intentional_newline: Final[str] = '\n\n'
    
    documents: list[__Document] = []

    def is_docustring(string: str):
        return string == '"""' or string == "'''"

    if __is_python_file(file):
        with open(file, "r") as file:
            docustring: bool = False
            building_class: bool = False
            class_signature: str = None
            building_function: bool = False
            function_signature: str = None
            arg: list[str] = [] # [key, description]
            args: bool = False
            returns: bool = False

            for line in file:
                stripped_line: str = line.strip()
                # start class (document) processing
                if stripped_line.startswith('class'):
                    class_signature = stripped_line.replace('class ', '').replace(':', '').strip()
                    if class_signature.startswith('_'):
                        continue
                    docustring = True
                    building_class = True
                    continue
                # start function processing
                if stripped_line.startswith('def'):
                    function_signature = re.sub(r'\([^)]*\):', '', stripped_line.replace('def ', '')).strip()
                    if function_signature.startswith('_'):
                        continue
                    docustring = True
                    building_function = True
                    continue

                current_document: __Document = documents[-1]
                current_function: __DocumentFunction = current_document.functions[-1]
                
                # Check to see if class/function has a docustring
                if docustring:
                    if not __is_docustring(line):
                        building_class = False
                        building_function = False
                    elif building_class:
                        # Create new class file
                        documents.add(__Document(class_signature))
                    elif building_function:
                        # Create new function entry to class file
                        current_document.add(__DocumentFunction(function_signature))
                    docustring = False
                    continue
                
                # Stop building if at end of docustring
                if __is_docustring(line):
                    docustring: bool = False
                    building_class: bool = False
                    class_signature: str = None
                    building_function: bool = False
                    function_signature: str = None
                    arg: list[str] = [] # [key, description]
                    args: bool = False
                    returns: bool = False
                    continue

                if building_function:
                    match stripped_line:
                        case 'Args:':
                            args = True
                            continue
                        case 'Returns:':
                            args = False
                            returns = True
                            continue
                        case _:
                            if not (args or returns):
                                current_function.description += intentional_newline if line == '\n' else line.strip() + " "
                                continue
                
                    split_line: list[str] = stripped_line.split(': ')
                    # assign a key if it hasn't been done already
                    if len(split_line) > 1:
                        arg[0] = split_line[0]
                        arg[1] = split_line[1:len(split_line) - 1].join(': ')
                    else:
                        # preserve intentional newlines
                        if line == '\n':
                            arg[1] += intentional_newline
                        # TODO: preserve multi-level bulleted lists
                        else:
                            # join split words
                            if arg[1][-1] == '-':
                                arg[1] = arg[1][0:len(arg[1]) - 1]
                            # ensure spaces between words
                            else:
                                arg[1] += ' '
                            arg[1] += stripped_line
                else:
                    # line = re.sub(r'^[^\S\r\n]+|[^\S\r\n]+$', '', line)
                    if building_class:
                        current_document.description += intentional_newline if line == '\n' else line.strip() + " "
                    else:
                        
                    continue

                if args:

                    

                elif returns:
                    pass

        return True
    
    return False

def __create_file(document: __Document):
    pass

parser = argparse.ArgumentParser(
    prog=NAME,
    description='Generates a random emo username.'
)
parser.add_argument(
    'source',
    help='the directory or file to generate from',
    type=Path
)
parser.add_argument(
    '-r', '--recursive',
    action='store_true',
    help="recursively travel through directories"
)
# parser.add_argument(
#     '-v', '--verbose',
#     action='store_true',
#     help="print information about file generation"
# )
parser.add_argument(
    '--version',
    action='store_true',
    help="prints software version and exits"
)
args = parser.parse_args()

if __is_python_file(args.source):
    __parse_file(args.source)
elif os.path.isdir(args.source):
    for file in (Path(args.source).glob('**/*') if args.recursive else Path(args.source).glob('*')):
        __parse_file(file)

else:
    print(f'{NAME}: source is not python file or directory')
    parser.print_usage()
    sys.exit(1)
