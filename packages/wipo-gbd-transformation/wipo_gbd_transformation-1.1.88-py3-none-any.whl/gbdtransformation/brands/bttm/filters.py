import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    try:
        return appnum.split('/')[-2].zfill(4)
    except:
        return ipas.get_appdate(appdate, appnum)

def translate_type(header):
    code = header.TransactionCode

    if code == 'National Marks': return 'TRADEMARK'
    if code == 'Madrid Marks': return 'TRADEMARK'
    if code == 'Prohibited Marks': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    code = header.TransactionCode

    if code == 'National Marks': return ['Individual']
    if code == 'Madrid Marks': return ['Individual']
    if code == 'Prohibited Marks': return ['Individual']

    # it is set to Other for all
    # kind = trademark.KindMark

    raise Exception('Kind "%s" not mapped.' % code)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == '3742': return 'Unknown'
    if status == '3745': return 'Unknown'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    # TOASK: many documents with DUMMY verbal elements
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    return trademark.ApplicationNumber.split('/')[-1]

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(content):
    return content.TransactionCode == 'Madrid Marks'

def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
