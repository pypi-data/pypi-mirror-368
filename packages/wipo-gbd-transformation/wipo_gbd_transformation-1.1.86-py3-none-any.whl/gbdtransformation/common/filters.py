import re
import time
import unicodedata

from yaml import dump
from datetime import datetime

import boto3
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import  Dumper
import os
try:
    from polyglot.detect import Detector
except Exception as e:
    pass

from gbdtransformation.common import countries

def load_collection_package(type, collection):
    module_pckg = __import__('gbdtransformation.%s.%s' % (type, collection),
            globals(),
            locals(),
            [collection])
    return module_pckg

def get_entity_from_db(value, collection, e_type, st13):
    e_type = e_type[0:3].upper()
    key = "%s.%s.%s" % (collection.lower(), e_type, value)
    #dynamodb = boto3.resource('dynamodb',
    #                          endpoint_url=os.environ.get('DYNAMO_DB'))
    dynamodb = boto3.resource('dynamodb',
                              endpoint_url=os.environ.get('DYDB_URL'))
    #dynamodb = boto3.resource('dynamodb', 
    #    region_name="eu-west-1", 
    #    aws_access_key_id='anything',
    #    aws_secret_access_key='anything',
    #    endpoint_url="http://localhost:8001")
    table = dynamodb.Table('gbd_pypers_entity')
    response = table.get_item(Key={
        'entity_id': key}).get('Item', {})
    if response:
        linked = set(response['linked_items'])
        linked.add(st13)
        payload = response['payload']
        # Updated the linked
        retry = 0
        while retry < 3:
            try:
                table.update_item(Key={'entity_id': key},
                                  UpdateExpression='SET linked_items = :val1',
                                  ExpressionAttributeValues={
                                      ':val1': list(linked)
                                  })
                break
            except Exception as e:
                time.sleep(0.2)
                retry += 1
        # Ignore applicant / representative root
        payload = payload[list(payload.keys())[0]]
        output = dump(payload, Dumper=Dumper)
        first = True
        new_output = []
        # pepare the padding
        for line in output.split('\n'):
            if not first:
                line = '    %s' % line
            first = False
            new_output.append(line)
        output = '\n'.join(new_output)
        return output
    return None


def to_str(input):
    return str(input)


# split goods and services terms
def split_terms(data, separator=';'):
    """ Splits text base on seprator"""
    if not data:
        return []
    elif hasattr(data, '__value'): data = data.__value

    if not data:
        return []
    terms = []
    if type(data) == list:
        for d in data:
            tmp = [str(x).strip() for x in d.split(separator) if str(x).strip()]
            tmp = [x for x in tmp if x != 'true' and x != 'false']
            terms.extend(tmp)
    else:
        terms = [str(x).strip() for x in data.split(separator) if str(x).strip()]
        terms = [x for x in terms if x != 'true' and x != 'false']
    return terms


def convertdate(date, input_format=None, output_format="%Y-%m-%d"):
    """Date convertor from input_format to output_format"""
    if not date:
        return None
    try:
        return datetime.strptime(date, input_format).strftime(output_format)
    except ValueError:
        # TODO - go back one day
        # example from detm
        # while True:
        #     try:
        #         edate = datetime(edate.year, fdate.month, fdate.day)
        #         break
        #     except:
        #         fdate = fdate + relativedelta(days=-1)
        # removing invalid dates
        return None


# expand multi-national applications
def expand_territories(territory, applicationDate):
    if territory.upper() == 'EM':
        territories = [ 'EM', 'AT', 'BE', 'BG', 'HR',
                        'CY', 'CZ', 'DK', 'EE', 'FI',
                        'FR', 'DE', 'GR', 'HU', 'IE',
                        'IT', 'LV', 'LT', 'LU', 'MT',
                        'NL', 'PL', 'PT', 'RO', 'SK',
                        'SI', 'ES', 'SE' ]
        # BREXIT date
        if applicationDate < '2020-01-31':
            territories.append('GB')

        return territories
    else:
        return [ territory.upper() ]

def replace_quotes(data, replace=""):
    """Remove quotes from strings"""
    if(isinstance(data, str)):
        return data.replace('"', replace).replace(':', '&colon;')
    elif hasattr(data, '__value'):
        return replace_quotes(data.__value)

    return None

def remove_tab(data):
    """Remove carriage returns"""
    if(isinstance(data, str)):
        return data.replace('\t', ' ')
    elif hasattr(data, '__value'):
        return remove_tab(data.__value)

    return None

def remove_cr(data):
    """Remove carriage returns"""
    if(isinstance(data, str)):
        return data.replace('\n', '')
    elif hasattr(data, '__value'):
        return remove_cr(data.__value)

    return None


def get_true_or_false(data):
    """Converts None to False, false to False and data to True"""
    if not data:
        return False
    elif isinstance(data, str):
        data = data.lower()
        if data == 'false': return False
        if data == 'n':
            return False

    return True


