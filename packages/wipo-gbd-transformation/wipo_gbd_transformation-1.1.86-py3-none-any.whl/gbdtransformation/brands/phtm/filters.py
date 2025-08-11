from datetime import datetime
import gbdtransformation.brands.ipas.filters as ipas

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum.split('/')[-2].zfill(4)

"""
def clean_application_number(number):
    # PH/4/1981/00000115 -> 00000115
    if number.startswith("PH/"):
        number = number.replace("PH/", "")
    return number

"""

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # a way to deduce the registration number
    appnum_parts = trademark.ApplicationNumber.split('/')
    regnum = '%s/%s' % (appnum_parts[-2], appnum_parts[-1])
    return regnum

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def translate_type(header):
    code = header.TransactionCode

    if code == 'Trademark': return 'TRADEMARK'
    if code == 'Trademarks': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode

    if subcode == 'Part A': return ['Individual']
    if subcode == 'Part B': return ['Individual']
    if subcode == 'National': return ['Individual']
    if subcode == 'Trademark (national)': return ['Individual']
    if subcode == 'Trademark (Madrid)': return ['Individual']

    raise Exception('Kind "%s" not mapped.' % subcode)

def convertdate2(date, input_formats, output_format="%Y-%m-%d"):
    if not date: return None

    for input_format in input_formats.split(';'):
        try:
            return datetime.strptime(date, input_format).strftime(output_format)
        except:
            continue
    raise Exception('Cannot translate state_date "%s"' % date)

def translate_status(record):
    status = record.STATUS_CATEGORY or record.STATUS_NAME
    if not status: return 'Unknown'

    status_map = { 'abandoned with finality': 'Ended',
                   'cancelled': 'Ended',
                   'refused for non-use': 'Ended',
                   'in verification of publication conditions': 'Pending',
                   'awaiting for bla notification about result of opposition process': 'Pending',
                   'refused with finality': 'Ended',
                   'removed from register for non-use': 'Ended',
                   'voluntarily abandoned': 'Ended',
                   'withdrawn': 'Ended',
                   'appeal pending': 'Pending',
                   'in examination': 'Pending',
                   'pending': 'Pending',
                   'for validation': 'Pending',
                   'registered': 'Registered',
                   '(migration) pending': 'Pending',
                   'abandoned with finality in examination': 'Ended',
                   'abandoned with finality in publication': 'Ended',
                   'awaiting due date to file payment of publication fee': 'Pending',
                   'awaiting for bla notification about possible oppositions': 'Pending',
                   'awaiting processing of appeal': 'Pending',
                   'awaiting processing of revival': 'Pending',
                   'finally refused': 'Ended',
                   'in assignment of responsible examiner for examination': 'Pending',
                   'in data capture of paper applications': 'Pending',
                   'inactive (dead number)': 'Expired',
                   'refused for non-filing of dau': 'Ended',
                   'refused for non-filing of dau / dnu': 'Ended',
                   'removed from register for non-filing of dau': 'Ended',
                   'removed from register for non-filing of dau / dnu': 'Ended',
                   'renewed': 'Registered',
                   'to abandon with finality for non-filing of revival': 'Ended',
                   'to check for renewal': 'Registered',
                   'to proceed after due date to file appeal against refusal': 'Pending',
                   'to proceed after due date to file request for revival': 'Pending',
                   'to produce notice of allowance': 'Pending',
                   'expired': 'Expired' }

    if status.lower() in status_map:
        return status_map[status.lower()]

    raise Exception('Status "%s" unmapped' % status)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    if status == 'TM Applications Received in Error': return 'Ended'

    return ipas.translate_status(status)

def translate_event(event):
    if event == 'TM Applications Received in Error': return 'Withdrawn'
    return ipas.translate_event(event)

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    if feature == 'B': return 'Combined'
    if feature == 'L': return 'Figurative'
    if feature == 'N': return 'Word'

    return ipas.translate_feature(feature)
    #raise Exception('Feature "%s" unmapped' % feature)

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_address(record):
    if not record: return None

    addr = [ record.ADDR_STREET, record.CITY_NAME,
             record.STATE_NAME, record.PROVINCE_NAME ]
    addr = [x for x in addr if x]

    return ', '.join(addr)

# no international for PH
def is_international(header):
    return False

# never accessed
def get_ir_refnum(appnum):
    return

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)

def get_file_name(img):
    if img == None:
        return None
    result = ""
    if img.MarkImageFilename:
        result += img.MarkImageFilename
    if img.MarkImageFileFormat:
        result += "." + img.MarkImageFileFormat.lower()
    if len(result) == 0:
        return None
    return result