# standard gdd definitions
from gbdtransformation.designs import kinds as std_kinds
from gbdtransformation.designs import status as std_status
from gbdtransformation.designs.filters import st13
from datetime import datetime, date
import json 

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [ "http://www.wipo.int/standards/XMLSchema/ST96/Design", 
                     "http://www.wipo.int/standards/XMLSchema/ST96/Common" ]

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def detectSealedDepositIndicator(HagueExpressTransaction):
    return 'Open'

def cleanHagueAgreementActCategory(category):
    return category.replace("Act", "") if category else None

def getExpiryDate(expiryDate, histories, designIdentifier=None, countryCode=None):
    '''
    Return last seen expiry date in the history events, if any
    restricted to the identified design if specified
    '''
    #print("getExpiryDate")
    #print(expiryDate)
    #print(histories)

    if histories == None or len(histories) == 0:
        return expiryDate

    if not isinstance(histories, list): 
        histories = [histories]

    for history in histories:
        if "HagueRenewal" in history:
            if "ExpiryDate" in history.HagueRenewal:
                if designIdentifier == None:
                    # no design restriction
                    expiryDate = history.HagueRenewal.ExpiryDate
                else:
                    # is the design identifier in the list of affected designs?
                    if isAffectedDesignIdentifier(designIdentifier, history.HagueRenewal.AffectedDesign):
                        if countryCode == None:
                            expiryDate = history.HagueRenewal.ExpiryDate
                        else:
                            if isApplicableToCountry(countryCode, history.HagueRenewal):
                                expiryDate = history.HagueRenewal.ExpiryDate
    return expiryDate

def getLastRenewalDate(histories, designIdentifier=None, countryCode=None):
    '''
    Return the renewal date if the last seen expiry date is in the history events
    Renewal date can be restricted optionally by design identifier and country
    '''
    #print("getLastRenewalDate")

    if histories == None or len(histories) == 0:
        return None

    if not isinstance(histories, list): 
        histories = [histories]

    renewalDate = None
    for history in histories:
        if "HagueRenewal" in history and isinstance(history, dict):
            if "ExpiryDate" in history.HagueRenewal:
                if designIdentifier == None:
                    # no design restriction
                    renewalDate = history.HagueRenewal.RenewalDate
                else:
                    # is the design identifier in the list of affected designs?
                    if isAffectedDesignIdentifier(designIdentifier, history.HagueRenewal.AffectedDesign):
                        if countryCode == None:
                            renewalDate = history.HagueRenewal.RenewalDate
                        else:
                            if isApplicableToCountry(countryCode, history.HagueRenewal):
                                renewalDate = history.HagueRenewal.RenewalDate
    return renewalDate

def getRefusalDate(histories, designIdentifier=None, countryCode=None):
    '''
    Return refusal date, if any
    Refusal datecan be restricted optionally by design identifier and country
    '''
    # check refusal
    refusalDate = None
    if histories != None:
        for history in histories:
            if "HagueRefusal" in history and isinstance(history, dict):
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueRefusal.AffectedDesign):
                    if countryCode == None or isApplicableToCountry(countryCode, history.HagueRefusal):
                        if "DecisionEffectiveDate" in history.HagueRefusal:
                            refusalDate = history.HagueRefusal.DecisionEffectiveDate
                        elif "DecisionDate" in history.HagueRefusal:
                            refusalDate = history.HagueRefusal.DecisionDate
    return refusalDate

def build_person_name(name_struct):
    first_name = None
    if "FirstName" in name_struct:
        first_name = name_struct.FirstName
    last_name = None
    if "LastName" in name_struct:
        last_name = name_struct.LastName
    if first_name is None and last_name is None: 
        return None
    name = ""
    if first_name is not None:
        name += first_name
    if last_name is not None:
        name += " " + last_name.upper()
    return name

def render_and_sort_views(viewBag):
    views = []
    for localViewKey in viewBag:
        localView = viewBag[localViewKey]
        #print(localView)
        view = {}
        if "ViewIdentifier" in localView:
            rank = int(localView.ViewIdentifier)
            localView["rank"] = rank
        if "FileName" in localView:
            name = localView.FileName
            localView["name"] = name
        if "ViewTypeCategory" in localView:
            localType = localView.ViewTypeCategory
            localView["type"] = localType
        legends = []
        if "ViewTypeTextBag" in localView:
            for local_legend in localView.ViewTypeTextBag:
                legend = {}
                legend["languageCode"] = local_legend._languageCode
                legend["legend"] = local_legend.__value
                legends.append(legend)
            if len(legends) > 0:
                localView["legends"] = legends
    return views

