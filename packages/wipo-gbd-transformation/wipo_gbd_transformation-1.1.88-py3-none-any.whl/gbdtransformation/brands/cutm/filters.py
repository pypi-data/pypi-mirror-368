import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def translate_type(header):
    code = header.TransactionCode

    if code == 'M': return 'TRADEMARK'
    if code == 'L': return 'TRADEMARK'
    if code == 'N': return 'TRADEMARK'
    if code == 'R': return 'TRADEMARK'
    if code == 'E': return 'EMBLEM'

    if code == 'D':
        raise Exception('Bypass AO from Cuban Office according to their instruction')

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    code = header.TransactionCode

    if code == 'M': return ['Individual']
    if code == 'L': return ['Individual'] # commercial phrase
    if code == 'N': return ['Certificate'] # commercial certificate
    if code == 'R': return ['Certificate'] # Establishement label
    if code == 'E': return ['Emblem'] # Emblem

    # if code == 'D': return ['Other'] # AO

    raise Exception('Kind "%s" not mapped.' % code)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status in ['INI', 'MIGR']:
        raise Exception('File should not be imported [cutm.%s]' % status)

    if status == '013': return 'Unknown'
    if status == '153': return 'Unknown'
    if status == '146': return 'Unknown'
    if status == '163': return 'Unknown'
    if status == '234': return 'Unknown'
    if status == '034': return 'Unknown'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    if feature == 'Mixta': return 'Combined'
    if feature == 'Figurativa': return 'Figurative'
    if feature == 'Denominativa': return 'Word'
    if feature == 'Tridimensional': return 'Three dimensional'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # no way to deduce regnum from appnum
    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    subcode = header.TransactionSubCode
    return subcode.find('Madrid') > -1

# CM/A/1/742990
def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
