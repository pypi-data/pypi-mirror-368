import yaml
import json
import re

from yaml.reader import Reader
from lxml import etree


NoDatesSafeLoader = yaml.SafeLoader
NoDatesSafeLoader.yaml_implicit_resolvers = {
    k: [r
        for r in v if r[0] != 'tag:yaml.org,2002:timestamp']
    for k, v in NoDatesSafeLoader.yaml_implicit_resolvers.items()
}

def _strip_invalid(s):
    res = ''
    for x in s:
        if Reader.NON_PRINTABLE.match(x):
            # res += '\\x{:x}'.format(ord(x))
            continue
        res += x
    return res


def _remove_none(root):
    """ Internal function to remove empty nodes (nodes with no data)
    @param root: the root of the dict sub-tree"""
    new_dict = {}
    if isinstance(root, dict):
        for k, v in root.items():
            v = _remove_none(v)
            if isinstance(v, list):
                v = _remove_none(v)
            if v is not None:
                new_dict[k] = v
    elif isinstance(root, list):
        v = [_remove_none(a) for a in root if a is not None]
        if len(v) > 0 and v[0] is not None:
            new_dict = v
    else:
        return root if root else None
    return new_dict or None


def sanitize(input_data):
    special_chars = {
        '&': '&amp;',
    }
    for char in special_chars.keys():
        input_data = input_data.replace(char, special_chars[char])
    # Restore already transformed
    matched = re.search(r'&amp;(\w)+;', input_data)
    if matched:
        restore = matched.group().replace('&amp;', '&')
        input_data = input_data.replace(matched.group(), restore)
    lines = input_data.split('\n')
    new_lines = [line for line in lines if len(line.strip())]
    input_data = '\n'.join(new_lines)
    return input_data


def JSON(input_data, raise_errors=False):
    """ Renders input data as JSON
    @param input_data: The data to convert to json
    @return JSON like string"""
    exceptions = []

    special_chars = {
        '&amp;': '&',
    }
    for char in special_chars.keys():
        input_data = input_data.replace(char, special_chars[char])

    try:
        input_data = yaml.load(_strip_invalid(input_data), Loader=NoDatesSafeLoader)
    except Exception as e:
        exceptions.append(e)
        try:
            input_data = json.loads(input_data)
            exceptions = []
        except Exception as f:
            exceptions.append(f)
    for e in exceptions:
        if raise_errors:
            raise e
        print(e)
    input_data = _remove_none(input_data)
    return json.dumps(input_data, indent=4)


def YAML(input_data, raise_errors=False):
    """ Renders input data as YAML
    @param input_data: The data to convert to YAML
    @return YAML like string"""
    exceptions = []
    try:
        input_data = json.loads(input_data)
    except Exception as e:
        exceptions.append(e)
        try:
            input_data = yaml.load(_strip_invalid(input_data), Loader=NoDatesSafeLoader)
            exceptions = []
        except Exception as f:
            exceptions.append(f)
    for e in exceptions:
        if raise_errors:
            raise e
        print(e)
    input_data = _remove_none(input_data)
    return yaml.dump(input_data)


def _remove_empty_chids(root, prev_parent):
    """ Internal function to remove empty nodes (nodes with no data)
    @param root: the root of the xml sub-tree
    @param prev_parent: the parent of the root"""
    for chid in root.getchildren():
        _remove_empty_chids(chid, root)
    if not list(root.getchildren()) and str(root.text).strip() in ['None', '']:
        prev_parent.remove(root)


def XML(input_data):
    """ Renders input data as XML
    @param input_data: The data to convert to XML
    @return XML like string"""
    input_data = sanitize(input_data)
    parser = etree.XMLParser(encoding='utf-8', recover=True)
    root = etree.fromstring(input_data, parser=parser)
    # Convert None text to empty nodes
    for elem in root.iter():
        for child in list(elem):
            if child.text == 'None':
                elem.remove(child)
    # Remove empty nodes
    _remove_empty_chids(root, None)
    output_data = etree.tostring(root, encoding='utf8', method='xml')
    output_data = output_data.decode('utf-8')
    output_data = output_data.replace(">False<", ">false<").replace(">True<", ">true<")
    lines = output_data.split('\n')
    remove_lines = []
    # Remove empty lines
    for line in lines:
        if line.strip() == '':
            remove_lines.append(line)
    for line in remove_lines:
        lines.remove(line)
    return '\n'.join(lines)
