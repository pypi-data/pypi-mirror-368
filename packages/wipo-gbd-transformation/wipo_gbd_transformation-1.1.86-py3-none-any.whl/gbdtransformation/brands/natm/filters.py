import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2].zfill(4)

def translate_type(header):
    code = header.TransactionCode

    # extraction missing info.
    if 'do not use' in code.lower():
        raise Exception('Code "%s" encountered. Skipping.' % code)

    if code == 'National Trademarks': return 'TRADEMARK'
    if code == 'National Marks Act 2012': return 'TRADEMARK'
    if code == 'Madrid Marks': return 'TRADEMARK'
    if code == 'Banjul Trademark': return 'TRADEMARK'
    if code == 'Banjul Protocol Marks': return 'TRADEMARK'
    if code == 'DEFENSIVE MARK': return 'TRADEMARK'
    if code == 'CERTIFICATION MARK': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Trade Mark': return ['Individual']
    if subcode == 'PART A': return ['Individual']
    if subcode == 'PART B': return ['Individual']
    if subcode == 'Banjul Trademark': return ['Individual']
    if subcode == 'Banjul Protocol Marks': return ['Individual']
    if subcode == 'Madrid Protocol': return ['Individual']
    if subcode == 'Madrid Agreement': return ['Individual']
    if subcode == 'DEFENSIVE MARK': return ['Defensive']
    if subcode == 'CERTIFICATION MARK': return ['Collective']

    raise Exception('Kind "%s" not mapped.' % subcode)

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
    # print(ipas.verbal_lang_map(markVerbalElements, applang=applang))
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
    return code == 'Madrid Marks'

# D/D/990411
def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
