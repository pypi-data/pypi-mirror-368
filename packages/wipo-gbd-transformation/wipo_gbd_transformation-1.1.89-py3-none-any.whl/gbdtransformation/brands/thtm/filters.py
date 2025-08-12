import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def translate_type(header):
    code = header.TransactionCode

    if not code: return 'TRADEMARK'

    if code == 'Trademark': return 'TRADEMARK'
    if code == 'Service mark': return 'TRADEMARK'
    if code == 'Certificate mark': return 'TRADEMARK'
    if code == 'Collective mark': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    kind = trademark.KindMark

    if not kind: return ['Individual']

    if kind == 'Collective mark': return ['Collective']

    return ipas.translate_kind(kind)


def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'Inactive':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    if event == 'Madrid Designation': return 'Registered'

    return ipas.translate_event(event)

# ---------------------------------------

# {'la': ['ທະວີໂຊກ ພ້ອມດ້ວຍຮູບ']} <- lo
def verbal_lang_map(markVerbalElements, applang=None):
    # print( ipas.verbal_lang_map(markVerbalElements, applang=applang))
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    return trademark.ApplicationNumber

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    subcode = header.TransactionSubCode
    return subcode == 'Madrid'

# <wo:MarkEventCode>Madrid Designation</wo:MarkEventCode>
# <wo:OfficeSpecificMarkEventName>IRN:1504436</wo:OfficeSpecificMarkEventName>
def get_ir_refnum(trademark):
    events = trademark.MarkEventDetails.MarkEvent
    for event in events:
        event_name = event.OfficeSpecificMarkEventName
        if event_name.startswith('IRN:'):
            return event_name.replace('IRN:', '')