def format_address(address_lines):
    address = ""
    if not isinstance(address_lines, list):
        address_lines = [address_lines]
    for address_line in address_lines:
        if address_line is not None and "__value" in address_line:
            address += address_line.__value + ' \n'
    if len(address) > 0:
        return address.strip()
    else:
        return None

def format_complete_address(PostalStructuredAddress):
    if PostalStructuredAddress == None:
        return None
    adr_lines = format_address(PostalStructuredAddress.AddressLineText)
    address = []
    if adr_lines:
        address.append(adr_lines)
    if PostalStructuredAddress.CityName:
        address.append(PostalStructuredAddress.CityName.strip())
    if PostalStructuredAddress.GeographicRegionName:
        address.append(PostalStructuredAddress.GeographicRegionName.strip())
    if PostalStructuredAddress.PostalCode:
        address.append(PostalStructuredAddress.PostalCode.strip())
    if PostalStructuredAddress.CountryCode:
        address.append(PostalStructuredAddress.CountryCode.strip())
    return ' '.join(address)

def getOfficeStatusDate(registrationDate, expiryDate, histories, designIdentifier, countryCode=None):
    expiryDate = getExpiryDate(expiryDate, histories, designIdentifier)
    grantedDate = None
    if countryCode != None and histories != None:
        # check possible renunciation including the particular country if specified
        for history in histories:
            if "HagueRenunciation" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueRenunciation):
                    if "DesignatedCountryBag" in history.HagueRenunciation:
                        for designatedCountry in history.HagueRenunciation.DesignatedCountryBag.DesignatedCountry:
                            if isinstance(designatedCountry, str):
                                if history.HagueRenunciation.DesignatedCountryBag.DesignatedCountry.DesignatedCountryCode  == countryCode:
                                    history.HagueRenunciation.InternationalRecordingDate
                            elif designatedCountry.DesignatedCountryCode == countryCode:
                                return history.HagueRenunciation.InternationalRecordingDate

            # to be tested: same for HagueLimitation, which is very similar to HagueRenunciation
            if "HagueLimitation" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueLimitation):
                    if "DesignatedCountryBag" in history.HagueLimitation:
                        for designatedCountry in history.HagueLimitation.DesignatedCountryBag.DesignatedCountry:
                            if isinstance(designatedCountry, str):
                                if history.HagueLimitation.DesignatedCountryBag.DesignatedCountry.DesignatedCountryCode  == countryCode:
                                    return history.HagueLimitation.InternationalRecordingDate
                            elif designatedCountry.DesignatedCountryCode == countryCode:
                                return history.HagueLimitation.InternationalRecordingDate

            if "HagueGrantProtection" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueGrantProtection.AffectedDesign):
                    if "RecordNotifyingOfficeCode" in history.HagueGrantProtection:
                        if history.HagueGrantProtection.RecordNotifyingOfficeCode == countryCode:
                            grantedDate = history.HagueGrantProtection.InternationalRecordingDate

            # other events potentially impacting status: 
            # to check: HagueInvalidation, HagueMerger, however no occurance since 2018 data

        refusalDate = getRefusalDate(histories, designIdentifier, countryCode)
        # refusal is per designated countries, not just by design
        if refusalDate != None and len(refusalDate) >= 0 and grantedDate is None:
            return refusalDate

    if grantedDate is not None:
        registrationDate = grantedDate

    if expiryDate == None or len(expiryDate) == 0:
        return registrationDate

    registrationDateObject = datetime.strptime(registrationDate, '%Y-%m-%d').date()
    expiryDateObject = datetime.strptime(expiryDate, '%Y-%m-%d').date()

    # the following gives the date of the last extension, if any
    lastRenewalDate = getLastRenewalDate(histories, designIdentifier)
    lastRenewalDateObject = datetime.strptime(expiryDate, '%Y-%m-%d').date()

    if lastRenewalDateObject > registrationDateObject:
        return lastRenewalDate
    else: 
        return registrationDate

