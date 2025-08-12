from gbdtransformation.common.filters import guess_language

def appnum_escape(appnum):
    appnum = appnum.replace('\u0431', 'B') # 46618бSU
    appnum = appnum.replace('\u0432', 'B') # 46618вSU
    appnum = appnum.replace('\u0433', 'G') # 46618гSU
    appnum = appnum.replace('\u0412', 'B')
    appnum = appnum.replace('\u0430', 'A') # 6857а/SU
    appnum = appnum.replace('\u0434', 'D') # 49229д/SU
    appnum = appnum.replace('\u041d', 'H') # 567/НТ/SU
    appnum = appnum.replace('\u0422', 'T') # 567/НТ/SU
    appnum = appnum.replace('\u041a', 'K') # 32-HКTп/SU
    appnum = appnum.replace('\u043f', 'N') # 32-HКTп/SU

    return appnum

def format_date(value):
    try:
        return value[0: value.index('T')]
    except:
        return value

def translate_status(mark):

    if mark.obj_state == '1':
        if mark.data.application_status == 'active': return 'Pending'
        if mark.data.application_status == 'stopped': return 'Ended'
        # sometimes the application_status is missing => default to Pending
        return 'Pending'

    # if the obj_state not sent, consider (2)
    if mark.obj_state == '2' or not mark.obj_state:
        if mark.data.registration_status_color == 'green': return 'Registered'
        if mark.data.registration_status_color == 'red': return 'Expired'

    raise Exception('could not get status')

# uatm does not communicate MarkFeature
def guess_mark_feauture(vienna_codes):
    if not(vienna_codes) or len(vienna_codes) == 0:
        return 'Word'

    codes_str = '/'.join(vienna_codes)

    if(codes_str == '28.11.00' or codes_str == '27.07.00'):
        return 'Word'
    if(codes_str == '28.05.00'):
        return 'Stylized characters'
    try:
        codes_str.index('28.11.00')
        return 'Combined'
    except: pass
    try:
        codes_str.index('28.05.00')
        return 'Combined'
    except: pass

    return 'Figurative'

def get_gs_language(items):
    if not(items): return

    if not isinstance(items, list):
        items = [items]

    item = items[0]
    # try:
    #     return item.ClassificationTermLanguageCode.lower()
    # except:
    return guess_language(item.ClassificationTermText, default='uk')
