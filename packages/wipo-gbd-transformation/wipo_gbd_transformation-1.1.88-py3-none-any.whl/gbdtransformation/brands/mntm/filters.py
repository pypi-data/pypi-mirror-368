import gbdtransformation.brands.ipas.filters as ipas
from gbdtransformation.common.filters import remove_leading

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def translate_type(header):
    code = header.TransactionCode
    subcode = header.TransactionSubCode

    # extraction missing info.
    if not code:
        raise Exception('Incomplete Document Info')

    # Testimony
    if subcode == 'Гэрчлэх тэмдэг': return 'TRADEMARK'
    # Geographical indication
    if subcode == 'Газар зүйн заалт': return 'GI'

    if code == 'Trademark': return 'TRADEMARK'
    if code == 'Trademark - Madrid': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    code = header.TransactionCode
    subcode = header.TransactionSubCode

    if subcode == 'Trademark - Madrid': return ['Individual']
    if subcode == 'Барааны тэмдэг': return ['Individual']
    # Testimony
    if subcode == 'Гэрчлэх тэмдэг': return ['Certificate']
    # Geographical indication
    if subcode == 'Газар зүйн заалт': return ['Other']
    # Collective Symbol
    if subcode == 'Хамтын тэмдэг': return ['Collective']

    if code == 'Trademark': return ['Individual']
    # return ['Other']

    raise Exception('Kind "%s" not mapped.' % code)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'Inactive':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    if status == 'T025': return 'Unknown'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    # if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

#TODO language is mn but not always
# {'mn': ['DUKE UNIVERSITY']}
def verbal_lang_map(markVerbalElements, applang=None):
    # print(ipas.verbal_lang_map(markVerbalElements, applang=applang))
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    regnum = trademark.RegistrationNumber
    if regnum:
        if not regnum == '-' and not regnum == 'M-':
            return regnum

    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    code = header.TransactionCode
    return code == 'Trademark - Madrid'

# 40-M-0673426
def get_ir_refnum(appnum):
    return remove_leading(appnum.split('-')[-1], '0')

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
