# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def get_appyear(appdate, appnum):
    if appnum[:1] == 'M': # M200000084
        return appnum[1:5]
    else:
        return appdate[-4:]

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_office_status(status):
    if status == 'Seniority': return 'Deleted - basis of Seniority'
    if status == 'EC_Seniority': return 'Deleted - basis of Seniority'
    if status == 'EC Seniority': return 'Deleted - basis of Seniority'
    if status == 'Decision appealed': return 'Appeal pending'
    if status == 'AppealExamination procedure': return 'Appeal pending'

    # correct the typo. bof!
    if status == 'Replaced by an Internatinal Registration': return 'Replaced by an International Registration'

    return status

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Registered': return 'Registered'
    if status == 'Cancelled': return 'Delete'

    if status in [ 'Seniority',
                   'Registration surrendered',
                   'Expired',
                   'EC_Seniority',
                   'EC Seniority',
                   'Deleted from Register',
                   'Replaced by an International Registration',
                   'Replaced by an Internatinal Registration' ]:
        return 'Expired'


    if status in [ 'Proceeding terminated by the request of applicant',
                   'Proceeding terminated',
                   'Refused',
                   'Application not filed' ]:
        return 'Ended'

    if status in [ 'Pending',
                   'Published',
                   'Decision appealed',
                   'AppealExamination procedure',
                   'Examination procedure',
                   'Opposition pending' ]:
        return 'Pending'

    if 'pending' in status:
        return 'Pending'

    raise Exception('Status "%s" unmapped' % status)

def split_vienna(code):
    return "%s.%s.%s" % (code[0:2], code[2:4], code[4:])

def get_full_address(addr):
    address = []

    if addr.RepAddress: address.append(addr.RepAddress)
    if addr.AddressLine: address.append(addr.AddressLine)
    if addr.AddressCity: address.append(addr.AddressCity)
    if addr.AddressPostcode: address.append(addr.AddressPostcode)

    return ', '.join(address)


def get_full_name_type(addr):
    name = []
    type = 'Natural person'
    if addr.FullName:
        name.append(addr.FullName)
    elif addr.FirstName:
        name.append("%s %s" % (addr.FirstName, addr.LastName))

    if addr.OrganizationName:
        name.append(addr.OrganizationName)
        type = 'Legal entity'

    if len(name):
        return (type, ', '.join(name))
    else:
        raise Exception("Cannot find name")

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Combined': return 'Combined'
    if feature == 'Figurative': return 'Figurative'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Multimedia': return 'Multimedia'
    if feature == 'Motion': return 'Motion'
    if feature == 'Pattern-marks': return 'Pattern'
    if feature == 'Position': return 'Position'
    if feature == 'Sound': return 'Sound'
    if feature == 'Colour': return 'Colour'

    raise Exception('Feature "%s" unmapped' % feature)

