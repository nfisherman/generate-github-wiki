#!/usr/bin/env python3

import argparse, sys, os, re, time, timeit, traceback
from mimetypes import guess_type
from pathlib import Path
from typing import Final

NAME: Final[str] = 'gengithubwiki'
VERSION: Final[str] = '0.1.0'

class Function:
    """
    Represents the data of a function within a class
    """
    def __init__(self, signature: str, description: str = "", args: dict[str, str] = {}, returns_type: str = "", returns_description: str = ""):
        self.signature: dict[str, str] = signature
        self.description: dict[str, str] = description
        self.args: list[dict[str, str]] = args
        self.returns_type: str = returns_type
        self.returns_description: str = returns_description

    def __repr__(self):
        result: list[str] = [f'Signature: {self.signature} (Function)']
        result.append(f'Description: {self.description}')
        result.append(f'Args: {self.args}')
        result.append(f'Returns: {self.returns_type}: {self.returns_description}')
        return '\n'.join(result)

class Document:
    """
    Represents the data of a document representing a class.
    """
    def __init__(self, class_name: str, description: str = "", functions: list[Function] = []):
        self.class_name: str = class_name
        self.description: str = description
        self.functions: list[Function] = functions

    def __repr__(self) -> str:
        result: list[str] = [f'Class Name: {self.class_name} (Class)']
        result.append(f'Description: {self.description}')
        result.append('Functions:')
        for function in self.functions:
            result.append(f'- {function}\n')
        return '\n'.join(result)

def __is_python_file(file: Path) -> bool:
    return guess_type(file)[0] == 'text/x-python'

def __parse_file(file: Path) -> list[Document]:
    """
    Takes a file and extracts the data from each present docustring.
    Each class is given its own document.

    Args:
        file (Path): the file to extract from

    Returns:
        list[Document]: a list containing all classes within the file, empty
                        list if none
    """
    intentional_newline: Final[str] = '\n\n'
    
    documents: list[Document] = []

    def is_docustring(string: str):
        return string == '"""' or string == "'''"

    if __is_python_file(file):
        with open(file, "r") as file:
            current_document: Document = None
            current_function: Function = None
            docustring: bool = False # Flags the start of a function/class
            building_class: bool = False # Flags that a class is building
            class_signature: str = None
            building_function: bool = False # Flags that a function arg or return is building
            function_signature: str = None
            arg: list[str] = [None, None] # entry into current_function.args; [key, description]
            args: bool = False # Flags that function args are building
            returns: bool = False # Flags that function returns are building

            for line in file:
                stripped_line: str = line.strip()
                # start class (document) processing
                if stripped_line.startswith('class'):
                    class_signature = stripped_line.replace('class ', '').replace(':', '').strip()
                    # Skip private classes
                    if class_signature.startswith('_'):
                        continue
                    docustring = True
                    building_class = True
                    continue
                # start function processing
                if stripped_line.startswith('def'):
                    function_signature = re.sub(
                        r'->(.*)',
                        '',
                        re.sub(
                            r'\([^)]*\)',
                            '', 
                            stripped_line.replace('def ', '')
                        )
                    ).strip()
                    if function_signature.startswith('_'):
                        continue
                    docustring = True
                    building_class = False
                    building_function = True
                    continue

                if not (building_class or building_function):
                    continue
                
                # Check to see if class/function has a docustring
                if docustring:
                    if not is_docustring(stripped_line):
                        building_class = False
                        building_function = False
                    elif building_class:
                        # Create new class file
                        documents.append(Document(class_signature))
                        current_document = documents[-1]
                        current_document.functions = []
                        current_function = None
                    elif building_function:
                        # Create new function entry to class file
                        current_document.functions.append(Function(function_signature))
                        current_document.functions[-1].args = {}
                        current_function = current_document.functions[-1]
                    docustring = False
                    continue

                # Stop building if at end of docustring
                if is_docustring(stripped_line):
                    # save changes
                    if current_function != None:
                        current_function.description = current_function.description.strip()
                        current_document.functions[-1] = current_function
                    current_document.description = current_document.description.strip()
                    documents[-1] = current_document

                    # only reset building_class flag if we reach a new class
                    building_class = None
                    class_signature = None
                    building_function = False
                    function_signature = None
                    arg = [None, None] # [key, description]
                    args = False
                    returns = False
                    continue

                is_new_line: Final[bool] = re.sub(r'^[^\S\r\n]+|[^\S\r\n]+$', '', line) == '\n'
                if building_function:
                    match stripped_line:
                        case 'Args:':
                            args = True
                            continue
                        case 'Returns:':
                            args = False
                            returns = True
                            arg = [None, None]
                            continue
                        case _:
                            if not (args or returns):
                                current_function.description += intentional_newline if is_new_line else line.strip() + " "
                                continue
                    
                    split_line: list[str] = stripped_line.split(': ')
                    # assign a key if it hasn't been done already
                    if len(split_line) > 1:
                        arg[0] = split_line[0]
                        arg[1] = ': '.join(split_line[1:len(split_line)])
                    else:
                        # preserve intentional newlines
                        if is_new_line:
                            arg[1] += intentional_newline
                        # TODO: preserve multi-level bulleted lists
                        else:
                            # join split words
                            if arg[1][-1] == '-':
                                arg[1] = arg[1][0:len(arg[1])]
                            # ensure spaces between words
                            else:
                                arg[1] += ' '
                            arg[1] += stripped_line
                    
                    if args:
                        current_function.args[arg[0]] = arg[1]
                    else:
                        current_function.returns_type = arg[0]
                        current_function.returns_description = arg[1]
                    current_document.functions[-1] = current_function
                else:
                    current_document.description += intentional_newline if is_new_line else line.strip() + " "

        return documents
    return [] # if no docustrings found

