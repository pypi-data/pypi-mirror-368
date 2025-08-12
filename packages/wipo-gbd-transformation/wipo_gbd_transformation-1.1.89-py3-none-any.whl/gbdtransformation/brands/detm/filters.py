from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
ignore_namespace = []


def translate_status(trademark):
    if trademark.STATUSCANCELLED == 'true': return ('Expired', 'Expired')
    if trademark.STATUSREFUSED == 'true': return ('Ended', 'Ended')

    if trademark.STATUSOPPOSABLE == 'true': return ('Registered', 'Registered and opposable')
    if trademark.STATUSINFORCE == 'true': return ('Registered', 'Registered')
    if trademark.STATUSOPPOSITIONPENDING == 'true': return ('Registered', 'Registered, opposition proceedings running')

    if trademark.STATUSAPPLICATION == 'true': return ('Pending', 'Application filed')

    raise Exception('Could not deduce status')

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'individual': return ['Individual']
    if kind == 'kollektiv': return ['Collective']
    if kind == 'gewaehrleistung': return ['Certificate']

    raise Exception('kind "%s" is not mapped' % kind)

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature.ACOUSTIC: return 'Sound'
    if feature.COLOUR: return 'Colour'
    if feature.IMAGE: return 'Figurative'
    if feature.KABELKENNFADEN: return 'Tracer'
    if feature.MOTION: return 'Motion'
    if feature.MULTIMEDIA: return 'Multimedia'
    if feature.OTHERMARK: return 'Other'
    if feature.PATTERN: return 'Pattern'
    if feature.POSITION: return 'Position'
    if feature.SOUND: return 'Sound'
    if feature.THREEDIM: return 'Three dimensional'
    if feature.WORD: return 'Word'
    if feature.WORDIMAGE: return 'Figurative'


    raise Exception('Feature could not be deduced')


# if Registered or Expired =>
# if RENEWALDATE: 10y after RENEWALDATE and endofmonth of FILDATE
# else: 10y and endofmonth of FILDATE
def get_expiry_date(trademark, gbd_status):
    if gbd_status in ['Registered', 'Expired']:
        rdate = trademark.RENEWALDATE
        fdate = trademark.FILDATE
        edate = datetime.strptime(rdate if rdate else fdate, '%Y-%m-%d')
        x = edate

        # add 10 years
        edate = edate + relativedelta(years=10)
        # end of month
        fdate = datetime.strptime(fdate, '%Y-%m-%d')

        fdate = fdate + relativedelta(months=1, day=1) + relativedelta(days=-1)
        # watch out for leap years
        while True:
            try:
                edate = datetime(edate.year, fdate.month, fdate.day)
                break
            except:
                fdate = fdate + relativedelta(days=-1)

        return edate.strftime('%Y-%m-%d')
    return None

