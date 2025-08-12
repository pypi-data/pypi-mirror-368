# standard gbd definitions
from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import status as std_status
from gbdtransformation.brands import features as std_features

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.euipo.europa.eu/EUTM/EUTM_Download',
    'http://www.oami.europa.eu/TM-Search'
]

def filter_language(value, app_language):
    if not value: return []

    languages = set(['en', 'fr', 'es'])
    languages.add(app_language.lower())
    new_matches = []
    for match in value:
        if not match: continue
        if not isinstance(match, dict):
            new_matches.append(match)
        elif not match.get('_languageCode', None):
            new_matches.append(match)
        elif match['_languageCode'].lower() in languages:
            new_matches.append(match)
    return new_matches

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def format_address(address):
    return '%s, %s %s' % (address.AddressStreet,
                          address.AddressPostcode,
                          address.AddressCity)

def format_name(name):
    fname = name.FirstName
    lname = name.LastName

    full_name = [name.FirstName, name.LastName]
    full_name = [f for f in full_name if f]

    return ' '.join(full_name)


def translate_kind(kind):
    if not kind: return ['Individual']

    if kind.capitalize() in std_kinds:
        return [kind.capitalize()]

    if kind == 'EU Certificate':
        return ['Certificate']

    raise Exception('kind "%s" is not mapped.' % kind)



def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature in ["3D shape", "3-D"]: return 'Three dimensional'

    if feature.capitalize() in std_features:
        return feature.capitalize()

    raise Exception('Feature "%s" unmapped' % feature)


def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # default registration number to application number
    # in case none is provided
    if tmstatus in ['Registered', 'Expired']:
        return trademark.ApplicationNumber

def translate_status(trademark):
    if trademark._operationCode == 'Delete':
        return 'Delete'

    status = trademark.MarkCurrentStatusCode

    if status in ['Application filed',
                  'Application published',
                  'Application under examination',
                  'Registration pending',
                  'Appeal pending',
                  'Registration cancellation pending',
                  'Filed']:
        return 'Pending'

    if status in ['Application refused',
                  'Application withdrawn',
                  'Application opposed',
                  'Registration cancelled',
                  'Registration surrendered',
                  'Ended']:
        return 'Ended'

    if status == 'Registered': return 'Registered'
    if status in ['Registration expired', 'Expired']: return 'Expired'

    raise Exception('Status "%s" not mapped.' % status)
