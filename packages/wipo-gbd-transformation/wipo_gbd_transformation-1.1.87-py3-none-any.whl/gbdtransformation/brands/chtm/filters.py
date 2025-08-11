import re

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.wipo.int/standards/XMLSchema/ST96/Common',
    'http://www.oasis-open.org/tables/exchange/1.0',
    'http://www.wipo.int/standards/XMLSchema/ST96/Trademark',
    'http://www.w3.org/2001/XMLSchema-instance',
    'urn:ige:schema:xsd:st96trademarksuperset-1.0.0'
]

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual mark': return ['Individual']
    if kind == 'Collective mark': return ['Collective']

    return 'Unknown'
    #raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Ended'

    if status in ['Registered', 
                  'Registration published']: 
        return 'Registered'

    if status in ['Application published',
                  'Application filed',
                  'Application opposed',
                  'Application accepted']:
        return 'Pending'

    if status in ['Application refused',
                  'Registration cancelled',
                  'Application cancelled']:
        return 'Ended'

    return 'Unknown'
    #raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature):
    """translation of mark feature"""
    if not feature: return 'Undefined'
    feature = feature.upper()
    if feature == 'COMBINED': return 'Combined'
    if feature == 'WORD': return 'Word'
    if feature == 'STYLIZED CHARACTERS': return 'Stylized characters'
    if feature == 'FIGURATIVE': return 'Figurative'
    if feature == 'SOUND': return 'Sound'
    if feature == '_3_D': return 'Three dimensional'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'THREE DIMENSIONAL': return 'Three dimensional'
    if feature == 'POSITION': return 'Position'
    if feature == 'HOLOGRAM': return 'Hologram'
    if feature == 'TRACER': return 'Tracer'
    if feature == 'PATTERN': return 'Pattern'
    if feature == 'OLFACTORY': return 'Olfactory'
    if feature == 'MULTIMEDIA': return 'Multimedia'
    if feature == 'MOTION': return 'Motion'
    return 'Unknown'

    #return feature.lower().capitalize()
    # raise Exception to recognize unmapped values
    #raise Exception('Feature "%s" unmapped' % feature)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber.ApplicationNumberText

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

def get_full_address(postalStructuredAddress):
    if "AddressLineText" not in postalStructuredAddress:
        return
    result = ""
    first = True
    for addressLineText in postalStructuredAddress["AddressLineText"]:
        if hasattr(addressLineText, '__value'):
            if first:
                first = False
            else:
                result += ", "
            result += addressLineText.__value
    if len(result) == 0:
        return
    else: 
        return result.strip()

def select_priority_date(priority):
    if priority == None:
        return None
    if "PriorityApplicationFilingDate" in priority:
        return priority["PriorityApplicationFilingDate"]
    elif "PriorityRegistrationDate" in priority:
        return priority["PriorityRegistrationDate"]
    else:
        return None

def clean_verbal_element(element_text):
    if element_text == None:
        return None
    element_text = element_text.replace("((fig.))", "")
    return element_text.strip()

def local_guess_language(content):
    if content == None:
        return None
    from lingua import Language, LanguageDetectorBuilder
    languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.ITALIAN]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    language = detector.detect_language_of(content)
    if language:
        return language.iso_code_639_1.name.lower()
    else:
        return "en"