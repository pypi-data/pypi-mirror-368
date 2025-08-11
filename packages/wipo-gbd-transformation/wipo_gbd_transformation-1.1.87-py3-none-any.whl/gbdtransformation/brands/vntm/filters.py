import gbdtransformation.brands.ipas.filters as ipas
from datetime import datetime

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    try:
        datetime.strptime(appdate, "%Y-%m-%d")
        return appdate
    except:
        return appnum[5:9]

def translate_type(header):
    code = header.TransactionCode

    if code == 'TradeMark': return 'TRADEMARK'

    # sometimes they miss the header info
    # but otherwise data is complete
    return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    kind = trademark.KindMark
    if not kind:
        return 'Individual'
    return ipas.translate_kind(kind)

def translate_status(trademark):
    value = trademark.MarkCurrentStatusCode
    if value in ['Cấp bằng','Đang giải quyết', 'Từ chối']:
        return ipas.translate_status('Pending')
    elif value in ['Công bố']:
        return ipas.translate_status('Active')
    elif value in ['Hết hạn', 'Rút đơn']:
        return ipas.translate_status("Expired")
    elif value in ['Từ bỏ', 'Mất hiệu lực']:
        return ipas.translate_status('Ended')
    return 'Unknown'

def translate_feature(trademark):
    feature = trademark.MarkFeature

    return ipas.translate_feature(feature)

def translate_event(event):
    if event == 'Notificationd': return 'Notification'
    if not event:
        return None
    return ipas.translate_event(event)

# ---------------------------------------

# TODO: all set to vi but some are english really
# TODO: {'vi': ['NITRASA, hình']} (remove the hih)
def verbal_lang_map(markVerbalElements, applang='vi'):
    # print( ipas.verbal_lang_map(markVerbalElements, applang=applang))
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
