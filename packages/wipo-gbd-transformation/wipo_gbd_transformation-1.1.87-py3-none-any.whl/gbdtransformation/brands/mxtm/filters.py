# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.wipo.int/standards/XMLSchema/trademarks'
]

def  get_entity_addr(addr):
    if not addr: return None
    address = []

    if addr.AddressStreet: address.append(addr.AddressStreet)
    if addr.AddressCity: address.append(addr.AddressCity)
    if addr.AddressPostcode: address.append(addr.AddressPostcode)

    return ', '.join(address)

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
def translate_type(type):
    if type == 'Trade mark': return 'TRADEMARK'
    if type == 'Slogan': return 'TRADEMARK'
    if type == 'Title of establishment': return 'TRADEMARK'

    raise Exception('type "%s" is not mapped.' % type)

def translate_kind(kind, type):
    if type == 'Trade mark':
        if kind == 'Individual': return ['Individual']
        if kind == 'Collective': return ['Collective']

    if type == 'Slogan':
        if kind == 'Individual': return ['Individual', type]
        if kind == 'Collective': return ['Collective', type]

    if type == 'Title of establishment': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status, regnum):
    if status == 'Active': return 'Registered'
    if status == 'Pending': return 'Pending'
    if status == 'Deleted':
        if not regnum: return 'Ended'
        else: return 'Expired'

    raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Combined': return 'Combined'
    if feature == 'Figurative': return 'Figurative'
    if feature == '3-D': return 'Three dimensional'

    raise Exception('Feature "%s" unmapped' % feature)

def sanitize_text(text):
    # for gs text
    try: text = text.__value
    except: pass

    if text:
        text = text.replace("&#xD;", " ").replace("&#xA;", " ").replace('\n', ' ')
    return text
