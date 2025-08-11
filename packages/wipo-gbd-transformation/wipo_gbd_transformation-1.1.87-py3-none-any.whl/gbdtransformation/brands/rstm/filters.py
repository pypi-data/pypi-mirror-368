import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum[:4]

def translate_type(header):
    code = header.TransactionCode

    if code == 'Trademark Individual': return 'TRADEMARK'
    if code == 'Trademark Collective': return 'TRADEMARK'
    if code == 'Trademark Certification': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    code = header.TransactionCode

    if code == 'Trademark Individual': return ['Individual']
    if code == 'Trademark Collective': return ['Collective']
    if code == 'Trademark Certification': return ['Certificate']

    raise Exception('Kind "%s" not mapped.' % code)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == '2285': return 'Unknown'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if feature == 'WORD': return 'Word'
    if feature == 'COMBINED': return 'Combined'
    if feature == 'FIGURATIVE': return 'Figurative'
    if feature == 'SCENT': return 'Olfactory'
    if feature == 'F': return 'Figurative'

    return ipas.translate_feature(feature)

def translate_event(event):
    if event == 'Поднет': return 'Filed'
    if event == 'Објављен': return 'Published'
    if event == 'Пред објавом': return 'Examined'
    if event == 'У поступку': return 'Pending'
    if event == 'Регистрован': return 'Registered'
    if event == 'Истекао': return 'Expired'
    if event == 'Одбијен': return 'Rejected'
    if event == 'Повучен': return 'Withdrawn'

    return ipas.translate_event(event)

# ---------------------------------------

# TODO: all set to sr but most are english really
def verbal_lang_map(markVerbalElements, applang=None):
    # print( ipas.verbal_lang_map(markVerbalElements, applang=applang))
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # no way to deduce registration number
    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    return False

def get_ir_refnum(appnum):
    return

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
