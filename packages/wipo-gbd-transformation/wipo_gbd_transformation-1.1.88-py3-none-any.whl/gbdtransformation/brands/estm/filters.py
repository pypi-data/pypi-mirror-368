# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://es.tmview.europa.eu/trademark/data',
    'http://tmview.europa.eu/trademark/data'
]

def  get_entity_addr(addr):
    if not addr: return None
    return "%s %s %s" % (addr.AddressStreet, addr.AddressCity, addr.AddressPostcode)
def  get_entity_name(name):
    if not name: return
    if name.OrganizationName: return name.OrganizationName
    return "%s %s" % (name.FirstName, name.LastName )
def  get_entity_kind(name):
    if not name: return
    if name.OrganizationName: return 'Legal entity'
    return 'Natural person'

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Ended'

    if status == 'Registered': return 'Registered'

    if status in ['Application published',
                  'Application filed',
                  'Application opposed']:
        return 'Pending'

    raise Exception('Status "%s" unmapped' % status)

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(feature):
    """translation of mark feature"""

    # needed information from office
    # if office cannot provide information, then agree on a way to guess (uatm)
    if not feature: return 'Undefined'
    feature = feature.upper()
    if feature == 'COMBINED': return 'Combined'
    if feature == 'WORD': return 'Word'
    if feature == 'STYLIZED_CHARACTERS': return 'Stylized characters'
    if feature == 'FIGURATIVE': return 'Figurative'
    if feature == 'SOUND': return 'Sound'
    if feature == ' 3 d': return 'Three dimensional'
    if feature == '3-d': return 'Three dimensional'
    if feature == '_3_D': return 'Three dimensional'
    if feature == '3-D': return 'Three dimensional'
    return feature.lower().capitalize()
    # raise Exception to recognize unmapped values
    raise Exception('Feature "%s" unmapped' % feature)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber

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
