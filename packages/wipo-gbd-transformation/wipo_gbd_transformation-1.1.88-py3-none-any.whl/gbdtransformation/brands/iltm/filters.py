import re
from gbdtransformation.common.filters import matchpath


def translate_kind(kind):
    if not kind: return None
    kind = kind.lower()

    if kind == 'certification mark': return ['Certificate']
    if kind == 'trademark/service mark': return ['Individual']
    if kind == 'collective/certification mark': return ['Collective', 'Certificate']
    if kind == 'collective mark': return ['Collective']

    raise Exception('%s mark kind not covered' % kind)

def translate_status(trademark):
    status = trademark.STATUS

    if status == 'active': return 'Registered'
    if status == 'pending': return 'Pending'

    if status == 'deleted':
        # hasnot been registered
        if not trademark.REGISTRATIONDATE: return 'Ended'
        # non-payment
        if trademark.REGISTRATIONDATE: return 'Expired'

    raise Exception('Status "%s" not mapped' % status)

# with agreement with the office, guessing the feature
def translate_feature(data):
    has_name = False
    has_image = False
    is_vienna_classified = False

    try:
        brand_names = ''.join(
            [x.__value.strip() for x in data.DETAILS.BRAND.NAME
                if x.__value]).strip()
        has_name = len(brand_names) > 0
    except: pass

    try:
        has_image = len(data.IMAGEFILE) > 0
    except: pass

    try:
        vienna_classes = ''.join(
            [x.strip() for x in data.VIENNAGROUP.VIENNATYPE]).strip()
        is_vienna_classified = len(vienna_classes) > 0
    except: pass

    if has_name and has_image and is_vienna_classified:
        return 'Combined'
    if has_name:
        return 'Word'
    if has_image and is_vienna_classified:
        return 'Figurative'

    return 'Undefined'

def translate_event(event):
    if event == 'Registered': return 'Registered'
    if event == 'Accepted': return 'Filed'

    return None

# -------
# helpers
# -------
def get_mark_last_update(data):
    event_dates = []
    for event in matchpath(data, 'EVENTS.EVENT'):
        if event.get('EventDate', None):
            event_dates.append(event.EventDate)

    if len(event_dates):
        return event_dates[-1]

def get_en_from_priority(data, field):
    fields = data[field]
    for f in fields:
        if f['_lang'] == 'en':
            return f['__value']
    return None

def get_case_id(caselink):
    urlre = re.compile(r'(?:[?&](?:tmcaseid=([^&]*)))+$')
    matches = urlre.findall(caselink)
    if len(matches):
        return matches[0]
