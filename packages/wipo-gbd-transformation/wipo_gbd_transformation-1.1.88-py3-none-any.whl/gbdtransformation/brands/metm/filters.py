import gbdtransformation.brands.ipas.filters as ipas
import gbdtransformation.common.filters as commons

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def translate_type(header):
    code = header.TransactionCode

    if code == 'Zig': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Individualni zig': return ['Individual']
    if subcode == 'Kolektivni zig': return ['Collective']

    # it is None for all
    # kind = trademark.KindMark

    raise Exception('Kind "%s" not mapped.' % subcode)

def translate_status(trademark):
    events = trademark.get('MarkEventDetails',{}).get('MarkEvent', [])
    if not isinstance(events, list):
        events = [events]
    events_types = [f.get('MarkEventCode') for f in events]
    if 'Registrovan' not in events_types:
        return 'Pending'
    status = trademark.MarkCurrentStatusCode

    if status == 'Converted': return 'Registered'

    return ipas.translate_status(status)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    if not event: return 'Unknown'
    if event == 'Registrovan': return 'Registered'
    return ipas.translate_event(event)

# ---------------------------------------
# # language code is not accurate for markVerbalElement
# def guess_language(text, lang, default):
#     if commons.is_latin(text):
#         return 'en'
#     else:
#         return commons.guess_language(text, lang, default)

# TODO: separate values like
# {'ar': ['BITUTAPE - بيتوتيب']}
# {'ar': ['ديمه كابيتال Dimah Capital']}
def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    return False

def get_ir_refnum(appnum):
    return

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)
