import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2].zfill(4)

def translate_type(header):
    code = header.TransactionCode

    if code == 'Insignia': return 'EMBLEM'
    if code == 'Indicacao Geografica': return 'GI'
    if code == 'Marca Nacional': return 'TRADEMARK'
    if code == 'Marca Madrid': return 'TRADEMARK'
    if code == 'Logotipo': return 'TRADEMARK'
    if code == 'Nome Comercial': return 'TRADEMARK'
    if code == 'Nome de Estabelecimento': return 'TRADEMARK'
    if code == 'Banjul Protocol TM': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Marca': return ['Individual']
    if subcode == 'Marca de Base': return ['Individual']
    if subcode == 'Madrid Protocol': return ['Individual']
    if subcode == 'Banjul Protocol TM': return ['Individual']
    if subcode == 'Madrid Agreement': return ['Individual']
    if subcode == 'Marca Colectiva': return ['Collective']
    if subcode == 'Marca de Certificacao': return ['Certificate']

    if subcode == 'Nomes': return ['Certificate']
    if subcode == 'Nome de Esbalecimento': return ['Certificate']
    if subcode == 'Logotipo': return ['Other']
    if subcode == 'Indicacao Geografica': return ['Other']
    if subcode == 'Insignia': return ['Emblem']

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
    return code == 'Marca Madrid'

# MD/D/1/1341864
def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
