from gbdtransformation.brands.wotm.filters import *


def is_pending(tm):
    return True

def get_status(tm):
    if tm.ApplicationNumber:
        return ('Pending', 'Pending subsequent designation')
    else:
        return ('Pending', 'Pending application')

def st13(tm, apprefs, regrefs):
    appnum = tm['http://www.wipo.int/standards/XMLSchema/trademarks_WO_Pending_Number']

    if len(regrefs):
        type = 'pending-%s' % ('basicregistrationnumber')
    # it happens to have pending with no Basic ApplicationNumber/RegistrationNumber (bof)
    else:
    # elif len(apprefs):
        type = 'pending-%s' % ('basicapplicationnumber')

    return std_st13(appnum.replace('PEND', ''), type=type, office='WO', roffice=tm.ReceivingOfficeCode)

def get_application_date(tm):
    ib_recieving_date = tm.MarkRecordDetails['http://www.wipo.int/standards/XMLSchema/trademarks_WO_IBReceiptDate']

    if(ib_recieving_date):
        return ib_recieving_date

    raise Exception('could not find IBReceiptDate')

# for pending, get from MarkRecordDetails (subsequent designations)
def get_designations(tm):
    try:
        countries = tm.MarkRecordDetails.DesignatedCountryDetails.DesignatedCountry
    except:
        raise Exception('No DesignatedCountryDetails. Do not Import')

    if not isinstance(countries, list):
        countries = [countries]
    return countries
