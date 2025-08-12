# standard gbd definitions
from gbdtransformation.brands import features as std_features
from gbdtransformation.brands.filters import st13 as std_st13
import re 
from datetime import datetime
# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = ['http://www.cipo.ic.gc.ca/standards/XMLSchema/ST96/Trademark',
                    'http://www.wipo.int/standards/XMLSchema/ST96/Common',
                    'http://www.wipo.int/standards/XMLSchema/ST96/Trademark',
                    'http://www.cipo.ic.gc.ca/standards/XMLSchema/ST96/Common',
                    'http://www.w3.org/2001/XMLSchema',
                    'http://www.oasis-open.org/tables/exchange/1.0',
                    'http://www.w3.org/1998/Math/MathML',
                    'http://www.w3.org/2001/XMLSchema-instance']

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def to_appnum(appnum):
    # remove leading 2 numbers
    appnum = appnum[2:]
    # remove leading zeros
    while appnum[0] == '0':
        appnum = appnum[1:]

    version = appnum[-2:]
    appnum = appnum[:-2]

    return '%s-%s' % (appnum, version)

def neutralize_version(appnum):
    if appnum.endswith('-00'):
        return appnum.replace('-00', '')
    else: 
        return appnum

def has_extension_version(name):
    if name is None: 
        return False
    name = name.replace(".png", "")
    if re.search(r'\-\d\d$', name):
        return True
    else: 
        return False

def get_type_kind(type_raw):

    translations = {
        'Certification Mark': {
            'type': 'TRADEMARK',
            'kind': 'Certificate'
        },
        'Denomination': {
            'type': 'TRADEMARK',
            'kind': 'Collective'
        },
        'Distinguishing Guise': {
            'type': 'TRADEMARK',
            'kind': 'Individual'
        },
        'General Mark': {
            'type': 'TRADEMARK',
            'kind': 'Individual'
        },
        'Geographical Indication': {
            'type': 'GI',
            'kind': 'Other'
        },
        'Mark protected by an Act respecting the Royal Canadian Legion': {
            'type': 'TRADEMARK',
            'kind': 'Collective'
        },
        'Mark Protected by Federal Act of Incorporation': {
            'type': 'TRADEMARK',
            'kind': 'Collective'
        },
        'Prohibited Mark; Abbreviation of the Name': {
            'type': 'EMBLEM',
            'kind': 'Abbreviation'
        },
        'Prohibited Mark; Armorial Bearings': {
            'type': 'EMBLEM',
            'kind': 'State emblem'
        },
        'Prohibited Mark; Arms, Crest or Emblem': {
            'type': 'EMBLEM',
            'kind': 'Armorial bearings'
        },
        'Prohibited Mark; Arms, Crest or Flag': {
            'type': 'EMBLEM',
            'kind': 'Armorial bearings'
        },
        'Prohibited Mark; Badge, Crest, Emblem or Mark': {
            'type': 'EMBLEM',
            'kind': 'Armorial bearings'
        },
        'Prohibited Mark; Emblem': {
            'type': 'EMBLEM',
            'kind': 'Emblem'
        },
        'Prohibited Mark; Flag': {
            'type': 'EMBLEM',
            'kind': 'Flag'
        },
        'Prohibited Mark; Name': {
            'type': 'EMBLEM',
            'kind': 'Name'
        },
        'Prohibited Mark; Official Mark': {
            'type': 'EMBLEM',
            'kind': 'Official sign'
        },
        'Prohibited Mark; Official Sign or Hallmark': {
            'type': 'EMBLEM',
            'kind': 'Official sign'
        },
        'Specific Mark': {
            'type': 'TRADEMARK',
            'kind': 'Individual'
        },
        'Standardization Mark': {
            'type': 'TRADEMARK',
            'kind': 'Individual'
        },
        'Trademark': {
            'type': 'TRADEMARK',
            'kind': 'Individual'
        },
        'Union Label': {
            'type': 'TRADEMARK',
            'kind': 'Collective'
         }
    }
    for item in type_raw:
        if item['_languageCode'] == 'en':
            res = translations.get(item['__value'], None)
            if not res:
                raise Exception('Could not map %s' % type_raw)
            return res.get('type'), res.get('kind', None)



