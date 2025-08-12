# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://tmview.europa.eu/trademark/data'
]


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def get_appyear(appnum):
    return appnum[:4]

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']
    if kind == 'Certificate': return ['Certificate']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Registered': return 'Registered'
    if status == 'Application filed': return 'Pending'
    if status == 'Application refused': return 'Ended'
    if status == 'Application withdrawn': return 'Ended'
    if status == 'Registration surrendered': return 'Ended'
    if status == 'Registration cancelled': return 'Ended'
    if status == 'Ended': return 'Ended'
    if status == 'Expired': return 'Expired'

    raise Exception('Status "%s" unmapped' % status)

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Figurative': return 'Figurative'
    if feature == 'Word': return 'Word'
    if feature == 'Colour': return 'Colour'
    if feature == 'Position': return 'Position'
    if feature == 'Motion': return 'Motion'
    if feature == 'Sound': return 'Sound'
    if feature == 'Hologram': return 'Hologram'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Multimedia': return 'Multimedia'
    # the office wild card. bof
    if feature == 'Other': return 'Other'

    raise Exception('Feature "%s" unmapped' % feature)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber

def sanitize_gs(line):
    'Dati pre-porting - Classe:30 - Prod/Serv: - Descrizione:'
    if 'Dati pre-porting' in line and 'Descrizione' in line:
        line = line.split('Descrizione:')[1].strip()
    if line.endswith('.'):
        line = line[:-1]

    if not line == 'null':
        return line

def sanitize_text(text):
    if text:
        text = text.replace('\n', ' ')
    return text

# -----------------------
# filtering empty tags
# -----------------------
def get_goods_services(goods_services):
    nc_gs = {} # classified
    if not goods_services:
        goods_services = []

    if not isinstance(goods_services, list):
        goods_services = [goods_services]

    for goods_service in goods_services:
        code = goods_service.ClassNumber
        if code and not code == '0':
            nc_gs[code] = {}
            desc = goods_service.GoodsServicesDescription

            if hasattr(desc, '__value'):
                terms = desc.__value
            else:
                terms = desc

            if terms:
                nc_gs[code]['terms'] = terms
            else:
                continue

            if hasattr(desc, '_languageCode'):
                lang = desc._languageCode
                nc_gs[code]['lang'] = lang.lower()

    return nc_gs
