#!/usr/bin/env python3
import sys, json, re, os, ast, inspect, datetime, time, logging, logging.config, html, shutil, platform
from os import isatty
from sys import exit
from typing import Any, Dict, Optional
# import filters as Filters

jtable_path = os.path.dirname(os.path.abspath(__file__))

if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)
from logger import CustomFormatter, CustomFilter, _ExcludeErrorsFilter, logging_config

import version
import tabulate
import yaml

import functions
Filters = functions
Plugin = functions.Plugin
running_context = functions.running_context()

def stdin_has_data():
    """Retourne True si des données sont envoyées sur stdin (ex: via pipe ou redirection)"""
    return not sys.stdin.isatty()

class Inspect:
    def __init__(self):
        self.out = []
    def add_row(self,row):
        self.out = self.out + [ [row[0]] + [row[1]] ]
        logging.info("Covering " + " / ".join(Filters.flatten([ [row[0]] + [row[1]] ])))
    def view_paths(self,dataset,path="", max_depth=0):
        self.cover_data(dataset,path="", max_depth=0)
        return self.out
    def cover_data(self,dataset,path="", max_depth=0):
        if type(dataset) is dict:
            for key,value in dataset.items():
                if " " in str(key):
                    the_path = path + "['" + str(key) + "']"
                else:
                    if path == "":
                        the_path = path + str(key)
                    else:
                        the_path = path + "." + str(key)
                self.cover_data(value,the_path )
        elif type(dataset) is list:
            index=0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
                # logging.warning(f"the_path: {the_path}")
                index += 1
                self.cover_data(item,the_path)
        else:
            self.add_row([path] + [str(dataset)])

