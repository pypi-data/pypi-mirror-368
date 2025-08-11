import sys
import time
import argparse
import random
import os
import traceback
import difflib
import gzip
import multiprocessing
import xml.etree.ElementTree as ET
import concurrent.futures
import pprint

from tabulate import tabulate
from gbdtransformation.parser import Parser


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

parsers = {}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    CRITICAL = '\033[91m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class progress:
    def __init__(self, total):
        self.total = total
        self.done  = 0

    def start(self):
        printProgressBar(0, self.total,
                        prefix='Progress:', suffix='Complete', length=50)

    def advance(self, value):
        self.done = value
        printProgressBar(self.done, self.total,
                        prefix='Progress:', suffix='Complete', length=50)

    def advance_with_step(self, value):
        self.done += value
        printProgressBar(self.done, self.total,
                        prefix='Progress:', suffix='Complete', length=50)


def test():
    doc = """
       Runs regression tests
       """
    configs = [{
        'name': ['--junit'],
        'dest': 'junit',
        'help': 'saves in junit format',
        'action': 'store_true',
        'default': False
    }]
    args = build_command_parser(configs, doc)
    pkg_folder = os.path.dirname(__file__)
    test_to_run = []
    for type in ['brands', 'designs']:
        path = os.path.join(pkg_folder, type)
        for root, dirs, files in os.walk(path):
            if 'tests' in dirs:
                template = os.path.basename(root)
                for file in os.listdir(os.path.join(root, 'tests')):
                    if file.startswith('_'):
                        continue
                    if file.endswith('.out'):
                        continue
                    filename, ext = os.path.splitext(file)
                    input_file_path = os.path.join(root, 'tests', file)
                    out_file_path = input_file_path.replace(ext, '.out')
                    has_output = os.path.exists(out_file_path)
                    test_to_run.append({
                        'template': template,
                        'path': input_file_path,
                        'test_output': has_output,
                        'invalid_output': None
                    })
    for test in test_to_run:
        res, exceptions, error = _run_per_file(
            test['template'], test['path'])
        test['execution'] = res
        test['errors'] = exceptions
        filename, ext = os.path.splitext(test['path'])
        if test['test_output']:
            expected = ''
            with open(test['path'].replace(ext, '.out'), 'r') as f:
                expected = [e.replace('\n', '') for e in f.readlines()]
            delta = difflib.ndiff(expected, res.split('\n'))
            to_outup_diffs = []
            for d in delta:
                if d[0] != ' ':
                    to_outup_diffs.append(d)
                else:
                    if to_outup_diffs:
                        break
                    to_outup_diffs = []
            test['invalid_output'] = '\n'.join(to_outup_diffs)
    display = [
        ['Nb.', 'Template', 'Input', 'Has run?', 'Errors', 'Valid output']
    ]
    counter = 0
    if args.junit:
        total = 0
        errors = 0
        fail = 0
        tests_run_xml = []
        for test in test_to_run:
            if test['errors']:
                tmp = '''<failure type="Conversion error">
                %s
                </failure>''' % test['errors']
            elif test['test_output'] and test['invalid_output']:
                tmp = '''<failure type="Invalid output">
                %s
                </failure>''' % test['invalid_output']
            else:
                tmp = ''
            current = '''
            <testcase classname="%s" name="%s" time="0.001">
             %s
            </testcase>''' % (test['path'], test['template'], tmp)
            total += 1
            if test['errors']:
                errors += 1
            elif test['test_output']:
                if test['invalid_output']:
                    fail += 1
            tests_run_xml.append(current)
        payload = '\n'.join(tests_run_xml)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <testsuite name="integration" tests="%s" errors="%s" failures="%s" skip="0">
            %s
        </testsuite>''' % (total, errors, fail, payload)
        with open('tests.xml', 'w') as f:
            f.write(xml)
    for test in test_to_run:
        counter += 1
        has_run = u'\u2713'
        color = ''
        end_color = ''
        valid_output = "No output to test"
        if test['test_output']:
            valid_output = u'\u2713'
            if test['invalid_output']:
                valid_output = test['invalid_output']
                color = bcolors.WARNING
                end_color = bcolors.ENDC
        if test['errors']:
            valid_output = u'\u2717'
            has_run = u'\u2717'
            color = bcolors.FAIL
            end_color = bcolors.ENDC
            test['errors'] = '\n'.join(['%s%s%s' % (color, e, end_color)
                                        for e in test['errors'].split('\n')])
        display.append([
            '%s%s' % (color, counter), test['template'], os.path.basename(test['path']),
            has_run, test['errors'], '%s%s%s' % (color,
                                                 valid_output, end_color)])
    print(tabulate(display[1:], headers=display[0]))


def _run_per_file(template, path, input_string=None, validate=False):
    parser = Parser(template)
    if input_string:
        data = input_string
    else:
        data = path
    try:
        transformed = parser.run(data, raise_errors=True)
        if validate:
            transformed, errors = parser.validate(transformed, gbd_format=transformed)
            return (transformed, None, errors)
        return (transformed, None, None)
    except Exception as e:
        return (None, traceback.format_exc(), None)


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
    return
    # percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    # filledLength = int(length * iteration // total)
    # bar = fill * filledLength + '-' * (length - filledLength)
    # print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    # if iteration == total:
        # print()

def do_transform(file, templates, validate=False):
    raw_data = __read_file(file)

    for template in templates.split(','):
        parser = parsers.get(template)
        ret = {'src': file}
        ret['fmt'] = 'gbd'
        # get return from transformation
        if template == 'solrjtm':
            ret['fmt'] = 'idx'
            try:
                transformed = parser.run(raw_data, raise_errors=True)
                ret['out'] = transformed
            except Exception as e:
                ret['terror'] = {'message': e, 'stacktrace': traceback.format_exc()}
        else:

            if not validate or template == 'solrjtm':
                try:
                    transformed = parser.run(raw_data, raise_errors=True)
                    ret['out'] = transformed
                    raw_data = transformed
                except Exception as e:
                    ret['terror'] = {'message': e, 'stacktrace': traceback.format_exc()}
            # get return from transformation and validation
            else:
                try:
                    transformed, errors = parser.validate(raw_data)
                    ret['out'] = transformed
                    ret['verrors'] = errors
                    raw_data = transformed
                except Exception as e:
                    ret['terror'] = {'message': e, 'stacktrace': traceback.format_exc()}
    return ret


def _sub_arry_offset(max_paralel, length, offset):
    if offset + max_paralel < length:
        return offset + max_paralel
    return length


def _paralel_process(path, xpath_lines):

    max_parallel = 25
    # Schedule an initial scan for each segment of the table.  We read each
    # segment in a separate thread, then look to see if there are more rows to
    # read -- and if so, we schedule another scan.
    tasks_to_do = []
    for root, dirs, files in os.walk(path):
        for f in files:
            # TODO: match file name with regex
            if f.endswith('.xml.gz'):
                file2process = os.path.join(path, root, f)
                tasks_to_do.append(file2process)
    pbar = progress(len(tasks_to_do))

    task_counter = 0
    # Make the list an iterator, so the same tasks don't get run repeatedly.

    with concurrent.futures.ThreadPoolExecutor() as executor:

        # Schedule the initial batch of futures.  Here we assume that
        # max_scans_in_parallel < total_segments, so there's no risk that
        # the queue will throw an Empty exception.
        futures = {
            executor.submit(_analyse_for_shazam, file2process, xpath_lines): file2process
            for file2process in tasks_to_do[task_counter:_sub_arry_offset(max_parallel,
                                                                    len(tasks_to_do),
                                                                    task_counter)]
        }
        pbar.start()
        task_counter = len(futures)
        while futures:
            # Wait for the first future to complete.
            done, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            pbar.advance_with_step(len(done))
            for fut in done:
                res = fut.result()
                file2process = futures.pop(fut)
                yield xpath_lines

            # Schedule the next batch of futures.  At some point we might run out
            # of entries in the queue if we've finished scanning the table, so
            # we need to spot that and not throw.
            for file2process in tasks_to_do[task_counter:_sub_arry_offset(len(done),
                                                                         len(tasks_to_do),
                                                                         task_counter)]:
                task_counter += 1
                futures[executor.submit(_analyse_for_shazam, file2process, xpath_lines)] = file2process

def _doc2xpath(el, path, lines, root=''):
    lines.add(root + path)
    path = root + path
    # Print attributes
    for name, val in el.items() :
        lines.add(path + "[@" + _removeNS(name) + "=" + val+"]")
    # Counter on the sibbling element names
    counters = {}
    # Loop on child elements
    for childEl in el :
        tag = _removeNS(childEl.tag)
        # Tag name already encountered ?
        if tag in counters:
            continue
        counters[tag] = 1
        # Print child node recursively
        _doc2xpath(childEl,  '/' + tag, lines, root=path)

def _removeNS(tag) :
    if tag.find('}') == -1 :
        return tag
    else:
        return tag.split('}', 1)[1]

def _analyse_for_shazam(file2process, xpath_lines):
    stream = __read_file(file2process)
    tree = ET.ElementTree(ET.fromstring(stream))
    troot = tree.getroot()
    _doc2xpath(troot, _removeNS(troot.tag), xpath_lines)

def shazam():
    doc = """
    deduce xpath lines from a directory of xml files
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'path to a file or a directory'
    }, {
        'name': ['-o'],
        'dest': 'outfile',
        'help': 'write output to a file',
        'type': str,
        'default': None,
    }, ]

    args = build_command_parser(configs, doc)
    path = args.path

    if os.path.isfile(path):
        print('Expected a directory location.')
        sys.exit(1)
    # a set to contain the unique xpath lines
    xpath_lines = set()

    # in case the path passed is relative
    if not os.path.isabs(path):
        path = os.path.realpath(os.path.join(os.getcwd(), path))
    # passed a directory
    current_xplath_lines = None
    for tmp in _paralel_process(path, xpath_lines):
        current_xplath_lines = tmp

    xpath_lines = current_xplath_lines
    if(args.outfile):
        with open(args.outfile, 'w') as fh:
            for line in sorted(xpath_lines):
                xpath = line.split('/')
                leaf = xpath.pop()
                fh.write(''.join(['__' for p in xpath]) + '/'+leaf)
                fh.write('\n')
    else:
        pprint.pprint(xpath_lines)




def _paralel_run(tasks_to_do, templates, pbar, validate=False, max_parallel=25):
    # Schedule an initial scan for each segment of the table.  We read each
    # segment in a separate thread, then look to see if there are more rows to
    # read -- and if so, we schedule another scan.

    task_counter = 0
    # Make the list an iterator, so the same tasks don't get run repeatedly.

    with concurrent.futures.ThreadPoolExecutor() as executor:

        # Schedule the initial batch of futures.  Here we assume that
        # max_scans_in_parallel < total_segments, so there's no risk that
        # the queue will throw an Empty exception.
        futures = {
            executor.submit(do_transform, file2process, templates, validate): file2process
            for file2process in tasks_to_do[task_counter:_sub_arry_offset(max_parallel,
                                                                          len(tasks_to_do),
                                                                          task_counter)]
        }
        task_counter = len(futures)
        while futures:
            # Wait for the first future to complete.
            processed, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            pbar.advance_with_step(len(processed))
            for fut in processed:
                res = fut.result()
                file2process = futures.pop(fut)
                yield res

            # Schedule the next batch of futures.  At some point we might run out
            # of entries in the queue if we've finished scanning the table, so
            # we need to spot that and not throw.
            for file2process in tasks_to_do[task_counter:_sub_arry_offset(len(processed),
                                                                          len(tasks_to_do),
                                                                          task_counter)]:
                task_counter += 1
                futures[executor.submit(do_transform, file2process, templates, validate)] = file2process


def do_multiprocess(files, settings):
    (args, pbar, done) = settings

    results = []
    # create parsers
    for template in args.template.split(','):
        parsers[template] = Parser(template)

    for file in files:
        results.append(do_transform(file, args.template, validate=args.validate))
        done.value += 1
        pbar.advance(done.value)
    # for tmp in _paralel_run(files, args.template, pbar, validate=args.validate,
    #                         max_parallel=args.threads):
    #     results.append(tmp)
    return results


def run():
    doc = """
    transform input to output using a defined template name.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'path to a file or a directory'
    }, {
        'name': ['template'],
        'type': str,
        'help': 'the template used for transformation'
    }, {
        'name': ['-t'],
        'dest': 'top',
        'type': int,
        'help': 'number of files to run the command onto',
        'default': 0
    }, {
        'name': ['-r'],
        'dest': 'random',
        'type': int,
        'help': 'number of *random* files to run the command onto',
        'default': 0
    }, {
        'name': ['-w'],
        'dest': 'workers',
        'type': int,
        'help': 'number of workers to run the command',
        'default': 1
    },{
        'name': ['-th'],
        'dest': 'threads',
        'type': int,
        'help': 'number of threads to run the command',
        'default': 25
    },{
        'name': ['-o'],
        'dest': 'outfile',
        'help': 'write output to a file',
        'type': str,
        'default': None,
    }, {
        'name': ['-a'],
        'dest': 'appendfile',
        'help': 'append output to a file',
        'type': str,
        'default': None,
    }, {
        'name': ['--qc'],
        'dest': 'validate',
        'help': 'runs gbd-validate on output',
        'action': 'store_true',
        'default': False
    }, {
        'name': ['-q', '--quiet'],
        'dest': 'quiet',
        'help': 'perform transformation quietly (do not print result of transformation)',
        'action': 'store_true',
        'default': False
    }, ]
    args = build_command_parser(configs, doc)


    def _walk_dir(root_path, nb):
        buffer = []
        for root, dirs, files in os.walk(root_path):
            for f in files:
                if f.endswith('.xml.gz'): # or f.endswith('.xml'):
                    buffer.append(os.path.join(root_path, root, f))
                    if len(buffer) == nb:
                        return buffer
        return buffer

    def _fish_dir(root_path, nb):
        buffer = []
        path = root_path
        # go fishing
        while len(buffer) < nb:
            sea  = os.listdir(path)
            # skip empty directories
            if not len(sea):
                path = root_path
                continue
            fish = os.path.join(path, random.choice(sea))
            if os.path.isdir(fish):
                path = fish
            elif os.path.isfile(fish) and fish.endswith('.xml.gz'):
                buffer.append(fish)
                path = root_path
        return buffer

    path = args.path
    # in case the path passed is relative
    if not os.path.isabs(path):
        path = os.path.realpath(os.path.join(os.getcwd(), path))

    files = []
    # passed a file
    if os.path.isfile(path):
        files.append(path)
    # passed a directory
    elif os.path.isdir(path):
        if args.random:
            files = _fish_dir(path, args.random)
        else:
            files = _walk_dir(path, args.top)
    else:
        raise Exception('invalid path %s. try again.' % path)



    workers = min(multiprocessing.cpu_count() - 4, args.workers)

    # print('Running template [%s] * [%s files] with [%s workers]' % (args.template,
    #                                                                 len(files), workers))
    files_per_worker_len = len(files) / workers

    files_per_worker = []
    tmp = []
    for el in files:
        if len(tmp) >= files_per_worker_len:
            files_per_worker.append(tmp)
            tmp = []
        tmp.append(el)
    files_per_worker.append(tmp)

    pbar = progress(len(files))
    pbar.start()

    # a way to share state among workers
    mpmanager = multiprocessing.Manager()
    done = mpmanager.Value('i', 0)

    with multiprocessing.Pool(processes=workers) as pool:  # auto closing workers
        raw_results = pool.starmap(do_multiprocess, zip(files_per_worker, [(args, pbar, done) for x in files]))
    results = []
    for result in raw_results:
        results.extend(result)

    _print_transformation_out(results, args)
    _print_transformation_err(results, args)
    _print_validation_err(results, args)



def _print_transformation_out(results, args):
    output_storage = args.outfile or args.appendfile or '/dev/null'
    output_mode = 'a' if args.appendfile else 'w'
    # fh = open(output_storage, output_mode)

    dirFiles = {}
    for r in results:
        if r.get('out', None):
            dir = os.path.dirname(r.get('src'))
            parentDir = os.path.dirname(dir)
            # print("dir: ", dir, " parent " , parentDir)
            destFile = os.path.join(parentDir, r.get('fmt')+".json")
            if destFile not in dirFiles:
                dirFiles[parentDir] = destFile
    # no support for append
    dirHandles = {}
    for dir in dirFiles:
        dirHandles[dir] = open(dirFiles[dir],'w')
        print("Creating this file: ", dirFiles[dir])
        dirHandles[dir].write("[\n")

    for result in results:
        if result.get('out', None):
            if not args.quiet:
                print(result['out'])
            childDir = os.path.dirname(result.get('src'))
            dir = os.path.dirname(childDir)
            #dirHandles[dir]#with open(dirFiles.get(dir), 'a') as df:
            dirHandles[dir].write(result['out'])
            dirHandles[dir].write(",\n")
            # fh.write(result['out'])
            # fh.write('\n')
    for dh in dirHandles.values():
        dh.write("{}]\n")
        dh.close()

    # fh.close()

def _print_validation_err(results, args):
    if not args.validate:
        return

    display_lines = []

    for result in results:
        verrors = result.get('verrors', [])
        if not len(verrors):
            continue

        display_line = {}
        display_line['QC Invalid File'] = __format_color(result['src'], bcolors.FAIL)
        display_line['Severity'] = []
        display_line['Field'] = []
        display_line['Message'] = []

        for i, verror in enumerate(verrors):
            severity = __format_color(verror['severity'], getattr(bcolors, verror['severity']))
            field = verror['field']
            message = verror['type']

            display_line['Severity'].append(severity)
            display_line['Field'].append(field)
            display_line['Message'].append(message)

        display_line['Severity'] = '\n'.join(display_line['Severity'])
        display_line['Field'] = '\n'.join(display_line['Field'])
        display_line['Message'] = '\n'.join(display_line['Message'])
        display_lines.append(display_line)

    if len(display_lines):
        print('\n')
        print(tabulate(display_lines, headers='keys', showindex='always', tablefmt='psql'))

def _print_transformation_err(results, args):
    # a single file
    if(len(results) == 1):
        result = results[0]
        if result.get('terror', None):
            print(__format_color(result['terror']['stacktrace'], bcolors.FAIL))
        return

    # multi file
    display_lines  = []

    for result in results:
        if not result.get('terror', None):
            continue

        display_line = {}
        display_line['Transformation Failed File'] = __format_color(result['src'], bcolors.FAIL)
        display_line['Error Message'] = result['terror']['message']

        display_lines.append(display_line)

    if len(display_lines):
        print('\n')
        print(tabulate(display_lines, headers='keys', showindex='always', tablefmt='psql'))

def __format_color(value, color):
    return '%s%s%s' % (color, value, bcolors.ENDC)

def __read_file(file):
    if file.endswith('.xml.gz'):
        with gzip.open(file, 'rb') as f:
            raw_data = f.read()
        return raw_data
    else:
        with open(file, 'r') as f:
            raw_data = f.read()
        return raw_data


