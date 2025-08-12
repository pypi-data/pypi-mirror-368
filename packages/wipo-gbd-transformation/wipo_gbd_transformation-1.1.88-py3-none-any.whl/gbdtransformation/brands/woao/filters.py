# standard gbd definitions
from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import status as std_status
from gbdtransformation.brands import features as std_features
from gbdtransformation.brands import events as std_events
from datetime import datetime
# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []

def get_type(lisbon):
    return lisbon.NUMBER._KIND

def get_names(names):
    joined = []
    if not isinstance(names, list):
        names = [names]
    for name in names:
        joined.append(name)

    return ' / '.join(joined)

def get_gbd_status(status):
    if status == 'A': return 'Registered'
    if status == 'C': return 'Ended'

    raise Exception('Status %s not mapped' % status)

def get_office_status(status):
    if status == 'A': return 'Active'
    if status == 'C': return 'Cancelled'

def get_st13_lisbon(lisbon, appdate):
    # remove special characters

    appnum = lisbon.NUMBER['__value']
    if not appnum:
        raise Exception("No appnumber provided")
    if not appdate:
        appdate = '0000'
    return 'WO81%s%s' % (appdate[:4], appnum.zfill(9))

def get_pub(lisbon):
    pub = lisbon.PUB
    if pub:
        if ':' in pub:
            tmp = pub.split(':')
            try:
                date = datetime.strptime(tmp[1].strip(), "%U/%Y")
                date = date.strftime('%Y-%m-%d')
            except:
                date = None
            return tmp[0].replace('N\u00b0', '').strip(), date
        return pub.replace('N\u00b0', '').strip(), None
    return None, None

def get_events(lisbon):
    types = [{
        'key': 'REFUSALGR',
        'gbd_type': 'Rejected',
        'type': 'Refusal'
    },
        {
            'key': 'MODIFICATIONGR',
            'gbd_type': 'Published',
            'type': 'Modification'
        },
        {
            'key': 'WITHDGR',
            'gbd_type': 'Withdrawn',
            'type': 'Withdrawal'
        },
        {
            'key': 'GRANTGR',
            'gbd_type': 'Registered',
            'type': 'Grant'
        },
        {
            'key': 'RENUNCIATION_RULE16GR',
            'gbd_type': 'Ended',
            'type': 'Cancelled'
        },
    ]
    to_return = []
    for ttype in types:
        events = lisbon.get(ttype['key'], [])
        if not isinstance(events, list):
            events = [events]
        for event in events:
            ev_key = list(event.keys())[0]
            sub_events = event[ev_key]
            if not isinstance(sub_events, list):
                sub_events = [sub_events]
            for tmp in sub_events:
                pdf = tmp.get('PDF', None)
                to_return.append({
                    'kind': ttype['type'],
                    'gbd_kind': ttype['gbd_type'],
                    'date': tmp.get('DATE', None),
                    'country': tmp.get('CC', None),
                    'extra': pdf
                })
    return to_return

def to_link(val):
    if val:
        return 'https://www.wipo.int/ipdl/jsp/data.jsp?TYPE=PDF&SOURCE=LISBON&KEY=' + val
    return None
