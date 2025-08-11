import re

from gbdtransformation.brands import st13_identifier
from gbdtransformation.common.filters import *

def parseStatus(x):
    return x

def parse_version(x):
    return x

def split_vienna(data, separator='.'):
    """when the class is xxyyzz"""
    if not len(data) == 6:
        raise Exception('cannot split vienna "%s"' % data)
    return separator.join([data[:2], data[2:4], data[4:6]])

def pad_vienna(data, separator='.'):
    """Convert to vienna style with padding"""
    if separator in data:
        slice = data.split('.')
        return slice[0].zfill(2) + '.' + pad_vienna('.'.join(slice[1:]))
    return data.zfill(2)


# create synonyms for application/registration numbers
# type = appnum | regnum
def create_synonyms(original, office, numtype, lenient=False):
    if not original: return []
    original = str(original)
    if not office: return [original]
    # collections are usually office code followed with tm: xxtm
    collection = '%stm' % office.lower()
    # some exceptions:
    if office == 'WHO': collection = 'whoinn'

    # get the appnum_mask / regnum_mask
    try:
        module_pckg = load_collection_package('brands', collection)
        masks = getattr(module_pckg, '%s_mask' % numtype)
        if not isinstance(masks, list): masks = [masks]
        # set when making synonyms for reference numbers
        if lenient:
            masks.append('(.*)')
    except (AttributeError, ModuleNotFoundError) as e:
        masks = ['(.*)']

    # match the regex
    matches = None
    for mask in masks:
        regex = re.compile(mask)
        matches = regex.search(original)
        if matches:
            break
    if not matches:
        return [original]
    masked = ''.join([m for m in matches.groups() if m])

    synonyms = []
    def _to_synonyms(value):
        synonyms.append(value)
        value = remove_special(value)
        synonyms.append(value)
        value = remove_non_numeric(value)
        synonyms.append(value)
        value = remove_leading(value, '0')
        synonyms.append(value)

    _to_synonyms(masked)
    _to_synonyms(original)

    return set(synonyms)


# TRADEMARK is a safe default here
def st13(appnum, office, type='TRADEMARK', appdate=None, roffice=None, sanitize=True):
    if not appnum:
        return None
    # collections are usually office code followed with tm: xxtm
    collection = '%stm' % office.lower()
    # some exceptions:
    if office == 'WHO': collection = 'whoinn'

    module_pckg = load_collection_package('brands', collection)
    try:
        masks = getattr(module_pckg, 'appnum_mask')
        if not isinstance(masks, list): masks = [masks]
    except:
        masks = ['(.*)']

    try:
        source = getattr(module_pckg, 'source')
    except:
        source = 'national'
    matches = None
    for mask in masks:
        regex = re.compile('^%s$' % mask)
        matches = regex.search(appnum)
        if matches:
            break

    if not matches:
        raise Exception('could not apply appnum mask %s on %s' % (mask, appnum))

    #print(appnum, ''.join(matches.groups()))
    appnum = ''.join(matches.groups())

    prefix = st13_identifier[source.lower()][type.lower()]
    if sanitize:
        # remove special characters
        special_chars = re.compile(r'\W')
        appnum = special_chars.sub('', appnum)

    # reference office (only relevant for madrid)
    if roffice:
        appnum = '%s%s' % (roffice.upper(), appnum)

    st13 = '%s%s' % (office.upper(), prefix)
    if appdate:
        st13 = '%s%s' % (st13, appdate[:4])

    # add application number and zfill till 17
    return '%s%s' % (st13, appnum.zfill(17 - len(st13)))