class JtableCli:
    def __init__(self):
        self.path = ""
        self.dataset = {}
        
        # global BaseLoader,Environment
        # from jinja2 import Environment, BaseLoader

        
    def parse_args(self):

        select = []
        queryset = {}
        self.tabulate_var_name="stdin"
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        parser = argparse.ArgumentParser(
            prog='jtable',
            description='Tabulate your JSON/Yaml data and transform it using Jinja',
            add_help=False)

        subparsers = parser.add_subparsers(dest='command')
        # load_parser = subparsers.add_parser('load')
        load_parser = argparse.ArgumentParser(add_help=False)

        # load_parser.add_argument("-h", "--help",nargs="*", help = "Show this help")
        load_parser.add_argument("-p", "--json_path", help = "json path")
        load_parser.add_argument("-s", "--select", help = "select key_1,key_2,...")
        load_parser.add_argument("-w", "--when", help = "key_1 == 'value'")
        load_parser.add_argument("-f", "--format", help = "Table format applied in simple,json,th,td... list below")
        load_parser.add_argument("-us", "--unselect", help = "Unselect unwanted key_1,key_2,...")
        load_parser.add_argument("--inspect", action="store_true", help="Inspect stdin")
        # load_parser.add_argument("-jf", "--json_file", help = "Load json")
        load_parser.add_argument("-vq", "--view_query", action="store_true", help = "View query")
        parser.add_argument('--version', action='version', version=version.__version__)
        load_parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
        load_parser.add_argument('-d', '--debug', action="store_true", help='Add code row number in log')
        load_parser.add_argument('-o', '--stdout', help='Ovewrite applied ouput filter, default: {{ stdin | jtable(queryset=queryset) }}')
        load_parser.add_argument('-pf', '--post_filter', help='Additionnal filter to apply on stdout, eg: jtable ..-f json -pf "from_json | to_nice_yaml"')
        load_parser.add_argument('-c', '--context', help='Add context')
        # load_parser.add_argument('file', nargs='?', help='Path to JSON file (or piped via stdin)')
        # args = parser.parse_args()
        global terminal_size
        terminal_size = shutil.get_terminal_size((80, 20))  # Largeur par défaut 80, hauteur 20

        # parse_known_args = load_parser.parse_known_args()[0]
        # print(parse_known_args)

        load_json_parser = subparsers.add_parser(
        'load_json', parents=[load_parser], help='Load JSON dataset'
        )

        load_yaml_parser = subparsers.add_parser(
        'load_yaml', parents=[load_parser], help='Load YAML dataset'
        )

        load_json_files_parser = subparsers.add_parser(
        'load_json_files', parents=[load_parser], help='Load multiple JSON files'
        )

        load_yaml_files_parser = subparsers.add_parser(
        'load_yaml_files', parents=[load_parser], help='Load multiple YAML files'
        )

        play_parser = subparsers.add_parser(
        'play', parents=[load_parser], help='Execute a query file (YAML)'
        )

        load_json_parser.add_argument('file', nargs='?', help='Path to JSON file (or piped via stdin)')
        load_yaml_parser.add_argument('file', nargs='?', help='Path to YAML file (or piped via stdin)')
        load_json_files_parser.add_argument('files', nargs='+', help='File patterns for JSON files (e.g., "folder/*/*.json" or "{var_name}:folder/*/*.json")')
        load_yaml_files_parser.add_argument('files', nargs='+', help='File patterns for YAML files (e.g., "folder/*/*.yml" or "{var_name}:folder/*/*.yml")')
        play_parser.add_argument('query_file', help='Path to query file (YAML)')
        # exit(0)

        # Check for --version first
        if len(sys.argv) > 1 and '--version' in sys.argv:
            args = parser.parse_args()
            return
            
        if len(sys.argv) > 1 and sys.argv[1] in {'load_json','load_yaml','load_json_files','load_yaml_files','play'}:
            # Commande explicite → on parse normalement
            args = parser.parse_args()
        elif stdin_has_data():
            # Pas de commande explicite mais stdin actif → injecter "load_json" avant les arguments
            sys.argv.insert(1, 'load_json')
            args = parser.parse_args()
        else:
            # Pas de commande explicite et pas de stdin → afficher aide
            parser.print_help()
            sys.exit(1)


        # print(args.debug)

        if os.environ.get('JTABLE_LOGGING') == "DEBUG" or args.debug:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
        else:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s %(class_name)s.%(parent_function)-15s | %(levelname)s %(message)s'

        
        if args.verbose == 0:
            logging_config['handlers']['console_stderr']['level'] = 'WARNING'
        if args.verbose == 1:
            logging_config['handlers']['console_stderr']['level'] = 'INFO'
        elif args.verbose == 2:
            logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging.config.dictConfig(logging_config)
        logging.info(f"running_context: {running_context}")
        # logging_format = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s'
        
        if args.context:
            print(f"Loading context from: {args.context}")
            logging.info(f"Loading context from: {args.context}")
            queryset = json.loads(args.context)
            print(f"queryset: {queryset}")
            exit(0)



                
        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            logging.info("stdin is a pipe")
            for line in sys.stdin:
                stdin = stdin + line
            self.dataset = { self.tabulate_var_name: stdin }
        # if args.help:
        #     if args.help == ['color']:
        #         jtable_color = [name for name, func in inspect.getmembers(Styling().__init__())]
        #         print(Styling().view_all_colors())
        #         exit(1)
        #     elif args.help[0] == 'b64decode':
        #         from .functions import b64decode
        #         print(b64decode.__doc__)
        #         exit(1)
        #     else:
        #         print(f"Error: No help available for '{args.help[0]}'")
        #         exit(1)
        if not is_pipe and not args.stdout and not args.command:

            parser.print_help(sys.stdout)
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            jtable_plugins = [name for name, func in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
            print(f"\njtable core filters:\n   {', '.join(jtable_core_filters)}\n")
            tablulate_formats = next((value for name, value in inspect.getmembers(tabulate) if name == 'tabulate_formats'), None)
            jtable_formats = ['json','gitlab_json_table','td','th']
            print(f"tabulate formats:\n   {', '.join(sorted(tablulate_formats))}\n")
            print(f"jtable additional formats:\n   {', '.join(sorted(jtable_formats))}\n")
            print(f"jtable plugins:\n   {', '.join(jtable_plugins)}\n")
            print(f"More help with jtable -h <help topic>")
            print(f"  colors:\n    type jtable -h color | jtable\n")
            exit(1)

        # if args.json_file:
        #     logging.info(f"loading json file: {args.json_file}")
        #     got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
        #     if re.match(got_variable_name_pattern, args.json_file):
        #         self.tabulate_var_name = args.json_file[1:].split('}:')[0]
        #         file_name = ':'.join(args.json_file.split(':')[1:])
        #     else:
        #         self.tabulate_var_name = "input_1"
        #         file_name = args.json_file
        #     logging.info(f"file_name: {file_name}, self.tabulate_var_name: {self.tabulate_var_name}")
        #     with open(file_name, 'r') as input_yaml:
        #         self.dataset = {**self.dataset, **{ self.tabulate_var_name: yaml.safe_load(input_yaml) } }

        # print(f"args.command: {args.command}")

        def load_multiple_inputs(file_search_string,format):
            logging.info(f"loading {format} files: {file_search_string}")
            err_help = f"\n[ERROR] {format}_files must looks like this:\n\n\
                jtable load_{format}_files \"{{target_var_name}}:folder_1/*/*/config.{format}\"\n"
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, file_search_string):
                logging.info(f"Contains variable name file_names: {file_search_string}")
                splitted_path = file_search_string[1:].split('}:')
                path=splitted_path[1]
                self.tabulate_var_name = splitted_path[0]
            else:
                self.tabulate_var_name = "input_1"
                logging.info(f"Adding var_name: {self.tabulate_var_name}")
                path = file_search_string
            logging.info(f"var_name: {self.tabulate_var_name}, path: {path}")
            logging.info(f"path: {path}")
            if running_context['shell_family'] == "windows":
                cmd = f"dir /s /b {path}"
                logging.info(f"cmd: {cmd}")
                files_str = os.popen("dir /s /b " + path).read()
            else:
                files_str = os.popen("ls -1 " + path).read()
            files_str = os.popen("ls -1 " + path).read()
            logging.info(f"files_str: {files_str}")
            file_list_dataset = []
            for file_name_full_path in files_str.split('\n'):
                if file_name_full_path != '':
                    with open(file_name_full_path, 'r') as input_file:
                        try:
                            if format == 'json':
                                file_content = json.load(input_file)
                            else:
                                file_content = yaml.safe_load(input_file)
                            if running_context['shell_family'] == "windows":
                                sep = "\\"
                                file_path = sep.join(file_name_full_path.split('\\')[:-1])
                                file_name = file_name_full_path.split('\\')[-1]
                            else:
                                file_path = "/".join(file_name_full_path.split('/')[:-1])
                                file_name = file_name_full_path.split('/')[-1]
                            file = { 
                                    "name": file_name,
                                    "path": file_path,
                                    "content": file_content
                                    }
                            file_list_dataset = file_list_dataset + [{ **file }]
                        except Exception as error:
                            logging.warning(f"fail loading file {file_name_full_path}, skipping")
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: file_list_dataset } }

        if args.command == 'load_json' or args.command == 'load_yaml':
            if stdin_has_data() and not args.file:
                dict_content = stdin
            else:
                file_type = "_".join(args.command.split('_')[1:]).upper()
                if not args.file:
                    logging.error(f"No {file_type} file provided, please provide a file or pipe {file_type} content to stdin")
                    exit(1)
                logging.info(f"loading {args.command} file: {args.file}")
                self.tabulate_var_name = "input"
                file_name = args.file
                with open(file_name, 'r') as file_content:
                    try:
                        if args.command == 'load_yaml':
                            dict_content = yaml.safe_load(file_content)
                        else:
                            # Assume JSON file
                            dict_content = json.load(file_content)
                    except Exception as error:
                        logging.error(f"Failed to load {args.command} file {file_name}, error was:\n{error}")
                        logging.error(f"File path: {os.path.abspath(file_name)}")
                        logging.error(f"File exists: {os.path.exists(file_name)}")
                        if os.path.exists(file_name):
                            logging.error(f"File size: {os.path.getsize(file_name)} bytes")
                        exit(2)
                
                # Check if the loaded content is None
                if dict_content is None:
                    logging.error(f"Loaded content from {file_name} is None. Please check the file content.")
                    exit(2)
                    
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: dict_content } }
        elif args.command == 'load_json_files' or args.command == 'load_yaml_files':
            file_type = "_".join(args.command.split('_')[1:]).upper()
            for file_pattern in args.files:
                load_multiple_inputs(file_pattern, file_type.lower())
        elif args.command == 'play':
            logging.info(f"loading query file: {args.query_file}")
            with open(args.query_file, 'r') as file:
                try:
                    query_file = yaml.safe_load(file)
                except Exception as error:
                    logging.error(f"Fail to load query file {args.query_file}, check Yaml format")
                    logging.error(f"error was:\n{error}")
                    exit(2)
                
            if 'vars' in query_file:
                if 'queryset' in query_file['vars']:
                    queryset = query_file['vars']['queryset']
            if 'secrets' in query_file:
                global secrets
                secrets = query_file['secrets']
            # print(f"json_content: {json_content}")
            # exit(0)

            # got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            # if re.match(got_variable_name_pattern, args.json_file):
            #     self.tabulate_var_name = args.json_file[1:].split('}:')[0]
            #     file_name = ':'.join(args.json_file.split(':')[1:])
            # else:
            #     self.tabulate_var_name = "input_1"
            #     file_name = args.json_file
            # logging.info(f"file_name: {file_name}, self.tabulate_var_name: {self.tabulate_var_name}")
            # with open(file_name, 'r') as input_yaml:
            #     self.dataset = {**self.dataset, **{ self.tabulate_var_name: yaml.safe_load(input_yaml) } }
        

        
        if args.json_path:
            new_path = args.json_path
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            queryset['path'] = new_path

        # Process query file if it was loaded (either from play command or other sources)
        if 'query_file' in locals() and query_file:

            if 'vars' in query_file:
                vars = {}
                for key,value in query_file['vars'].items():
                    logging.info(f"Covering vars, key: {key}")
                    jinja_eval = Templater(template_string=str(value), static_context=self.dataset).render({},eval_str=True)
                    vars.update({key: jinja_eval})
                    self.dataset = {**self.dataset,**vars, **{"vars": vars}}

            
        if 'select' in queryset:
            select = queryset['select']

        if args.unselect:
           queryset['unselect'] = args.unselect

        if args.select:
            queryset['select'] = args.select

        if args.when:
            queryset['when'] = args.when

        if not 'path' in queryset:
            queryset['path'] = "{}"
                    
        if not "format" in queryset:
            queryset['format'] = 'simple'

        if args.format:
            queryset['format'] = args.format

        if args.view_query:
            original_format = queryset['format']
            queryset['format'] = "th"
            
        if args.stdout:
            out_expr = args.stdout
        else:
            if self.tabulate_var_name == "stdin":
                if args.post_filter:
                    original_out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | jtable(queryset=queryset) }}"
                    out_expr = "{{ " + self.tabulate_var_name + f" | from_json_or_yaml | jtable(queryset=queryset) | {args.post_filter} }}}}"
                else:
                    out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | jtable(queryset=queryset) }}"
            else:
                out_expr = "{{ " + self.tabulate_var_name + " | jtable(queryset=queryset) }}"


        if 'query_file' in locals() and query_file:
            if 'stdout' in query_file:
                out_expr = query_file['stdout']
            
        if args.inspect:
            if self.tabulate_var_name == "stdin":
                inspected_paths = Inspect().view_paths(yaml.safe_load(stdin))
            else:
                inspected_paths = Inspect().view_paths(self.dataset[self.tabulate_var_name])
            tbl = tabulate.tabulate(inspected_paths,['path','value'])
            print(tbl)
            return

        if args.view_query:
            if args.post_filter:
                out = Templater(template_string=original_out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            else:
                out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            query_file_out = {}
            query_set_out = {}
            fields = out
            if select == []:
                for field in fields:
                    select = select + [ {'as': field, 'expr': field }  ]
            query_set_out['path'] = queryset['path']
            query_set_out['select'] = select
            query_set_out['format'] = original_format
            if args.when:
                query_set_out['when'] = args.when
            query_file_out['vars'] = {'queryset': query_set_out }
            # if args.post_filter:
            #     query_file_out['vars'].update({'prepa_stdout': f"{out_expr}" })
            # query_file_out['stdout'] = f"{{{{ prepa_stdout | {args.post_filter} }}}}"
            query_file_out['stdout'] = out_expr



            yaml_query_out = yaml.dump(query_file_out, allow_unicode=True,sort_keys=False)
            print(yaml_query_out)
        else:
            logging.info(f"queryset: {queryset}")
            logging.info(f"out_expr: {out_expr}")
            # logging.info(str({**self.dataset,**{"queryset": queryset}}))
            # exit(0)
            out = Templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=False)
            print(out)

