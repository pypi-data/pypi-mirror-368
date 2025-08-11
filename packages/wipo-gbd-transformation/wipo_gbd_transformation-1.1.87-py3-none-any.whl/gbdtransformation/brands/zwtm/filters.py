import gbdtransformation.brands.ipas.filters as ipas
import gbdtransformation.brands.filters as common

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def st13(appnum, office, **args):
    return common.st13(appnum, office)

def translate_type(header):
    code = header.TransactionCode

    # extraction missing info.
    if not code:
        raise Exception('Incomplete Document Info')

    if code == 'National TradeMarks': return 'TRADEMARK'
    if code == 'Zimbabwe': return 'TRADEMARK'
    if code == 'Madrid': return 'TRADEMARK'
    if code == 'Banjul Protocol Marks': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Part A': return ['Individual']
    if subcode == 'Part B': return ['Individual']
    if subcode == 'Part C': return ['Individual']
    if subcode == 'Part D': return ['Individual']
    if subcode == 'National Trademarks': return ['Individual']
    if subcode == 'Madrid Protocol': return ['Individual']
    if subcode == 'Banjul Protocol Marks': return ['Individual']

    raise Exception('Kind "%s" not mapped.' % code)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'Inactive':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    code = header.TransactionCode
    return code == 'Madrid'

# IB/D/1/1020123
def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
