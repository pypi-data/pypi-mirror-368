# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = ['http://dk.tmview.europa.eu/trademark/data',
                    'http://www.w3.org/2001/XMLSchema-instance',
                    'http://dk.tmview.europa.eu/trademark/data',
                    'http://tm-xml.org/schema/DK-TM-Search-TradeMark-V1-2.xsd']

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def get_appyear(appnum):
    return appnum.split(' ')[1]

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
    return " ".join(addr.FreeFormatAddressLine)

def  get_name(name):
    if not name: return None
    if name.OrganizationName:
        return name.OrganizationName
    return "%s %s" % (name.FirstName, name.LastName )

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual Mark': return ['Individual']
    if kind == 'Collective Mark': return ['Collective']
    if kind == 'Certification- and Guarantee Mark': return ['Certificate']
    if kind == 'Collective Mark, a Certification Mark or a Guarantee Mark': return ['Collective', 'Certificate']

    # raise Exception to recognize unmapped values
    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    if not status: return 'Unknown'

    if status in ['Application accepted',
                  'Application published',
                  'Classification checked' ]:
        return 'Pending'

    if status in ['Application refused',
                  'Application withdrawn',
                  'Registration cancelled',
                  'Registration surrendered']:
        return 'Ended'

    if status in [ 'Registered',
                   'Revocation proceeding pending',
                   'STATUS UNKNOWN']:
        return 'Registered'

    if status == 'Expired':
        return 'Expired'

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == '3D shape': return 'Three dimensional'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Word': return 'Figurative'
    if feature == 'Pattern': return 'Pattern'
    if feature == 'Motion': return 'Motion'
    if feature == 'Colour': return 'Colour'
    if feature == 'Position': return 'Position'
    if feature == 'Sound': return 'Sound'

    raise Exception('Feature "%s" unmapped' % feature)