def translate_status(trademark):
    if trademark._operationCategory == 'Delete':
        return 'Delete'

    status = trademark.MarkCurrentStatusCode
    if not status: return 'Unknown'

    wipo_statues = {
        'application filed': 'Pending',
        'filing date accorded': 'Pending',
        'classification checked': 'Pending',
        'application accepted': 'Pending',
        'application published': 'Pending',
        'opposition pending': 'Pending',
        'appeal pending': 'Pending',
        'action before court of justice pending': 'Pending',

        'revocation proceeding pending': 'Registered',
        'invalidity proceeding pending': 'Registered',
        'registration published': 'Registered',

        'application refused': 'Ended',
        'application withdrawn': 'Ended',
        'interruption of proceeding': 'Ended',
        'registration cancelled': 'Ended',
        'conversion requested': 'Ended',
        'registration surrendered': 'Ended',
    }

    res = wipo_statues.get(status.lower(), None)

    # if Registered, check if past expiry date
    if res == 'Registered':
        expiry_date = trademark.ExpiryDate
        if expiry_date:
            today = datetime.today().strftime("%Y-%m-%d")
            if expiry_date < today:
                res = 'Expired'

    if res is not None:
        return res

    raise Exception('status "%s" is not mapped.' % status)


def translate_feature(feature):
    # if not feature: return 'Undefined'
    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == 'Three dimensional': return 'Three dimensional'
    if feature == 'Colour': return 'Colour'
    if feature == 'Sound': return 'Sound'
    if feature == 'Taste': return 'Taste'
    if feature == 'Position': return 'Position'
    if feature == 'Touch': return 'Touch'
    if feature == 'Motion': return 'Motion'
    if feature == 'Olfactory': return 'Olfactory'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Other': return 'Other'
    if feature == 'Design': return 'Combined'

    raise Exception('feature "%s" is not mapped.' % feature)
    return 'Unknown'

def get_mark_name_from_headings(wspec, trademark):
    if isinstance(wspec.IndexHeading, list):
        if len(wspec.IndexHeading) == 0:
            heading = None
        else:
            heading = wspec.IndexHeading[0].IndexHeadingText
    else:
        heading = wspec.IndexHeading.IndexHeadingText
    
    if heading == None:
        # fallback to MarkVerbalElementText
        heading = trademark.MarkRepresentation.MarkReproduction.WordMarkSpecification.MarkVerbalElementText
        print(heading)

    return heading

def get_mark_names(word_mark_spec):
    verbal = word_mark_spec.MarkVerbalElementText
    signif = word_mark_spec.MarkSignificantVerbalElementText

    if not signif == verbal:
        return signif
    else:
        return verbal

def parse_viena(value):
    return '%s.%s.%s' % (value.ViennaCategory.zfill(2), value.ViennaDivision.zfill(2), value.ViennaSection.zfill(2))

def join_postal(values):
    if not isinstance(values, list):
        values = [values]

    return ', '.join([f['__value'] for f in values if f['__value']])

def translate_event(value):
    wipo_events = {
        'application filed': 'Filed',
        'filing date accorded': 'Filed',
        'classification checked': 'Pending',
        'application accepted': 'Pending',
        'application published': 'Published',
        'opposition pending': 'Opposed',
        'registration published': 'Registered',
        'application refused': 'Rejected',
        'application withdrawn': 'Withdrawn',
        'appeal pending': 'Appealed',
        'interruption of proceeding': 'Invalidated',
        'registration cancelled': 'Withdrawn',
        'conversion requested': 'Converted',
        'registration surrendered': 'Withdrawn',
        'revocation proceeding pending': 'Pending',
        'invalidity proceeding pending': 'Pending',
        'action before court of justice pending': 'Awaiting court action',
        'national prosecution history entry': 'Awaiting court action',
        'domestic international application history entry': 'Awaiting court action',
        'national board proceeding history entry': 'Unknown',
        'national assignment history entry': 'Unknown',
        'location history entry': 'Unknown'
    }
    r = wipo_events.get(value.lower(), None)
    if r:
        return r
    raise Exception('Event "%s" unmapped' % value)
