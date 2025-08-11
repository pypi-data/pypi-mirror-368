from datetime import datetime, date
from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import status as std_status
from gbdtransformation.brands import features as std_features

ignore_namespace = [
   'http://www.ipaustralia.gov.au/trademarks/schema/tm-extract/2005/2',
   'http://www.ipaustralia.gov.au/trademarks/schema/tm-extract/2012/1'
]

def translate_feature(feature, words=None):
    # needed information from office
    if not feature or not isinstance(feature, str): return 'Undefined'

    # out-of-the-box match
    if feature.capitalize() in std_features:
        return feature.capitalize()

    lst = feature.split(', ')

    has_words  = words or _lst_has(lst, 'Word')
    has_figure = _lst_has(lst, 'Shape', 'Device', 'Figurative')

    if has_words and has_figure: return 'Combined'
    if _lst_has(lst, 'Word'): return 'Word'
    if _lst_has(lst, 'Movement'): return 'Motion'
    if _lst_has(lst, 'Shape'): return 'Three dimensional'
    if _lst_has(lst, 'Figurative'): return 'Figurative'
    if _lst_has(lst, 'Fancy'): return 'Stylized characters'
    if _lst_has(lst, 'Colour'): return 'Colour'
    if _lst_has(lst, 'Scent'): return 'Olfactory'
    if _lst_has(lst, 'Feel'): return 'Touch'
    if _lst_has(lst, 'Other'): return 'Other'

    return 'Other'
    #raise Exception('Feature "%s" unmapped' % feature)

def translate_status(status):
    if not status: return 'Unknown'

    # out-of-the-box match
    if status.capitalize() in std_status:
        return status.capitalize()

    status_translated = _status_map.get(status.lower(), None)

    if not status_translated:
        return 'Unknown'
        #raise Exception('Status "%s" unmapped' % status)

    return status_translated


def translate_kind(kind):
    # out-of-the-box match
    if kind.capitalize() in std_kinds:
        return [kind.capitalize()]

    if kind == 'Trade': return ['Individual']
    if kind == 'Certification': return ['Certificate']

    if not kind: return ['Individual']

    return ['Other']
    #raise Exception('kind "%s" is not mapped.' % kind)


# -------------------------
# handling dates exceptions
# -------------------------
def get_application_date(tm):
    sdate = tm.BASGR.BASAPPD
    # application date not set
    if not sdate:
        rdate = tm.BASGR.BASREGD
        if rdate:
            return rdate
        try:
            irdate = tm.INTREGG.NTFDATE
            if irdate:
                return irdate
        except: pass

    return sdate

def get_registration_date(tm):
    rdate = tm.BASGR.BASREGD
    if rdate:
        return rdate

    # try to look in registration publication
    try:
        return tm.PUBREG.PUBREGD
    except: pass


def get_expiry_date(tm):
    edate = tm.BASGR.BASREND
    # expiry date not set
    if not edate:
        status = tm.BASGR.BASSTA
        if status.endswith('Renewal fee not paid') or status.startswith('Registered'):
            sdate = tm.BASGR.BASREGD
            # add 10 years to registration date
            if sdate:
                sdate = datetime.strptime(sdate, '%Y%m%d')
                try:
                    edate = sdate.replace(year = sdate.year + 10)
                except ValueError:
                    edate = sdate + (date(sdate.year + 10, 3, 1) - date(sdate.year, 3, 1))

                edate = edate.strftime('%Y%m%d')

    return edate

# -----------------------------------------------------
# helpers for applicants/representatives/correspondence
# -----------------------------------------------------
def unique_persons(persons):
    if not persons:
        return []

    if not isinstance(persons, list):
        persons = [persons]

    # records are sometines duplicated with same NAML8
    # ADDRL8 666666:XX - "Refer to WIPO correspondence" (International Application)
    unique_by_identifier = list({p.get('NAML8', None): p
        for p in persons
        if not p.ADDRL8 == '666666:XX' }.values())

    return unique_by_identifier

def get_person_name(person):
    if not person:
        return None

    name_lst = [person.NAML4, person.NAML5, person.NAML3, person.NAML6]
    name_lst = list(filter(None, name_lst))
    return ' '.join(name_lst)

# ------------
# helpers
# ------------
# get the injected tag: WIPO_IMGNB
def get_nb_images(tm):
    try:
        if tm.MARKDET.DEVDESC is not None: return 1
    except: pass
    return 0
             # NOT INJECTION ANYMORE int(tm[list(tm.keys()).pop()])

# split on ',' if series
def get_word_series(text, is_series):
    if not text:
        return []

    return text.split(',') if is_series else [text]

def _lst_has(lst, *values):
    for value in values:
        value = value.lower()
        for item in lst:
            if item.lower().startswith(value):
                return True
    return False

_status_map = {
    'published: awaiting examination': 'Pending',
    'accepted: awaiting advertisement': 'Pending',
    'accepted: opposed': 'Pending',
    'accepted: in opposition period': 'Pending',
    'accepted: opposition period expired': 'Pending',
    'accepted: under examination': 'Pending',
    'published: awaiting indexing': 'Pending',
    'published: awaiting examination': 'Pending',
    'published: under examination': 'Pending',
    'published: under examination - hearing requested': 'Pending',
    'published: under examination - deferred': 'Pending',
    'published: under examination - court action': 'Pending',
    'published: deferred awaiting certification rules assessment': 'Pending',
    'published: cancelled at the request of ib': 'Ended',

    'accepted: awaiting publication': 'Registered',

    'registered: registered/protected': 'Registered',
    'protected: registered/protected': 'Registered',
    'registered: renewal due': 'Registered',
    'protected: renewal due': 'Registered',

    'linked: linked/merged before registration': 'Ended',
    'linked: linked/merged after registration': 'Ended',
    'merged: linked/merged before registration': 'Ended',
    'merged: linked/merged after registration': 'Ended',

    'lapsed: notice of intention to defend not filed': 'Ended',
    'lapsed: registration fee not paid on time': 'Ended',
    'lapsed: not accepted': 'Ended',
    'lapsed: in opposition period': 'Ended',
    'lapsed: under examination': 'Ended',
    'removed: non-use': 'Ended',
    'removed: registrar cessation': 'Ended',
    'rejected: examination requirements not met': 'Ended',
    'withdrawn: cancelled before protection': 'Ended',
    'cancelled: owner request': 'Ended',
    'cancelled: cancelled by a court': 'Ended',
    'cancelled: cancelled at the request of ib': 'Ended',
    'cancelled: cancelled for unknown reason': 'Ended',
    'refused: opposition successful': 'Ended',
    'refused: irda notice of intention to defend not filed': 'Ended',
    'refused: pre 1995 refused': 'Ended',
    'withdrawn: applicant request': 'Ended',
    'ceased: non-use': 'Ended',
    'ceased: registrar cessation': 'Ended',
    'not protected: not accepted': 'Ended',
    'not protected: registration fee not paid on time': 'Ended',
    'not protected: notice of intention to defend not filed': 'Ended',
    'registered: expired renewal possible': 'Expired',
    'protected: expired renewal possible': 'Expired',
    'removed - not renewed: renewal fee not paid': 'Expired',
    'ceased - not renewed: renewal fee not paid': 'Expired'
}
