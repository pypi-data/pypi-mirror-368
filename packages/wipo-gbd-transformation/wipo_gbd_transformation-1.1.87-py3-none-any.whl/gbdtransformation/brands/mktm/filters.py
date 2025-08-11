# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.oami.europa.eu/TM-Search'
]


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def get_appyear(appnum):
    return appnum[:4]

def translate_kind(kind):
    if kind == 'Individual': return ['Individual']
    if kind == 'Certificate': return ['Certificate']
    if kind == 'Collective': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Expired': return 'Expired'
    if status == 'Registered': return 'Registered'

    if status in ['Application filed',
                  'Application published' ]:
        return 'Pending'

    if status in ['Application refused',
                  'Application withdrawn',
                  'Application opposed',
                  'Registration cancelled']:
        return 'Ended'


    raise Exception('Status "%s" unmapped' % status)

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == '3-D': return 'Three dimensional'
    if feature == 'Combined': return 'Combined'
    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Olfactory': return 'Olfactory'

    raise Exception('Feature "%s" unmapped' % feature)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber
