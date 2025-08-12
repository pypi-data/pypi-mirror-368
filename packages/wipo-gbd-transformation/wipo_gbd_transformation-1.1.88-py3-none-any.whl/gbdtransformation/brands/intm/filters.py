# standard gbd definitions
from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import status as std_status
from gbdtransformation.brands import features as std_features
from gbdtransformation.brands import events as std_events

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = ['http://www.oami.europa.eu/TM-Search']


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def translate_kind(kind):
    """translation of the kind of trademark to a
        multivalue gbd interpretation"""
    # out-of-the-box match
    if kind.capitalize() in std_kinds:
        return kind.capitalize()

    # raise Exception to recognize unmapped values
    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    if not status: return 'Unknown'

    # out-of-the-box match
    if status.capitalize() in std_status:
        return status.capitalize()


    if status in ['Application filed',
                  'Application published',
                  'Application under examination',
                  'Registration pending',
                  'Appeal pending',
                  'Registration cancellation pending']:
        return 'Pending'

    if status in ['Application refused',
                  'Application withdrawn',
                  'Application opposed',
                  'Registration cancelled',
                  'Registration surrendered']:
        return 'Ended'

    # raise Exception to recognize unmapped values
    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    """translation of mark feature"""

    # needed information from office
    # if office cannot provide information, then agree on a way to guess (uatm)
    if not feature: return 'Undefined'

    # out-of-the-box match
    if feature.capitalize() in std_features:
        return feature.capitalize()

    if feature == '3-D': return 'Three dimensional'

    # raise Exception to recognize unmapped values
    raise Exception('Feature "%s" unmapped' % feature)

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None
