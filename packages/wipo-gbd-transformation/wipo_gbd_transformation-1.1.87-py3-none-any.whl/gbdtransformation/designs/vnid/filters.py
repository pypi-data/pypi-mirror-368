# standard gbd definitions
import gbdtransformation.designs.ipas.filters as ipas


# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/designs',
   'http://www.wipo.int/standards/XMLSchema/wo-designs'
]
def get_appdate(appdate, appnum):
    return appnum.split('-')[-2]

def get_designs_count(design, header):
    return '1'

def get_designs_pos(design, header):
    return '1'

def translate_kind(desgin, header):
    code = header.TransactionCode.lower()
    subcode = header.TransactionSubCode.lower()
    if code == 'industrial design':
        return 'Industrial Design'
    raise Exception('Type "%s" "%s" is not mapped.' % (code, subcode))

def translate_status(design):
    status = design.DesignCurrentStatusCode
    if status in ['181', '486']:
        return 'Unknown'
    return ipas.translate_status(status)


def get_registration_nb(design, idstatus):
    if design.RegistrationNumber:
        return design.RegistrationNumber

    return None


def get_expiry_date(design, idstatus):
    return ipas.get_expiry_date(design, idstatus)

def get_registration_date(design, idstatus):
    return ipas.get_registration_date(design, idstatus)

def is_international(header):
    return False

def get_ir_refnum(appnum):
    return appnum

def select_earliest_date(publications):
    return ipas.select_earliest_date(publications)

def deduplicate_publication_dates(publications):
    return ipas.deduplicate_publication_dates(publications)

def deduplicate_classes(classes):
    return ipas.deduplicate_classes(classes)

def deduplicate_publications(publications):
    return ipas.deduplicate_publications(publications)
