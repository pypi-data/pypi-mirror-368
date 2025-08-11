# standard gbd definitions
from gbdtransformation.brands.filters import st13 as std_st13

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []

def parse_appnum(appnum):
    return appnum.split('/')

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

gbd_status_map = {
    '1': 'Ended',
    '2': 'Ended',
    '3': 'Pending',
    '4': 'Registered',
    '5': 'Delete'
}
off_status_map = {
    '1': 'Invalid registration',
    '2': 'Registration aborted',
    '3': 'In registration',
    '4': 'Registered',
    '5': 'Deleted'
}

def translate_status(status, feature):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    gstatus = gbd_status_map[status]

    # this is an empty document. we will import it as a Delete
    if gstatus == 'Ended' and feature == 'Undefined':
        gstatus = 'Delete'

    return (gstatus, off_status_map[status])

map_feature = {
    'B': 'Figurative',
    'C': 'Combined',
    'F': 'Colour',
    'G': 'Motion',
    'H': 'Hologram',
    'K': 'Three dimensional',
    'L': 'Multimedia',
    'O': 'Other',
    'P': 'Position',
    'S': 'Sound',
    'W': 'Word',
    'M': 'Pattern'
}


def translate_feature(feature):
    """translation of mark feature"""

    # needed information from office
    # if office cannot provide information, then agree on a way to guess (uatm)
    if not feature: return 'Undefined'

    translated_feature = map_feature.get(feature, None)
    if translated_feature:
        return translated_feature

    # raise Exception to recognize unmapped values
    raise Exception('Feature "%s" unmapped' % feature)

def get_name(applicant):
    return ("%s %s" % (applicant.Vorname, applicant.Name)).replace('None', '').strip()

def get_address(applicant):
    return ("%s %s %s %s %s" % (applicant.Strasse, applicant.Stiege, applicant.Tuer, applicant.PLZ, applicant.Ort)).replace('None ', '').strip()
