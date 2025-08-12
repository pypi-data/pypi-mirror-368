# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.oami.europa.eu/TM-Search',
    'http://pe.oami.europa.eu/TM-Search'
]

def translate_kind(kind, ipr_kind):
    if kind == None and ipr_kind != None:
        return [ ipr_kind ]
    if not kind: return 'Undefined'

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']
    if kind == 'State property': return ['Collective']
    if kind == 'Certificate': return ['Certificate']

    return ['Other']
    #raise Exception('kind "%s" is not mapped.' % kind)

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
                   'Ended',
                   'Application refused' ]:
        return 'Ended'

    if status in [ 'Application published',
                   'Application Filed',
                   'Application filed',
                   'Examination of opposition',
                   'Opposition pending',
                   'Appeal pending',
                   'Application opposed',
                   'Registration cancellation pending' ]:
        return 'Pending'

    return 'Unknown'
    #raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Sound': return 'Sound'
    if feature == 'Motion': return 'Motion'
    if feature == 'Other': return 'Other'
    if feature == 'Colour' or feature == 'Color': return 'Colour'
    if feature == 'Hologram': return 'Hologram'

    return 'Unknown'
    #raise Exception('Feature "%s" unmapped' % feature)

def  get_entity_addr(addr):
    els = ['AddressStreet', 'AddressCity', 'AddressPostcode', 'AddressCounty']
    res = []
    if not addr: return None
    for el in els:
        if addr.get(el, None):
            res.append(addr[el])
    return ', '.join(res)

def  get_entity_name(name):
    if not name: return
    if name.OrganizationName: return name.OrganizationName
    els = ['FirstName', 'LastName']
    res = []
    for el in els:
        if name.get(el, None):
            res.append(name[el])
    return ' '.join(res)

def  get_entity_kind(name):
    if name == 'Legal': 
        return 'Legal Entity'
    elif name == 'Physical person':
        return 'Natural Person'
    else:
        return None