class JtableCls:
    def __init__(self, render="jinja_native"):
        logging.info(f"Initilizing render: {render}")
        self.td = []
        self.th = []
        self.table_headers = []
        self.json = []
        self.render = render
        self.splitted_path = []
        self.when = []
        self.select = []
        self.unselect = []
        self.views = {}
        self.path = "{}"
        self.format = ""

    def cross_path(self, dataset, path, cross_path_context = {} ):
        level = len(path)
        if level > 1:
            # logging.info(f"path: {path}")
            next_path = path[1:]
            current_path = str(path[0])
            current_path_value = "unknown"
            if current_path[0:2] == "['":
                current_path_value = current_path[2:-2]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value], next_path, cross_path_context = cross_path_context)
                else:
                    logging.error('keys dataset were:')
                    logging.error(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
            elif current_path[0] == ".":
                current_path_value = current_path[1:]
                if current_path_value in list(dataset):
                    self.cross_path(dataset[current_path_value],next_path, cross_path_context = cross_path_context)
                else:
                    logging.info(list(dataset))
                    logging.error(current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    # exit(1)
                    
            elif current_path[0] == "[":
                current_path_value = current_path[1:-1]
                if int(current_path_value) <= len(dataset):
                    self.cross_path(dataset[int(current_path_value)],next_path, cross_path_context = cross_path_context)
                    
                else:
                    logging.error( current_path + " was not found in dataset level: " + str(len(self.splitted_path) - level))
                    exit(1)
            
            elif current_path[0] == "{":
                item_name = current_path[1:-1]
                if level > 0:
                    if type(dataset) is dict:
                        for key,value in dataset.items():
                            next_path = path[1:]
                            # new_cross_path_context = {item_name: {"key": key, "value": value}}
                            cross_path_context = { **cross_path_context, **{item_name: {"key": key, "value": value}}}
                            self.cross_path(dataset[key],next_path,cross_path_context=cross_path_context)
                            
                    elif type(dataset) is list:
                        index = 0
                        for item in dataset:
                            next_path = path[1:]
                            # new_cross_path_context = { item_name: item }
                            cross_path_context = { **cross_path_context, **{ item_name: item }}
                            self.cross_path(dataset[index],next_path,cross_path_context=cross_path_context)
                            index += 1
                else:
                    logging.info(f"item_name: {item_name}")
                    self.render_table(dataset=dataset,select=self.select, item_name = item_name, context = cross_path_context)
            else:
                logging.info("[ERROR] was looking for path...")
                exit(1)
        else:
            item_name = path[0][1:-1]
            # logging.info(f"item_name: {item_name}")
            self.render_table(dataset=dataset,select=self.select, item_name = item_name, context=cross_path_context)
    
    def render_object(self, dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}):
        # exit(0)
        for query_item,query_data in queryset.items():
            logging.info(f"query_item: {query_item}")
            # exit(0)
            if query_item == "select":
                self.select = query_data
            elif query_item == "unselect":
                self.unselect = query_data
            elif query_item == "path":
                # logging.info(f"self.path query_data: {query_data}")
                self.path = query_data
            elif query_item == "views":
                self.views = query_data
            elif query_item == "when":
                self.when = query_data
            elif query_item == "format":
                self.format = query_data
            else:
                raise Exception(f"the queryset argument contains a non accepted key: {query_item}")
            
        self.path = path if path != "{}" else self.path
        self.select = select if select != [] and select != "" else self.select
        self.unselect = unselect if unselect != [] and unselect != "" else self.unselect
        self.views = views if views != {} else self.views
        # self.when = when if when != [] else self.when
        self.when = when if when != [] and when != "" else self.when
        logging.info(f"when: {self.when.__class__.__name__}")
        if self.when.__class__.__name__ == "str":
            self.when = self.when.split(',')
        logging.info(f"when: {self.when}")
        # exit(0)
        self.format = format if format != "" else self.format
        self.context = context
        logging.info(f"unselect: {self.unselect}")

        self.dataset = dataset
        
        for k,v in self.views.items():
            self.views = {**self.views, **{ k: '{{' + str(v) + '}}' } }
        from jinja_path_splitter import JinjaPathSplitter

        self.splitted_path = JinjaPathSplitter().split_path(self.path)
        if self.splitted_path[0] == "['']":
            self.splitted_path[0] = "['input']"
            self.dataset = {"input": self.dataset}
        
        logging.info(f"Crossing paths")
        self.cross_path(self.dataset, self.splitted_path )

        if self.format == "json":
            return json.dumps(self.json)
        elif self.format == "th":
            return self.th
        elif self.format == "td":
            return self.td
        elif self.format == "github":
            return tabulate.tabulate(self.td,self.th,tablefmt="github")
        elif self.format == "gitlab_json_table":
            out_dataset = {
                "fields": [ { "key": key, "sortable": "true" } for key in self.th ],
                "items": self.json,
                "filter": True,
                "caption": ""
            }
            return f"```json:table\n{json.dumps(out_dataset,indent=2, separators=(',', ': '))}\n```"
        elif self.format == "html":
            return tabulate.tabulate(self.td,self.th,tablefmt="unsafehtml")
        else:
            return tabulate.tabulate(self.td,self.th,tablefmt=self.format)
        
        # return out_return[self.format]
    
    def render_table(self, dataset, select=[], item_name='', context={}):
        stylings = []
        logging.info(f"unselect: {self.unselect}")
        if len(select) > 0:
            logging.info(f"select: {select.__class__.__name__}")
            if select.__class__.__name__ == "str":
                expressions = fields_label = select.split(",")
            else:
                expressions = [expressions['expr'] for expressions in select]
                stylings = [(stylings['styling'] if 'styling' in stylings else []) for stylings in select]
                fields_label = [fields_label['as'] for fields_label in select]
        else:
            fields = path_auto_discover().discover_paths(dataset)
            fields_label = list(map(lambda item: '.'.join(item), fields))
            item_name = 'item' if item_name == '' else item_name
            expressions = list(map(lambda item:  item_name + '[\'' + '\'][\''.join(item) + '\']' , fields))
        
        if self.unselect != [] and self.unselect != "":
            for field in self.unselect.split(','):
                if field in fields_label:
                    index = fields_label.index(field)
                    del expressions[index]
                    del fields_label[index]
                    if stylings != []:
                        del stylings[index]

        logging.info(f"expressions: {expressions}")
        logging.info(f"fields_label: {fields_label}")
        # exit()

        if type(dataset) is dict:
            dataset_to_cover = []
            for key,value in dataset.items():
                dataset_to_cover = dataset_to_cover + [ {'key': key, 'value': value} ]
        elif type(dataset) is list:
            dataset_to_cover = dataset
        else:
            raise Exception('[ERROR] dataset must be a dict or list, was: ' + str(type(dataset)))

        # static_context = {"dataset": dataset, **context}
        column_templates = []
        for expr in expressions:
            jinja_expr = '{{ ' + expr  + ' }}'
            column_templates = column_templates + [Templater(template_string=jinja_expr, static_context={**context,**self.context},strict_undefined=False)]

        view_templates = []
        for var_name,var_data in self.views.items():
            view_templates = view_templates + [Templater(template_string=str(var_data), static_context={**context,**self.context},strict_undefined=False)]

        when_templates = []
        for condition in self.when:
            when_templates = when_templates + [Templater(template_string=condition, static_context={**context,**self.context},strict_undefined=False)]



        for item in dataset_to_cover:
            row = []
            json_dict = {}

            def when(when=[],when_context={}):
                condition_test_result = True
                for condition in when:
                    jinja_expr = '{{ ' + condition  + ' }}'
                    # logging.info(f"item_name: {item_name}")
                    logging.info(f"when: {when}")
                    # loop_condition_context = item
                    # loop_condition_context = { item_name: item } if item_name != '' else item
                    loop_condition_context = { item_name: item } if (item_name != '' and item_name != 'item' ) else item
                    logging.info(f"loop_condition_context: {loop_condition_context}")
                    logging.info(f"when_context: {when_context}")
                    # loop_condition_context = { item_name: item }
                    condition_template = Templater(template_string=jinja_expr, static_context= {**when_context,**loop_condition_context},strict_undefined=False)
                    condition_test_result = condition_template.render({},eval_str=True)
                    logging.info(f"condition_test_result: {condition_test_result}, type: {type(condition_test_result)}")
                    if condition_test_result == "False" or condition_test_result == False:
                        break
                return condition_test_result

            for expr in expressions:
                loop_context = { item_name: item } if item_name != '' else item
                view_context = {}
                view_index = 0
                for exp_key,exp_val in self.views.items():
                    try:
                        templated_var = view_templates[view_index].render({**loop_context,**view_context},eval_str=True)
                    except Exception as error:
                        logging.error(f"Error while rendering var_name: {exp_key}, exp_val: {exp_val}, error was:\n{error}")
                        exit(1)
                    view_context.update({ exp_key: templated_var })
                    view_index += 1

            if self.when != []:
                condition_test_result = when(when = self.when, when_context = {**self.context,**context,**view_context})
                # logging.warning(f"condition_test_result: {condition_test_result}, type: {type(condition_test_result)}")
            else:
                condition_test_result = True
            
                
            if condition_test_result  == True or condition_test_result == "True":

                column_index = 0
                for expr in expressions:
                    loop_context = { item_name: item } if item_name != '' else item
                    try:
                        value_for_json = value = column_templates[column_index].render({**loop_context,**view_context},eval_str=True)
                    except:
                        break
                    del loop_context
                    if self.format == "html":
                        value = html.escape(str(value))
                    key = fields_label[column_index]
                    if value_for_json != None:
                        json_value = { key: value_for_json }
                        json_dict = {**json_dict, **json_value }
                        del json_value
                        del value_for_json
                    if stylings != []:
                        styling = stylings[column_index]
                        condition_color = True
                        # if styling != []:
                        for styling_attributes in styling:
                            color_conditions = [color_conditions for color_conditions in  styling_attributes['when'] ]
                            # logging.info(color_conditions)
                            condition_color = when(when = color_conditions, when_context = {**context,**view_context})
                            logging.info(f"condition_color: {condition_color}")
                            if condition_color == True or condition_color == "True":
                                value = Styling().apply(value = value,format=self.format, styling_attributes = styling_attributes)
                                # logging.info(f"condition_color value: {value}")

                    row = row + [ value ]
                    del value
                    column_index += 1
                self.json = self.json + [ json_dict ]
                self.td = self.td + [ row ]
        
        
        if fields_label is None:
            headers = list(map(lambda item: '.'.join(item), expressions))
            fields_label = headers
        
        self.th = fields_label
            
        try:
            self.json_content = json.dumps(self.json)
        except Exception as error:

            logging.info(tabulate(self.td,self.th))
            logging.error(f"\nSomething wrong with json rendering, Errors was:\n  {error}")
            exit(2)

class path_auto_discover:
    def __init__(self):
        self.paths = []
        self.fields = []
        self.raw_rows = []
        
    def cover_paths(self,dataset,path=[]):
        if type(dataset) is dict:
            for key,value in dataset.items():
                the_path = path + [ key ]
                self.cover_paths(value,the_path )
        elif type(dataset) is list:
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]
        else:
            self.paths = self.paths + [ path + [dataset] ]
            if path[1:] not in self.fields:
                self.fields = self.fields + [path[1:]]

    def discover_paths(self,dataset):
        
        # Check if dataset is None or empty
        if dataset is None:
            logging.error("Dataset is None. Please check your input data.")
            exit(1)
        
        # when input is dict transform as list like dict2items
        if type(dataset) is dict:
            dataset_as_list = []
            for key,value in dataset.items():
                dataset_as_list = dataset_as_list + [ {'key': key, 'value': value} ]
            dataset = dataset_as_list
        index=0

        try:
            for item in dataset:
                for key,value in item.items():
                    self.cover_paths(value,[str(index),key])
                    index+=1
                self.raw_rows = self.raw_rows + [ item ]
        except(Exception) as error:
            logging.error(f"Something wrong with your dataset, error was:")
            logging.error(f"    {error}")
            logging.error(f"Dataset type: {type(dataset)}")
            logging.error(f"Dataset content: {dataset}")
            exit(1)
        logging.info(f"fields: {self.fields}")
        return self.fields