def append(value, *suf):
    if not value: return ''

    for s in suf:
        if s:
            value = '%s%s' % (value, s)

    return value

def contains(text, value):
    try:
        text.lower().index(value.lower())
        return True
    except:
        return False

def remove_leading(value, *chars):
    if not value:
        return None
    for char in chars:
        if value[0:1] == char:
            value = value[1:]
            return(remove_leading(value, *chars))
    return value

def remove_trailing(value, *chars):
    if not value:
        return None
    if isinstance(value, list):
        return [remove_trailing(v, chars) for v in value]
    if hasattr(value, '__value'):
        value = value.__value
    if not value:
        return None

    for char in chars:
        if value.endswith(char):
            value = value[:-1]
            return(remove_trailing(value, *chars))
    return value

# remove special characters
def remove_special(val):
    special_chars = re.compile(r'\W')
    val = special_chars.sub('', val)
    return val

# remove non-numeric
def remove_non_numeric(val):
    non_numeric = re.compile(r'\D')
    val = non_numeric.sub('', val)
    return val

# some collections need to split brand name by language
def guess_brand_language(value, lang=None, default=None, opts=[]):
    return guess_language(value, lang=lang, default=default, opts=opts)

def guess_language(value, lang=None, default=None, opts=[]):
    """
    sudo apt-get install python-numpy libicu-dev
    pip install -U git+https://github.com/aboSamoor/polyglot.git@master
    """
    if not value: return None

    if isinstance(value, list):
        value = value[0]

    if hasattr(value, '__value'):
        value = value['__value']
    if not value: return None

    value = value.strip()
    if not value: return None

    if lang: return lang.lower()

    if is_latin(value):
        if default: return default
        else: return 'la'

    try:
        lang = Detector(value, quiet=True).languages[0]
        lang_code = lang.code.lower()

        # manual corrections of lang detection mistakes
        # bof !
        if lang_code == 'tg': lang_code = 'uk'

        if lang_code != 'un':
            if len(opts):
                if lang_code in opts:
                    return lang_code
            else:
                return lang_code
    except Exception as e:
        pass

    if default:
        return default.lower()
    else:
        return None

def is_latin(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False

    return True

def country_name2code(name):
    if not name:
        return None

    name = name.strip().lower()
    for code, country in countries.items():
        if isinstance(country, list):
            for syn in country:
                if syn.lower() == name:
                    return code
        else:
            if country.lower() == name:
                return code
    return None
    #raise Exception('[%s] country name is not mapped' % name)



def address_line2country_code(addr):
    items = [a.strip() for a in addr.split(',')]
    maybe_country_name = items[-1]

    return country_name2code(maybe_country_name)


# -----------------------
# internal engine helpers
# -----------------------

def first(value):
    if isinstance(value, list):
        return value[0]
    return value

def last(value):
    if isinstance(value, list):
        return value[-1]
    return value

def has_value(elem):
    if not elem: return False
    if not isinstance(elem, list):
        elem = [elem]

    for item in elem:
        if hasattr(item, '__value'):
            text = item.__value or ''
        else:
            text = item or ''

        # remove emptyspaces, '.' & '-' and see
        # if anything else is left
        text = re.sub(r'[-,\.\s]', '', text)

        if len(text): return True

    return False

def get_value(elem):
    if hasattr(elem, '__value'):
        text = elem.__value or ''
    else:
        text = elem or ''

    return text

def remove_numerics(text):

    if hasattr(text, '__value'):
        text = text.__value or ''
    else:
        text = text or ''

    # remove emptyspaces, '.' & '-' and see
    # if anything else is left
    text = re.sub(r'[0-9]', '', text)

    return text

def field_name(value):
    """
    a place holder to identify field names
    in order to suppress the automatic
    yaml_filter
    """
    return value

def matchpath(scope, path):
    match = []
    path_parts = path.split('.')

    while(len(path_parts)):
        part = path_parts.pop(0)
        if(hasattr(scope, part) or (isinstance(scope, dict) and part in scope.keys())):
            match = scope[part]
            scope = match
        else:
            return []
    if not isinstance(match, list):
        return [match]
    else:
        return match

def yaml_filter(root):
    if hasattr(root, '__value'):
        return yaml_filter(root.__value)
    if isinstance(root, bool):
        return root
    if isinstance(root, str):
        if root.lower() in ['true', 'false']:
            return bool(root)
        root = root.replace('\\', '\\\\')
        root = root.replace('"', '\\"')
        root = '"%s"' % root
    return root

def try_to_8bit(value):
    if not value: return ''
    value = str(value)
    return unicodedata.normalize('NFKC', value)

def my_print(value):
    print("++++++++++++")
    print(value)
    print("++++++++++++ %s" % len(value))
    return value
