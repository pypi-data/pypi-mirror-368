# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def get_full_address(applicant):
    if applicant.postalCode:
        return "%s %s" % (applicant.address, applicant.postalCode)
    return  applicant.address

def translate_status(status, status_is):
    # office did not map to english -> we do it
    if 'Áfrýjun' in status_is: return 'Pending' # Appeal
    if status_is == 'Afturkallað': return 'Ended' # Revoked
    if status_is == 'Birt': return 'Pending' # Published
    if status_is == 'Andmæli': return 'Registered' # Published
    if status_is == 'Krafa um niðurfellingu': return 'Ended' # Request for cancellation
    if status_is == 'Tilbúið til birtingar': return 'Pending' # Ready for publishing
    if status_is == 'Í rannsókn': return 'Registered' # Investigating ..
    if status_is == 'Krafa um ógildingu': return 'Registered' # Claim for annulment ..
    if status_is == 'Rannsóknarhæft': return 'Pending' #Researchable or in their office Application
    if status_is == 'Fyrsta höfnun': return 'Pending' #First rejection or in their office Application
    if status_is == 'Hafna': return 'Ended' #Rejection or in their office Application
    if status_is == 'Vafamál': return 'Registered' #Investigating or in their office Application
    if status_is == 'Endurupptökufrestur': return 'Pending' #Re-admission deadline (Trad)
    if 'Í bi' in status_is: return 'Pending' #On hold
    if 'nari sko' in status_is: return 'Pending'
    if 'Rökstu' in status_is: return 'Pending'
    if status_is == 'Rökstuningur': return 'Pending'
    if status_is == 'Synja': return 'Ended'
    if status_is == 'Umsögn hjá NS': return 'Pending'

    if status == 'Filed': return 'Pending'
    if status == 'Expired': return 'Expired'
    if status == 'Ended': return 'Ended'
    if status == 'Registered': return 'Registered'

    return 'Unknown'
    #raise Exception('status "%s" unmapped' % status)


def translate_feature(feature, is3D):
    if not feature: return 'Undefined'

    if is3D: return "Three dimensional"
    if feature == 'orð- og myndmerki': return "Combined"
    if feature == 'myndmerki': return "Figurative"
    if feature == 'orðmerki': return "Word"
    if feature == 'orðmerki skannað': return "Stylized characters"
    if feature == 'hljóðmerki': return "Sound"
    if feature == 'þrívíddarmerki með orðhluta': return "Three dimensional"
    if feature == 'staðsetningarmerki': return "Position"
    if feature == 'annað': return "Other"
    if feature == 'hreyfimerki': return "Motion"
    if feature == 'mynsturmerki': return "Pattern"
    if feature == 'margmiðlunarmerki': return "Multimedia"

    return 'Other'
    #raise Exception('feature "%s" unmapped' % feature)