class Styling:
    def __init__(self):
        self.color_table = [{"name":"Black","ansi_code":30,"hex":"#000000"},{"name":"Red","ansi_code":31,"hex":"#FF0000"},{"name":"Green","ansi_code":32,"hex":"#008000"},{"name":"Yellow","ansi_code":33,"hex":"#FFFF00"},{"name":"Blue","ansi_code":34,"hex":"#0000FF"},{"name":"Magenta","ansi_code":35,"hex":"#FF00FF"},{"name":"Cyan","ansi_code":36,"hex":"#00FFFF"},{"name":"White","ansi_code":37,"hex":"#FFFFFF"},{"name":"Gray","ansi_code":90,"hex":"#808080"},{"name":"LightRed","ansi_code":91,"hex":"#FF8080"},{"name":"LightGreen","ansi_code":92,"hex":"#80FF80"},{"name":"LightYellow","ansi_code":93,"hex":"#FFFF80"},{"name":"LightBlue","ansi_code":94,"hex":"#8080FF"},{"name":"LightMagenta","ansi_code":95,"hex":"#FF80FF"},{"name":"LightCyan","ansi_code":96,"hex":"#80FFFF"},{"name":"LightWhite","ansi_code":97,"hex":"#F0F0F0"}]
    def view_all_colors(self):
        return self.color_table
    def get_color(self,color_name="",format=""):
        color_match=[color for color in self.color_table if color['name'].lower() == color_name.lower() ]
        # logging.info(f"color_match: {color_match}")
        # logging.info(f"color_match: {format}")
        if color_match == []:
            return ""
        else:
            if format == "html":
                color_pallet = "hex"
            elif format == "simple":
                color_pallet = "ansi_code"
            elif format == "github":
                return color_name
            else:
                return ""
        # logging.info(f"color_match: {color_match[0]}")
        return color_match[0][color_pallet]


    def apply(self,value="",format="",styling_attributes={}):
        logging.info(f"value: {value} / format: {format} / styling_attributes: {styling_attributes}")
        value_colorized = ""
        if "style" in styling_attributes:
            color_label = styling_attributes['style'].split(": ")[1]
        else:
            color_label = "white"
        text_formating = 0
        formating = ""
        if "formating" in styling_attributes:
            formating = styling_attributes['formating']
        if formating == "normal" or formating == "":
            text_formating = 0
        elif formating == "bold":
            text_formating = 1
        elif formating == "dim":
            text_formating = 2
        elif formating == "italic":
            text_formating = 3
        elif formating == "underlined":
            text_formating = 4
        else:
            logging.error(f"Unknown formating: {formating}")
            exit(1)
        # color_corresp = self.get_color(color_label,"ansi_code")
        color_corresp = self.get_color(color_label,format)

        if color_corresp == "":
            if format == "html":
                value_colorized  = r'<span style="' + styling_attributes['style'] + ';">' + value + r"</span>"
            else:
                logging.info(f"style '{styling_attributes['style']}' not found, using default")
                # value_colorized = value
                return value

        else:
            if format == "simple":
                value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
            elif format == "github":
                # value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
                # value_colorized = f"$`\textcolor{{red}}{{\text{{Smith}}`$"
                logging.info(f"color_label: {color_label}")
                return r"$`\textcolor{"+ color_label + r"}{\text{" + value + "}}`$"
            elif format == "html":
                value_colorized  = r'<span style="' + styling_attributes['style'] + r';">' + value + r"</span>"
            else:
                value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"

            logging.info(f"format: {format}")   
        return value_colorized

