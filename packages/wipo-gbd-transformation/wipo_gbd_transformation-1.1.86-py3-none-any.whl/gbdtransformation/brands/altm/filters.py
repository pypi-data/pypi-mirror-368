import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2]

def translate_type(header):
    code = header.TransactionCode

    if code == 'Trademarks': return 'TRADEMARK'
    if code == 'National Mark Division': return 'TRADEMARK'
    if code == 'G. Indications': return 'GI'
    if code == 'G. Indications(Kombetare)': return 'GI'
    # designation of origin .. hmm
    if code == 'Emertim Origjine': return 'AO'
    if code == 'Emertim Origjine(Kombetare)': return 'AO'

    if not code:
        raise Exception('Incomplete document. Do not Import.')

    raise Exception('Type "%s" is not mapped.' % code)


#TODO: verify with office
def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    subcode = subcode.lower()

    if subcode == 'goods mark': return ['Individual']
    if subcode == 'goods and services mark': return ['Individual']
    if subcode == 'mark goods & services': return ['Individual']
    if subcode == 'marke individuale': return ['Individual']
    if subcode == 'service mark': return ['Individual']

    if subcode == 'marke kolektive': return ['Collective']
    if subcode == 'marke certifikuese': return ['Certificate']

    #GI
    if subcode == 'tregues gjeografik': return ['Other']
    # designation of origin
    if subcode == 'emertim origjine': return ['Other']
    if subcode == 'emertim origjine(kombetare)': return ['Other']

    # application-brand division
    if subcode == 'ndarje e aplikimit-marke': return ['Individual']
    # partial-brand transfer
    if subcode == 'transferim i pjesshem-marke': return ['Individual']
    # transformation - national marker
    if subcode == 'transformim-markenderkombetare': return ['Individual']

    raise Exception('SubCode "%s" is not mapped.' % subcode)


def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == '2295': return 'Unknown'
    if status == '2353': return 'Unknown'
    if status == '2366': return 'Unknown'
    if status == '2387': return 'Unknown'
    if status == '2389': return 'Unknown'
    if status == '2394': return 'Unknown'
    if status == 'Reinstated': return 'Pending'

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
    # no way to deduce the registration number
    # raise Exception('!!!')

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    return False

def get_ir_refnum(appnum):
    return appnum

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
