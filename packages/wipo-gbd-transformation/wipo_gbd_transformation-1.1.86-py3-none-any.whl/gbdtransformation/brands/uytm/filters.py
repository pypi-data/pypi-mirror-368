# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.oami.europa.eu/TM-Search'
]


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_type(type):
    if not type: return 'TRADEMARK'

    if type == 'Trade mark': return 'TRADEMARK'
    if type == 'Slogan': return 'TRADEMARK'

    raise Exception('type "%s" is not mapped.' % type)

def translate_kind(kind, type):
    if not kind: kind = 'Individual'

    if type == 'Trade mark':
        if kind == 'Individual': return ['Individual']
        if kind == 'Collective': return ['Collective']
        if kind == 'Certificate': return ['Certificate']

    if type == 'Slogan':
        if kind == 'Individual': return ['Individual', type]

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Registered': return 'Registered'

    if status == 'Expired': return 'Expired'
    if status == 'Registration cancelled': return 'Expired'

    if status in [ 'Application filed',
                   'Application published' ]:
        return 'Pending'

    if status in [ 'Application refused',
                   'Application opposed',
                   'Registration surrendered',
                   'Application withdrawn' ]:
        return 'Ended'

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == 'Sound': return 'Sound'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Olfactory': return 'Olfactory'

    raise Exception('Feature "%s" unmapped' % feature)

