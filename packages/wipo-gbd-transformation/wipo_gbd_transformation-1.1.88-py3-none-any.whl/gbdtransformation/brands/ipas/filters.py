import gbdtransformation.common.filters as commons
from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import events as std_events

def get_appdate(appdate, appnum):
    return appdate

def translate_kind(kind):
    # out-of-the-box match
    if kind.capitalize() in std_kinds:
        return [kind.capitalize()]

    raise Exception('Kind "%s" not mapped.' % kind)

def parse_version(version):
    """ Function is here to be overriden in child elements( e.g BRTM)"""
    return version

def parseStatus(status):
    """ Function is here to be overriden in child elements( e.g BRTM)"""
    return status

def translate_event(event):
    # out-of-the-box match
    if event.capitalize() in std_events:
        return event.capitalize()

    if event.lower() == 'active': return 'Registered'
    # raise Exception('Event "%s" not mapped.' % event)
    return 'Unknown'


def translate_feature(feature):
    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == 'Colour': return 'Colour'
    if feature == 'Stylized characters': return 'Stylized characters'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Sound': return 'Sound'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Olfactory': return 'Olfactory'
    if feature == 'Position': return 'Position'
    if feature == 'Other': return 'Other'
    if feature == 'Undefined': return 'Undefined'

    raise Exception('Feature "%s" not mapped.' % feature)


def translate_status(status):
    status = status.lower()

    if status == 'registered': return 'Registered'
    if status == 'active': return 'Registered'
    if status == 'reinstated': return 'Registered'
    if status == 'expired': return 'Expired'
    if status == 'inactive': return 'Expired'
    if status == 'published': return 'Pending'
    if status == 'examined': return 'Pending'
    if status == 'filed': return 'Pending'
    if status == 'application filed': return 'Pending'
    if status == 'converted': return 'Pending'
    if status == 'opposed': return 'Pending'
    if status == 'application opposed': return 'Pending'
    if status == 'pending': return 'Pending'
    if status == 'appealed': return 'Pending'
    if status == 'awaiting court action': return 'Pending'
    if status == 'application published': return 'Pending'
    if status == 'abandoned': return 'Ended'
    if status == 'withdrawn': return 'Ended'
    if status == 'registration surrendered': return 'Ended'
    if status == 'application withdrawn': return 'Ended'
    if status == 'rejected': return 'Ended'
    if status == 'application refused': return 'Ended'
    if status == 'finalrefusal': return 'Ended'
    if status == 'suspended': return 'Ended'
    if status == 'invalidated': return 'Ended'
    if status == 'surrendered': return 'Ended'
    if status == 'suspended': return 'Ended'
    if status == 'renewed': return 'Registered'
    if status == 'renewalprocess': return 'Registered'
    if status == 'canceled': return 'Ended'
    if status == 'registration cancelled': return 'Ended'
    if status == 'cancelled': return 'Ended'

    return 'Unknown'
    #raise Exception('Status "%s" not mapped.' % status)

# --------------------
# cleaning brand name
# --------------------
def verbal_lang_map(markVerbalElements, applang=None, remove=[]):
    verbal = {}
    if not isinstance(markVerbalElements, list):
        markVerbalElements = [markVerbalElements]

    for elt in markVerbalElements:
        if hasattr(elt, '__value'):
            text = elt.__value
        else:
            text = elt

        if not text: continue

        text = text.strip().rstrip('.')

        if not text: continue
        if text == '-': continue

        if hasattr(elt, '_languageCode'):
            lang = elt._languageCode
        elif applang:
            lang = applang
        else:
            if commons.is_latin(text):
                lang = 'en'
            else:
                lang = commons.guess_language(text, default=applang)

        verbal.setdefault(lang, [])
        verbal[lang].append(text)

    return verbal


# -----------------------
# filtering empty tags
# -----------------------
def get_goods_services(goods_services):
    nc_gs = {} # classified
    if not goods_services:
        goods_services = []

    if not isinstance(goods_services, list):
        goods_services = [goods_services]

    for goods_service in goods_services:
        code = goods_service.ClassNumber
        if code and not code == '0':
            nc_gs[code] = {}
            desc = goods_service.GoodsServicesDescription

            if hasattr(desc, '__value'):
                terms = desc.__value
            else:
                terms = desc

            if terms:
                nc_gs[code]['terms'] = terms
            else:
                continue

            if hasattr(desc, '_languageCode'):
                lang = desc._languageCode
                nc_gs[code]['lang'] = lang.lower()

    return nc_gs

# -----------------------
# completing missing data
# -----------------------

# Expired trademarks with no Expiry date
# => get it from Expired event
def get_expiry_date(trademark, tmstatus):
    if trademark.ExpiryDate:
        return trademark.ExpiryDate

    if not tmstatus == 'Expired':
        return None

    # find the MarkEvent Expired and get its date
    events = trademark.get('MarkEventDetails', {}).get('MarkEvent', [])
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if(event.MarkEventCode == 'Expired'):
                return event.MarkEventDate


# Registered or Expired trademarks with no registration date
# => get it from Registered or Published Event
def get_registration_date(trademark, tmstatus):
    if trademark.RegistrationDate:
        return trademark.RegistrationDate

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # find the MarkEvent Expired and get its date
    events = trademark.get('MarkEventDetails', {}).get('MarkEvent', [])

    # first priority is to get the Registered Event
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if event.MarkEventCode == 'Registered':
                return event.MarkEventDate
    # second priority is to get the Published Event
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if event.MarkEventCode == 'Published':
                return event.MarkEventDate