# from jinja2 import nativetypes,StrictUndefined,Undefined,Environment
# from jinja2.sandbox import SandboxedEnvironment

        
class Templater:
    def __init__(self, template_string = "", static_context = {},strict_undefined = True):
        from jinja2 import Environment
        env = Environment()
        self.strict_undefined = strict_undefined
        import random
        self.id = random.randint(0,1000000)

        jtable_core_filters = [name[0] for name in inspect.getmembers(Filters, predicate=inspect.isfunction)]
        for filter_name in jtable_core_filters:
            env.filters[filter_name] = getattr(Filters, filter_name)
        env.filters['jtable'] = JtableCls().render_object
        # logging.info(f"jtable_core_filters: {jtable_core_filters}")

        ####################  Add plugin function ####################
        jtable_core_plugins = [name[0] for name in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
        logging.info(f"jtable_core_plugins: {jtable_core_plugins}")
        class plugin_fct(object):
            def process_plugin(self,*args, **kwargs):
                if len(args) == 0 and len(kwargs) == 0:
                    logging.error("plugin function must have at least one argument in:")
                    exit(3)
                if args[0] not in jtable_core_plugins:
                    logging.error(f"plugin function {args[0]} not found in {', '.join(jtable_core_plugins)}")
                    exit(3)
                method_to_call = getattr(Plugin, args[0], None)
                try:
                    res = method_to_call(*args[1:],**kwargs)
                except Exception as error:
                    logging.error(f"Failed to call plugin function {args[0]}, error was:\n  {str(error)}")
                    exit(3)
                return res
            
        plugin = lambda: plugin_fct().process_plugin
        logging.debug(f"({self.id}) strict_undefined: {strict_undefined}, static_context: {static_context}")
        static_context = {**static_context, **{"plugin": plugin()}}

        ##############################################################
        logging.info(f"({self.id}) compiling template_string: {template_string}")
        logging.info(f"({self.id}) template_string type  {type(template_string)}")
        try:
            self.template = env.from_string(template_string, globals=static_context)
        except Exception as error:
            logging.error(f"({self.id}) Failed to compile template, error was:\n  {str(error)}")
            exit(3)
    
    def render(self, vars, eval_str = False):

        logging.debug(f"({self.id}) Rendering template, self.strict_undefined: {self.strict_undefined}, vars: {vars}")
        
        try:
            out_str = self.template.render(vars)
        except Exception as error:
            if str(error)[0:30] == "'dict object' has no attribute" \
                or str(error)[0:30] == "'list object' has no attribute"\
                or str(error).__contains__("is undefined"):
                    if self.strict_undefined == True:
                        logging.error(f"({self.id}) Failed while rendering context, error was:\n  {str(error)}")
                        logging.error(f"({self.id}) debug strict_undefined: {self.strict_undefined}")
                        logging.error(f"({self.id}) debug vars: {vars}")
                        raise error
                        # out = out_str =""
                    else:
                        out = out_str =""
            else:
                out = out_str = error
                logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                raise out
                # out = out_str =""
            
        if eval_str == True:
            try:
                expr = ast.parse(out_str, mode='eval').body
                expr_type = expr.__class__.__name__
                if expr_type == 'List' or expr_type == 'Dict':
                    out =  ast.literal_eval(out_str)
                elif expr_type == 'Name':
                    out = out_str
                else:
                    out = str(out_str)
            except:
                out = out_str
        else:
            out = out_str
                    
        return out
    
class UnicodeString:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"UnicodeString({repr(self.value)})"

    def __add__(self, other):
        if isinstance(other, (str, UnicodeString)):
            # Convertir en chaîne si `other` est un UnicodeString
            return UnicodeString(self.value + str(other))
        raise TypeError(f"Unsupported operand type(s) for +: 'UnicodeString' and '{type(other).__name__}'")

    def __radd__(self, other):
        # Pour prendre en charge str + UnicodeString
        if isinstance(other, str):
            return UnicodeString(other + self.value)
        raise TypeError(f"Unsupported operand type(s) for +: '{type(other).__name__}' and 'UnicodeString'")

def main():
    try:
        JtableCli().parse_args()
    except KeyboardInterrupt:
        exit(1)
    except Exception as error:
        print(f"Unexpected failure: {error}", file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()