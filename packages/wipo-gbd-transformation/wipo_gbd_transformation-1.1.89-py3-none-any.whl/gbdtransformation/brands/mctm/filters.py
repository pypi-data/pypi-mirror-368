# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []

def  get_entity_addr(addr):
    if not addr: return None
    return addr.AddressLine

def  get_entity_name(name):
    if not name: return
    if name.OrganizationName: return name.OrganizationName
    return "%s %s" % (name.FirstName, name.LastName )

def  get_entity_kind(name):
    if not name: return
    if name.OrganizationName: return 'Legal Entity'
    return 'Natural Person'

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']
    if kind == 'State property': return ['Collective']
    if kind == 'Certificate': return ['Certificate']
    return ['Individual']
    raise Exception('kind "%s" is not mapped.' % kind)


def translate_status(status):
    if not status: return 'Unknown'
    if status == 'Registration cancelled': return 'Expired'
    if status == 'Expired': return 'Expired'
    if status == 'Registration surrendered': return 'Expired'

    if status in [ 'Registered trademark',
                   'Registered',
                   'Registration renewed']:
        return 'Registered'

    if status in [ 'Application withdrawn',
                   'Application refused' ]:
        return 'Ended'

    if status in [ 'Application published',
                   'Application Filed',
                   'Examination of opposition',
                   'Opposition pending',
                   'Appeal pending' ]:
        return 'Pending'

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Sound': return 'Sound'

    raise Exception('Feature "%s" unmapped' % feature)
