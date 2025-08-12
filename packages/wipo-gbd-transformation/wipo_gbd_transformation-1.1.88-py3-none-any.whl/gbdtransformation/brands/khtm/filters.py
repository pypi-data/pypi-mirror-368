import gbdtransformation.brands.ipas.filters as ipas

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

    if code == 'Madrid Designated': return 'TRADEMARK'
    if subcode == 'Domestic Trademark': return 'TRADEMARK'
    if subcode == 'Domestic Service Mark': return 'TRADEMARK'
    if subcode == 'Domestic Collective Mark': return 'TRADEMARK'
    if subcode == 'Domestic Certification Mark': return 'TRADEMARK'
    if subcode == 'Foreign Trademark': return 'TRADEMARK'
    if subcode == 'Foreign Service Mark': return 'TRADEMARK'
    if subcode == 'Foreign Certification Mark': return 'TRADEMARK'
    if subcode == 'Foreign Collective Mark': return 'TRADEMARK'
    if subcode == 'Related Foreign Trademarks': return 'TRADEMARK'
    if subcode == 'Domestic GI': return 'GI'
    if subcode == 'Foreign GI': return 'GI'

    raise Exception('Type "%s" is not mapped.' % subcode)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode
    kind = trademark.KindMark

    if subcode == 'Domestic GI': return ['Other']
    if subcode == 'Foreign GI': return ['Other']
    if subcode == 'Domestic Collective Mark': return ['Collective']
    if subcode == 'Domestic Certification Mark': return ['Certificate']
    if subcode == 'Foreign Trademark': return ['Individual']
    if subcode == 'Domestic Trademark': return ['Individual']
    if subcode == 'Domestic Service Mark': return ['Individual']
    if subcode == 'Foreign Service Mark': return ['Individual']
    if subcode == 'Foreign Certification Mark': return ['Certificate']
    if subcode == 'Foreign Collective Mark': return ['Collective']

    if kind == 'Individual': return ['Individual']
    # code = header.TransactionCode

    # if code == 'Madrid Designated': return ['Individual']
    # if subcode == 'Domestic Trademark': return ['Individual']
    # if subcode == 'Domestic Service Mark': return ['Individual']
    # if subcode == 'Foreign Trademark': return ['Individual']
    # if subcode == 'Foreign Service Mark': return ['Individual']

    raise Exception('Kind "%s" not mapped.' % kind)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'Inactive':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    if status == '1401': return 'Unknown'
    if status == '0032': return 'Unknown'
    if status == '0035': return 'Unknown'
    if status == '0049': return 'Unknown'
    if status == '0063': return 'Unknown'
    if status == '0086': return 'Unknown'
    if status == '0123': return 'Unknown'
    if status == '0160': return 'Unknown'
    if status == '0535': return 'Unknown'
    if status == '0552': return 'Unknown'
    if status == '0644': return 'Unknown'
    if status == '0699': return 'Unknown'
    if status == '0718': return 'Unknown'
    if status == '2330': return 'Unknown'
    if status == '2335': return 'Unknown'
    if status == '2346': return 'Unknown'
    if status == '2347': return 'Unknown'
    if status == '2349': return 'Unknown'
    if status == '2353': return 'Unknown'
    if status == '2363': return 'Unknown'
    if status == '2376': return 'Unknown'
    if status == '2390': return 'Unknown'
    if status == '2394': return 'Unknown'
    if status == '2395': return 'Unknown'
    if status == '2399': return 'Unknown'
    if status == '2400': return 'Unknown'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    # print( ipas.verbal_lang_map(markVerbalElements, applang=applang))
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber and not trademark.RegistrationNumber == 'KH/M/':
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
    return code == 'Madrid Designated'

# KH/673426/M
def get_ir_refnum(appnum):
    return appnum.split('/')[1]

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