def getGbdStatus(registrationDate, expiryDate, histories, designIdentifier, countryCode=None):
    # (Ended|Expired|Pending|Registered|Unknown)
    # note: Ended is for every non-active cases except expired ones, so withdrawal, refusal,
    # renunciation

    # if we have specified a country, check if the country is not part of a renunciation,
    # then the status would be Ended for all design following Hague XML schema explanations
    grantedDate = None
    if countryCode != None and histories != None:
        for history in histories:
            if "HagueRenunciation" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueRenunciation):
                    if "DesignatedCountryBag" in history.HagueRenunciation:
                        for designatedCountry in history.HagueRenunciation.DesignatedCountryBag.DesignatedCountry:
                            if isinstance(designatedCountry, str):
                                if history.HagueRenunciation.DesignatedCountryBag.DesignatedCountry.DesignatedCountryCode  == countryCode:
                                    return "Ended"
                            elif designatedCountry.DesignatedCountryCode == countryCode:
                                    return "Ended"

            # to be tested: same for HagueLimitation, which is very similar to HagueRenunciation
            if "HagueLimitation" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueLimitation):
                    if "DesignatedCountryBag" in history.HagueLimitation:
                        for designatedCountry in history.HagueLimitation.DesignatedCountryBag.DesignatedCountry:
                            if isinstance(designatedCountry, str):
                                if history.HagueLimitation.DesignatedCountryBag.DesignatedCountry.DesignatedCountryCode  == countryCode:
                                    return "Ended"
                            elif designatedCountry.DesignatedCountryCode == countryCode:
                                    return "Ended"
        
            if "HagueGrantProtection" in history and isinstance(history, dict):
                # is the design identifier in the list of affected designs?
                if designIdentifier == None or isAffectedDesignIdentifier(designIdentifier, history.HagueGrantProtection.AffectedDesign):
                    if "RecordNotifyingOfficeCode" in history.HagueGrantProtection:
                        if history.HagueGrantProtection.RecordNotifyingOfficeCode == countryCode:
                            grantedDate = history.HagueGrantProtection.InternationalRecordingDate
            
            # other events potentially impacting status: 
            # to check: HagueInvalidation, HagueMerger, however no occurance since 2018 data

    # check refusal, refusal is per designated countries, not just by design
    # unfortunately it seems that conditional refusal are encoded as refusal, so
    # so we have to look for a follow-up grant to recover this problem
    if countryCode != None:
        refusalDate = getRefusalDate(histories, designIdentifier, countryCode)
        if refusalDate != None and len(refusalDate)>0 and grantedDate is None: 
            return "Ended"

    if grantedDate is not None:
        registrationDate = grantedDate

    if registrationDate == None or len(registrationDate) == 0:
        return "Pending"

    expiryDate = getExpiryDate(expiryDate, histories, designIdentifier, countryCode)
    if expiryDate == None or len(expiryDate) == 0:
        return "Registered"
    
    try:
        registrationDateObject = datetime.strptime(registrationDate, '%Y-%m-%d').date()
        expiryDateObject = datetime.strptime(expiryDate, '%Y-%m-%d').date()
        currentDate = date.today()

        if expiryDateObject < currentDate:
            return "Expired"
        else: 
            return "Registered"
    except Exception as e: 
        print("invalid date")
        print(e)

    return "Unknown"

def isAffectedDesignIdentifier(designIdentifier, affectedDesignBlock):
    '''
    Return True if the identified design is included in the affected design information
    '''
    if "AllDesignsIndicator" in affectedDesignBlock:
        return True
    elif "DesignIdentifierBag" in affectedDesignBlock:
        affectedDesignIdentifiers = []
        for identifier in  affectedDesignBlock.DesignIdentifierBag.DesignIdentifier:
            affectedDesignIdentifiers.append(identifier)
        if designIdentifier in affectedDesignIdentifiers:
            return True
        else:
            return False
    return False

possibleEventsFromOffice = [ "HagueGrantProtection", "HagueRefusal" ]

def isApplicableToCountry(countryCode, hagueHistoryEvent):
    '''
    Return True if the history event is applicable to the provided country 
    '''
    if hagueHistoryEvent is None:
        return False

    if "RecordNotifyingOfficeCode" in hagueHistoryEvent:
        if hagueHistoryEvent.RecordNotifyingOfficeCode == countryCode:
            return True
    elif "DesignatedCountryBag" in hagueHistoryEvent:
        if hagueHistoryEvent.DesignatedCountryBag is not None:
            if "DesignatedCountry" in hagueHistoryEvent.DesignatedCountryBag:
                for designatedCountry in hagueHistoryEvent.DesignatedCountryBag.DesignatedCountry:
                    if isinstance(designatedCountry, str):
                        if hagueHistoryEvent.DesignatedCountryBag.DesignatedCountry.DesignatedCountryCode  == countryCode:
                            return True
                    elif designatedCountry.DesignatedCountryCode == countryCode:
                        return True
    return False

"""
Functions dedicated to Hague transaction history  
"""

transaction_header_elements = [ "HagueBulletinNumber", "PublicationDate" ]

def get_event_type(history):
    for child in history:
        if child.startswith("_"):
            continue
        if child not in transaction_header_elements:
            return child
    return None

def serialize(history):
    #print(history)
    jsonString = history.toJSON()
    # keeping single quote in the JSON (even escaped) will fail when going back to yaml (yaml parsing error)
    # so we need to use an alternative unicode for single quote. 
    jsonString = jsonString.replace("\'", "\u201A")
    return json.loads(jsonString)


