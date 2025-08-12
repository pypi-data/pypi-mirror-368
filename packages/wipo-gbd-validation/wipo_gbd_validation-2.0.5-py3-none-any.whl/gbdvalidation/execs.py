import os
import difflib
import argparse
import traceback

from tabulate import tabulate
from gbdvalidation.engine import RuleEngine


def build_command_parser(options, doc):
    """Argparse builder
    @param options: the dict of config options
    @pram doc: the helper for the command
    return parsed args"""
    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    for config in options:
        name = config.pop('name')
        parser.add_argument(*name, **config)
    return parser.parse_args()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run():
    """Run function for CLI"""
    doc = """
    Tranform a pipeline form a format to another
    """
    configs = [{
        'name': ['-f', '--file'],
        'type': str,
        'dest': 'file_input',
        'help': 'the file that needs transformation'
    }, {
        'name': ['-s' '--string'],
        'type': str,
        'dest': 'string_input',
        'help': 'the string that needs transformation'
    }]

    args = build_command_parser(configs, doc)

    validator = RuleEngine()
    errors = validator.validate(input_file=args.file_input, input_string=args.string_input)
    display = [
        ['Error code', 'Severity', 'Field', 'Type']
    ]
    for error in errors:
        string_color = "%s%s%s"
        if error['severity'] in ['CRITICAL', 'ERROR']:
            string_color = string_color % (bcolors.FAIL, error['severity'], bcolors.ENDC)
        elif error['severity'] in ['WARNING']:
            string_color = string_color % (bcolors.WARNING, error['severity'], bcolors.ENDC)
        elif error['severity'] in ['INFO']:
            string_color = string_color % (bcolors.OKGREEN, error['severity'], bcolors.ENDC)
        else:
            string_color = string_color % (bcolors.OKBLUE, error['severity'], bcolors.ENDC)

        display.append([
            error['code'],
            string_color,
            error['field'],
            error['type']
        ])
    print(tabulate(display[1:], headers=display[0]))


def printProgressBar(iteration, total, prefix = '', suffix = '',
                     decimals=1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

def _run_per_file(path):
    res = ''
    error = None
    try:
        validator = RuleEngine()
        res = validator.validate(input_file=path)
    except Exception as e:
        error = traceback.format_exc()
    return res, error

def bulk_run():
    doc = """
    Validates a full dataset
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection'
    }]
    args = build_command_parser(configs, doc)
    xmls_to_run = []
    for root, dirs, files in os.walk(args.path):
        for f in files:
            file_path = os.path.join(root, f)
            if f.endswith('.json'):
                full_appnum = f.replace('.json', '')
                run_id = None
                tmp = full_appnum.split('_')
                if len(tmp) > 1 and '.' in tmp[-1]:
                    run_id = tmp[-1]
                    appnum = '_'.join(tmp[0:-1])
                else:
                    appnum = full_appnum
                xmls_to_run.append({
                    'path': file_path,
                    'run_id': run_id,
                    'appnum': appnum
                })
    print("Will check over %s files" % len(xmls_to_run))
    printProgressBar(0, len(xmls_to_run),
                     prefix='Progress:', suffix='Complete', length=50)
    i = 0
    for xml in xmls_to_run:
        res, error = _run_per_file(xml['path'])
        xml['errors'] = res
        xml['exceptions'] = error
        printProgressBar(i + 1, len(xmls_to_run),
                         prefix='Progress:', suffix='Complete', length=50)
        i += 1
    display = [
        ['Nb.', 'Path', 'Error code', 'Severity', 'Field', 'Type']
    ]
    counter = 0
    for xml in xmls_to_run:
        if xml['errors']:
            counter += 1
            errors = xml['errors']
            for error in errors:
                string_color = "%s%s%s"
                if error['severity'] in ['CRITICAL', 'ERROR']:
                    string_color = string_color % (bcolors.FAIL, error['severity'], bcolors.ENDC)
                elif error['severity'] in ['WARNING']:
                    string_color = string_color % (bcolors.WARNING, error['severity'], bcolors.ENDC)
                elif error['severity'] in ['INFO']:
                    string_color = string_color % (bcolors.OKGREEN, error['severity'], bcolors.ENDC)
                else:
                    string_color = string_color % (bcolors.OKBLUE, error['severity'], bcolors.ENDC)
                display.append([
                    '%s' % counter,
                    xml['path'],
                    error['code'],
                    string_color,
                    error['field'],
                    error['type']
                ])
        if xml['exceptions']:
            print('Exception validating file %s: %s' % (xml['path'], xml['exceptions']))
    print(tabulate(display[1:], headers=display[0]))