def __create_file(document: Document):
    pass


parser = argparse.ArgumentParser(
    prog=NAME,
    description='Convert docustrings to a format Github wiki can understand.'
)
parser.add_argument(
    'source',
    help='the directory or file to generate from',
    type=Path
)
parser.add_argument(
    '-o', '--output',
    help='the directory to output the files in (default: \'docs\'/)',
    default=Path('docs'),
    type=Path
)
parser.add_argument(
    '-r', '--recursive',
    action='store_true',
    help="recursively travel through directories"
)
parser.add_argument(
    '-e', '--epilog',
    help="text to put at the end of files (default: '*Made with gengithubwiki*')",
    default='*Made with [gengithubwiki](https://github.com/nfisherman/generate-github-wiki)*'
)
parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help="print information about file generation"
)
parser.add_argument(
    '--version',
    action='version',
    version=f'{NAME} {VERSION}'
)
args = parser.parse_args()

def __log(message: str):
    if args.verbose:
        print(message)

documents: list[Document] = [] 
files_processed: int = 0
files_skipped: int = 0
t_start = timeit.default_timer()
# program is pointed to single python file
if __is_python_file(args.source):
    parsed_files: list[Document] = None
    t1 = timeit.default_timer()
    try:
        __log(f'Processing {args.source}')
        parsed_files = __parse_file(args.source)
    except Exception as e:
        t2 = timeit.default_timer()
        execution_time: str = f'{t2-t1:.3f}'
        print(f'{NAME}: failed to process {args.source} ({execution_time}s)')
        files_skipped += 1
        __log(traceback.format_exc())
        
    if parsed_files != None:
        if len(parsed_files) > 0:
            documents += parsed_files
            t2 = timeit.default_timer()
            execution_time: str = f'{t2-t1:.3f}'
            __log(f'{args.source} ready to write ({execution_time}s)')
            files_processed += len(parsed_files)
        else:
            t2 = timeit.default_timer()
            execution_time: str = f'{t2-t1:.3f}'
            __log(f'{args.source} contains no classes, skipping write')
            files_skipped += 1
# program is pointed to a directory
elif os.path.isdir(args.source):
    # recursive flag
    for file in (Path(args.source).glob('**/*') if args.recursive else Path(args.source).glob('*')):
        if os.path.isdir(file):
            continue
        parsed_files: list[Document] = None
        t1 = timeit.default_timer()
        try:
            __log(f'Processing {args.source}')
            parsed_files = __parse_file(args.source)
        except Exception as e:
            t2 = timeit.default_timer()
            execution_time: str = f'{t2-t1:.3f}'
            print(f'{NAME}: failed to process {args.source} ({execution_time}s)')
            files_skipped += len(parsed_files)
            __log(traceback.format_exc())
            
        if parsed_files != None:
            if len(parsed_files) > 0:
                documents += parsed_files
                t2 = timeit.default_timer()
                execution_time: str = f'{t2-t1:.3f}'
                __log(f'{args.source} ready to write ({execution_time}s)')
                files_processed += 1
            else:
                t2 = timeit.default_timer()
                execution_time: str = f'{t2-t1:.3f}'
                __log(f'{args.source} contains no classes, skipping write')
                files_skipped += 1
else:
    print(f'{NAME}: source is not a python file or a directory')
    parser.print_usage()
    sys.exit(1)

if len(documents) > 0:
    for document in documents:
        output_file = args.output / Path(f'{document.class_name}.md')
        temp_file = args.output / Path(f'.{str(abs(hash(document.class_name)))[0:9]}_{document.class_name}.tmp')
        args.output.mkdir(parents=True, exist_ok=True)
        # write content
        t1 = timeit.default_timer()
        with open(output_file, 'w') as file:
            file.write(f'# {document.class_name}\n\n')
            file.write(f'{document.description}\n')
            for function in document.functions:
                file.write(f'\n## {function.signature}\n\n')
                file.write(f'{function.description}\n\n')
                if len(function.args) > 0:
                    file.write(f'### Arguments\n\n')
                    for arg in function.args:
                        split_arg_key: list[str] = arg.split(' ')
                        arg_type: str = ""
                        if '(' in split_arg_key[1]:
                            arg_type = f' (``{split_arg_key[1][1:len(split_arg_key[1]) - 1]}``)'
                        file.write(f'{split_arg_key[0]}{arg_type}: {function.args[arg]}\n\n')
                if len(function.returns_type) > 0:
                    file.write(f'### Returns\n\n')
                    file.write(f'``{function.returns_type}``: {function.returns_description}\n')
            if len(args.epilog) > 0:
                file.write('\n---\n\n')
                file.write(f'{args.epilog}\n')
        # cleanup
        prev_line: str = None
        with open(args.output / Path(f'{document.class_name}.md'), 'r+') as source, open(temp_file, "w") as target:
            for line in source:
                if prev_line == '\n' and prev_line == line:
                    continue
                target.write(line)
                prev_line = line
        os.replace(temp_file, output_file)

t_end = timeit.default_timer()
print(f'Created {files_processed} documents and skipped {files_skipped} ({t_end - t_start:0.3f}s)')
