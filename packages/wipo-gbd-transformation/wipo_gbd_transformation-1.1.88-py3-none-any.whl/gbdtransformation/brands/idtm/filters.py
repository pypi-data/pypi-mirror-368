import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum[3:7]

def translate_type(header):
    code = header.TransactionCode

    if code == 'Merek Dagang': return 'TRADEMARK'
    if code == 'Merek Jasa': return 'TRADEMARK'
    if code == 'Merek Perpanjangan (R)': return 'TRADEMARK'
    if code == 'Merek Perpanjangan (V)': return 'TRADEMARK'
    if code == 'Trademark - Madrid (DCP)': return 'TRADEMARK'
    if code == 'Merek Kolektif': return 'TRADEMARK'
    if code == 'Merek Dagang & Jasa': return 'TRADEMARK'

    if code == 'Madrid DCP (MIGRASI)': return 'TRADEMARK'
    if code == 'Madrid BIRTH transaction': return 'TRADEMARK'
    if code == 'Madrid Office of Origin': return 'TRADEMARK'
    if code == 'Madrid CORRECTION transaction': return "TRADEMARK"
    # extraction missing info.
    if not code:
        return 'TRADEMARK'
        # raise Exception('Incomplete Document Info')

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    kind = trademark.KindMark

    if not kind: return ["Individual"]

    return ipas.translate_kind(kind)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    if feature == 'Merek Kata dan Lukisan': return 'Combined'
    if feature == 'Merek Kata': return 'Word'
    if feature == 'Merek Lukisan': return 'Figurative'
    if feature == 'Merek Tiga Dimensi': return  'Three dimensional'
    if feature == 'Merek Suara': return  'Sound'
    if feature == 'Merek Hologram': return  'Hologram'
    if feature == 'Odor': return  'Olfactory'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

# TODO: remove occurances of Logo
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
    code = header.TransactionCode
    return code == 'Trademark - Madrid (DCP)'

# M0020181390000
def get_ir_refnum(appnum):
    return appnum[7:]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
