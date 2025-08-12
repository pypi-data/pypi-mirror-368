import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2].zfill(4)

def translate_type(header):
    subcode = header.TransactionSubCode
    code = header.TransactionCode

    if(code.startswith('Marchi Nazionale')): return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Marchi Prodotti e Servizi': return ['Individual']
    if subcode == 'Marchi Collettivi': return ['Collective']

    raise Exception('Kind "%s" not mapped.' % subcode)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if feature == 'Marchi Nazionale (Name only)': return 'Word'
    if feature == 'Marchi Nazionale (Both Name and Logo)': return 'Combined'
    if feature == 'Marchi Nazionale (Logo only)': return 'Figurative'
    if feature == 'Marchi Nazionale (Tridimensional)': return 'Three dimensional'
    if feature == 'Marchi Nazionale (Sound)': return 'Sound'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # missing regnum
    appnum_parts = trademark.ApplicationNumber.split('/')
    regnum = '%s%s' % (appnum_parts[-2], appnum_parts[-1])
    return regnum

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

# no international for SM
def is_international(header):
    return False

# never accessed
def get_ir_refnum(appnum):
    return

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
