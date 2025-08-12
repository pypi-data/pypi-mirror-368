import datetime
import re

from gbdtransformation.brands.filters import st13 as std_st13
from gbdtransformation.brands.filters import split_vienna as std_split_vienna

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    'http://www.wipo.int/standards/XMLSchema/trademarks'
]

def split_vienna(code):
    if not code: return ''
    if len(code) == 4: code = '%s00' % code

    return std_split_vienna(code)

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']

    return ['Other']
    #raise Exception('kind "%s" is not mapped.' % kind)

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'Figurative': return 'Figurative'
    if feature == 'Word': return 'Word'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Sound': return 'Sound'
    if feature == 'Colour': return 'Colour'
    if feature == 'Position': return 'Position'

    return 'Other'
    #raise Exception('Feature "%s" unmapped' % feature)

def get_entity_kind(entity):
    if entity.ApplicantLegalEntity: return 'Legal entity'
    else: return ''

def get_refs(brefs):
    if not isinstance(brefs, list):
        brefs = [brefs]

    apprefs = []
    regrefs = []

    for bref in brefs:
        if bref.BasicApplicationDetails:
            zref = bref.BasicApplicationDetails.BasicApplication
            if(zref.BasicApplicationNumber):
                apprefs.append({'number': zref.BasicApplicationNumber,
                                'date':   zref.BasicApplicationDate})
        if bref.BasicRegistrationDetails:
            zref = bref.BasicRegistrationDetails.BasicRegistration
            if zref.BasicRegistrationNumber:
                regrefs.append({'number': zref.BasicRegistrationNumber,
                                'date':   zref.BasicRegistrationDate})
    return (apprefs, regrefs)

def get_entity_name_and_address(adrbook):
    name_lines = adrbook.Name.FreeFormatName.FreeFormatNameDetails.FreeFormatNameLine
    try:
        addr_lines = adrbook.Address.FreeFormatAddress.FreeFormatAddressLine
    except:
        addr_lines = []

    if not isinstance(name_lines, list): name_lines = [name_lines]
    if not isinstance(addr_lines, list): addr_lines = [addr_lines]

    # sometime we have empty tags !
    name_lines = [n for n in name_lines if n]
    addr_lines = [n.rstrip(',') for n in addr_lines if n]

    return (', '.join(name_lines), ', '.join(addr_lines))

def get_designations(tm):
    if tm.DesignatedCountryDetails:
        countries = tm.DesignatedCountryDetails.DesignatedCountry
    else:
        countries = []
    if not isinstance(countries, list):
        countries = [countries]
    return countries


def get_designations_madrid(tm):
    madrid = []
    madrid96 = []
    if tm.DesignatedCountryDetails:
        countries = tm.DesignatedCountryDetails.DesignatedCountry
        if not isinstance(countries, list):
            tmp = []
            tmp.append(countries)
            countries = tmp
        for c in countries:
            if c.get('DesignatedUnderCode') != 'Protocol':
                madrid96.append(c.DesignatedCountryCode)
            else:
                madrid.append(c.DesignatedCountryCode)
    return madrid, madrid96


def get_status(tm):
    if tm.ExpiryDate:
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        if today > tm.ExpiryDate: return ('Expired', 'Expired')
    # TOASK: no expiry date => Expired ?
    else:
        return ('Expired', 'Expired')

    return ('Registered', 'Registered')

def st13(tm, apprefs, regrefs):
    appnum = tm.ApplicationNumber
    return std_st13(appnum, office='WO', type='registered', sanitize=False)

def get_application_date(tm):
    if tm.ApplicationDate and len(tm.ApplicationDate.strip().replace('-', '')):
        return tm.ApplicationDate

def get_expiry_date(tm):
    if tm.ExpiryDate and len(tm.ExpiryDate.strip().replace('-', '')):
        return tm.ExpiryDate
