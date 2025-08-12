# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = ['http://www.oami.europa.eu/TM-Search']


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber

def  get_addr(addr):
    if not addr: return None
    return "%s %s %s" % (addr.AddressStreet, addr.AddressCity, addr.AddressPostcode)

def  get_name(name):
    if not name: return None
    if name.OrganizationName:
        return name.OrganizationName
    return "%s %s" % (name.FirstName, name.LastName )

def translate_kind(kind):
    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status in ['Application filed',
                  'Application published' ]:
        return 'Pending'

    if status in ['Application refused',
                  'Registration cancelled' ]:
        return 'Ended'

    if status == 'Registered':
        return 'Registered'

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Combined': return 'Combined'
    if feature == 'Figurative': return 'Figurative'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Sound': return 'Sound'
    if feature == 'Stylized characters': return 'Stylized characters'
    if feature == 'Multimedia': return 'Multimedia'

    raise Exception('Feature "%s" unmapped' % feature)

