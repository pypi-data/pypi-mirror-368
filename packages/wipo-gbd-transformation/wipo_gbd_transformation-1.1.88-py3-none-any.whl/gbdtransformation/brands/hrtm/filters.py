# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://tmview.europa.eu/trademark/data',
    'http://www.oami.europa.eu/TM-Search',
    'http://hr.tmview.europa.eu/trademark/data'
]

def  get_entity_addr(addr):
    if not addr: return None
    result = ""
    if addr.AddressStreet:
        result+= addr.AddressStreet
    if addr.AddressCity:
        result+= " " + addr.AddressCity
    if addr.AddressState:
        result+= " " + addr.AddressState
    if addr.AddressPostcode:
        result+= " " + addr.AddressPostcode
    return result.strip()

def create_full_name(name): 
    result = ""
    
    if name.FirstName: 
        result += name.FirstName + " "
    if name.LastName:
        result += name.LastName
    if name.OrganizationName and name.OrganizationName != name.LastName and name.OrganizationName != result:
        if name.FirstName or name.LastName:
            result += ", "
        result += name.OrganizationName
    return result

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']
    if kind == 'Guarantee': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Registered': return 'Registered'

    if status in ['Application published',
                  'Application filed',
                  'Application opposed',
                  'Filed']:
        return 'Pending'

    if status in ['Expired']:
        return 'Expired'

    if status in ['Ended']:
        return 'Ended'

    return 'Unknown'
    #raise Exception('Status "%s" unmapped' % status)

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
    if "RegistrationNumber" in trademark and trademark.RegistrationNumber:
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

def clean_app_reg_number(app_num):
    if app_num == None:
        return None
    if not app_num[:1].isdigit():
        app_num = app_num[1:]
    return app_num

def get_publication_date(publications):
    # in the publication information, in case:
    # PublicationSection == "Registration"
    # the associated PublicationDate is the publicationDate
    if publications == None:
        return None
    if isinstance(publications, list):
        for publication in publications:
            if 'PublicationSection' in publication and publication['PublicationSection'] == 'Registration':
                if 'PublicationDate' in publication:
                    return publication['PublicationDate']
    else:
        if "Publication" in publications:
            publication = publications["Publication"]
            if 'PublicationSection' in publication and publication['PublicationSection'] == 'Registration':
                if 'PublicationDate' in publication:
                    return publication['PublicationDate']
    return None
