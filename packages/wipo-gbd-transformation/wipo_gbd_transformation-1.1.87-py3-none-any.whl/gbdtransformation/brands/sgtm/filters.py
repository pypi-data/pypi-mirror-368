import re
from gbdtransformation.common.filters import country_name2code, get_value

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Trade Mark': return ['Individual']
    if kind == 'Collective Mark': return ['Collective']
    if kind == 'Certification Mark': return ['Certificate']

    if kind == 'Collective Mark/ Certificate Mark/ Guarantee Mark': return ['Certificate', 'Collective']
    if kind == 'Collective, certification or guarantee mark': return ['Certificate', 'Collective']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status, prev_status=''):
    if status == 'Destroyed': return 'Delete'

    if status == 'Deleted': return 'Ended'
    if status == 'Abandoned': return 'Ended'
    if status == 'Cancelled': return 'Ended'
    if status == 'Deemed Never Made': return 'Ended'
    if status == 'Application Deemed Never Made': return 'Ended'
    if status == 'Registration Deemed Never Made': return 'Ended'
    if status == 'Withdrawn': return 'Ended'
    if status == 'Treated As Withdrawn': return 'Ended'
    if status == 'Treated as Withdrawn': return 'Ended'
    if status == 'Treated As Withdrawn (Reinstatable)': return 'Ended'
    if status == 'Treated As Withdrawn (Reinstatement Pending)': return 'Ended'
    if status == 'Treated As Withdrawn (Continued Processing Possible)': return 'Pending'
    if status == 'Refused': return 'Ended'
    if status == 'Refunded': return 'Ended'
    if status == 'Revoked': return 'Ended'

    if status == 'Registered': return 'Registered'
    if status == 'Split': return 'Registered'
    if status == 'Split (Partially Assigned)': return 'Registered'

    if status == 'Divided': return 'Pending'
    if status == 'Recorded': return 'Pending'
    if status == 'Pending': return 'Pending'
    if status == 'Pending (Published)': return 'Pending'
    if status == 'Pending (Under Examination)': return 'Pending'
    if status == 'Pending (Formalities Check)': return 'Pending'

    if status == 'Expired': return 'Expired'
    if status == 'Expired (Late Renewal Possible)': return 'Expired'
    if status == 'Expunged': return 'Expired'
    if status == 'Removed': return 'Expired'
    if status == 'Removed (Restoration Possible)': return 'Expired'
    if status == 'Expired (Renewal Possible)': return 'Expired'
    raise Exception('status/prev_status "%s/%s" is not mapped.' % (status, prev_status))

def translate_feature(trademark):
    if trademark.three_dimensional_shape == 'Y': return 'Three dimensional'
    if trademark.aspect_of_packaging == 'Y': return 'Three dimensional'
    if trademark.color_as_a_trademark == 'Y': return 'Colour'
    if trademark.non_conventional_mark == 'Hologram': return 'Hologram'
    if trademark.non_conventional_mark == 'Movement': return 'Motion'
    if trademark.non_conventional_mark == 'Scent': return 'Olfactory'
    if trademark.non_conventional_mark == 'Sound': return 'Sound'

    has_verbal = trademark.mark_description is not None
    try:
        mark_signif = trademark.mark_index.words_in_mark
        # sometimes has an attribute
        if not isinstance(mark_signif, str):
            mark_signif = mark_signif.__value
        has_verbal = has_verbal or mark_signif
    except: pass

    try:
        has_transliteration = trademark.mark_index.transliteration
    except:
        has_transliteration = False

    has_image = False
    try:
        has_image = not trademark.logo_details.file_name.upper().endswith('.TIF')
    except: pass

    if has_verbal and has_image: return 'Combined'
    if has_verbal and not has_image: return 'Word'
    if not has_verbal and not has_transliteration and has_image: return 'Figurative'
    if has_transliteration: return 'Stylized characters'

    return 'Undefined'

def format_applicant_address(applicant):
    country_name = applicant.country
    addr = []

    state = applicant.get('state') or ''
    if state: addr.append(state)

    for i in range(1,5):
        # remove country name from address line
        line = applicant.get('company_addr%s' % i) or ''
        line = line.rstrip('.').strip()
        if country_name:
            line = re.sub(re.escape(country_name), '', line, flags=re.IGNORECASE)
            line = line.replace(country_name, '')
        if line == '#-': line = ''
        line = line.strip().rstrip(',')

        if line: addr.append(line)

    return ', '.join(addr)

def format_representative_address(agent):
    country_code = None
    addr = []
    for i in range(1,5):
        line = agent.get('agent_addr%s' % i) or agent.get('afs_addr%s' % i) or ''
        if line.upper().find('SINGAPORE') > -1:
            country_code = 'SG'
            line = re.sub(re.escape('SINGAPORE'), '', line, flags=re.IGNORECASE)
        line = line.strip()

        if line: addr.append(line)

    return (country_code, ', '.join(addr))

def get_country_code(country_name):
    if not country_name: return
    # sometimes we have 2 countries indicated => map the first one
    # france; switzerland
    # korea & japan
    country_name = country_name.split('; ')[0].split(' & ')[0]

    try:
        country_code = country_name2code(country_name)
        return country_code
    except:
        pass

def get_priority_country_code(country_name):
    if not country_name: return
    try:
        country_code = country_name2code(country_name)
        return country_code
    except:
        pass

def get_prio_gs(elem, dflt='all'):
    value = get_value(elem) or dflt
    return '(%s)' % value.replace('"', '')

def get_mark_names(trademark):
    mark_name = trademark.mark_description or ''
    try:
        mark_signif = trademark.mark_index.words_in_mark
        if not isinstance(mark_signif, str):
            mark_signif = mark_signif.__value
        if not mark_signif:
            mark_signif = ''
    except: mark_signif = ''

    # happens to have the tag repeated (bof)
    if isinstance(mark_name, list):
        mark_name = mark_name[0] or ''
    if isinstance(mark_signif, list):
        mark_signif = mark_signif[0] or ''

    # no need to duplicate information
    if mark_name.lower() == mark_signif.lower():
        return (mark_name, '')

    if mark_signif and not mark_name:
        mark_name = mark_signif
        mark_signif = ''

    return (mark_name, mark_signif)
