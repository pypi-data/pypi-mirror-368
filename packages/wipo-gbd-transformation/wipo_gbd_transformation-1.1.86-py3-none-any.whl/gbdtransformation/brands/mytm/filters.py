import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    if appnum.startswith('TM'):
        return appnum[2:6]

    if appnum.find('/') > -1:
        return appdate[:4]

    if len(appnum) == 10:
        return appnum[:4]

    return '19%s' % (appnum[:2])

def translate_type(header):
    code = header.TransactionCode

    if code == 'TRADE MARK': return 'TRADEMARK'
    if code == 'CERTIFICATION': return 'TRADEMARK'
    if code == 'DEFENSIVE': return 'TRADEMARK'
    if code == 'COLLECTIVE MARK': return 'TRADEMARK'
    if code == 'NOT DEFINED': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    kind = trademark.KindMark

    if kind == 'TRADE MARK': return ['Individual']
    if kind == 'CERTIFICATION': return ['Certificate']
    if kind == 'DEFENSIVE': return ['Defensive']
    if kind == 'COLLECTIVE MARK': return ['Collective']
    if kind == 'NOT DEFINED': return ['Other']

    raise Exception('Kind "%s" not mapped.' % kind)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == '15': return 'Unknown'
    if status == '17': return 'Unknown'
    if status == '27': return 'Unknown'
    if status == '28': return 'Unknown'
    if status == '29': return 'Unknown'
    if status == '30': return 'Unknown'
    if status == '36': return 'Unknown'
    if status == '86': return 'Unknown'
    if status == '644': return 'Unknown'
    if status == '645': return 'Unknown'
    if status == '653': return 'Unknown'
    if status == '671': return 'Unknown'
    if status == '672': return 'Unknown'
    if status == '688': return 'Unknown'
    if status == '789': return 'Unknown'
    if status == '791': return 'Unknown'
    if status == '826': return 'Unknown'
    if status == '448': return 'Unknown'
    if status == 'Suspended': return 'Ended'

    if status == 'Inactive':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if feature == 'WORD': return 'Word'
    if feature == 'COMBINED': return 'Combined'
    if feature == 'IMAGE': return 'Figurative'
    if feature == 'COLOUR': return 'Colour'
    if feature == 'STYLISH': return 'Stylized characters'
    if feature == '3D': return 'Three dimensional'
    if feature == 'SHAPE': return 'Three dimensional'
    if feature == 'MOTION': return 'Motion'
    if feature == 'POSITION': return 'Position'
    if feature == 'SOUND': return 'Sound'
    if feature == 'NOT DEFINED': return 'Undefined'
    if feature == 'ANYCOMBINATION': return 'Undefined'
    if feature == 'HOLOGRAM': return 'Hologram'
    if feature == 'SMELL': return 'Olfactory'

    raise Exception('Feature "%s" not mapped.' % feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    # print( ipas.verbal_lang_map(markVerbalElements, applang=applang))
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    return trademark.ApplicationNumber

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
