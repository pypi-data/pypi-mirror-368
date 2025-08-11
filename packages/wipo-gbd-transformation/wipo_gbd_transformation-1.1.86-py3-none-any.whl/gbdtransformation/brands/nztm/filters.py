# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.iponz.govt.nz/XMLSchema/trademarks/information',
    'http://www.iponz.govt.nz/XMLSchema/trademarks'
]

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def translate_kind(kind, irn):
    # collective international applications do not have KindMark
    if not kind and irn: return ['Collective']

    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Certificate': return ['Certificate']
    if kind == 'Collective': return ['Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Removed': return 'Delete'

    if status == 'Abandoned': return 'Ended'
    if status == 'Cancelled': return 'Ended'
    if status == 'Refused': return 'Ended'
    if status == 'Rejected': return 'Ended'
    if status == 'Revoked': return 'Ended'
    if status == 'Withdrawn': return 'Ended'
    if status == 'Renounced': return 'Ended'
    if status == 'Invalid': return 'Ended'
    if status == 'Abandoned - continued processing available': return 'Ended'
    if status == 'Refused - continued processing available': return 'Ended'

    if status == 'Expired': return 'Expired'
    if status == 'Expired but restorable': return 'Expired'
    if status == 'Registered (past expiry date)': return 'Expired'
    if status == 'Merged': return 'Expired'

    if status == 'Registered': return 'Registered'
    if status == 'Protected': return 'Registered'

    if status == 'Under Opposition': return 'Pending'
    if status == 'Under Examination': return 'Pending'
    if status == 'Accepted': return 'Pending'
    if status == 'Abeyance': return 'Pending'

    raise Exception('Status "%s" unmapped' % status)

def sanitize_vienna(vienna):
    return '%s.%s.%s' % (vienna[0:2], vienna[2:4], vienna[4:])

def get_registration_nb(trademark, tmstatus):
    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(feature):
    if not feature:
        return 'Undefined'
    if not isinstance(feature, list):
        if feature == 'Word': return 'Word'
        if feature == 'Figurative': return 'Figurative'
        if feature == 'Colour': return 'Colour'
        if feature == '3-D': return 'Three dimensional'
        if feature == 'Sound': return 'Sound'
        if feature == 'Motion': return 'Motion'
        if feature == 'Olfactory': return 'Olfactory'
        if feature == 'Undefined' or feature == "": return 'Undefined'
    else:
        if 'Word' in feature and 'Figurative' in feature:
            return 'Combined'
    raise Exception('Feature "%s" unmapped' % feature)

def format_addressbook(abook):
    # first try to get the Address from FormattedNameAddress
    try:
        address = abook.FormattedNameAddress.Address
    except:
        address = None

    # if not set, then fallback to PostalAddress
    if not address:
        address = abook.PostalAddress

    # if still not set, give up
    if not address: return (None, None)

    cc = address.AddressCountryCode
    address_line = format_address(address)

    return(address_line, cc)

def format_address(address):
    faddress = address.FormattedAddress
    if not faddress: return None

    addr = []
    if faddress.AddressLine:
        if not isinstance(faddress.AddressLine, list):
            faddress.AddressLine = [faddress.AddressLine]

        for line in faddress.AddressLine:
            addr.append(line.__value)

    if faddress.AddressSuburb:
        addr.append(faddress.AddressSuburb)

    if faddress.AddressCity:
        addr.append(faddress.AddressCity)

    if faddress.AddressPostcode:
        addr.append(faddress.AddressPostcode)

    return (', '.join(addr))
