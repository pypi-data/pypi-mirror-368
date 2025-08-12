# official st66 statuses
# ======================
# 01 Application Filed
# 02 Filing date accorded
# 03 Classification checked
# 05 Application published
# 06 Opposition pending
# 07 Registration published
# 08 Application refused
# 09 Application withdrawn
# 10 Appeal pending
# 11 Interruption of proceeding
# 12 Registration cancelled
# 13 Conversion requested
# 14 Registration surrendered
# 15 Revocation proceeding pending
# 16 Invalidity proceeding pending
# 17 Action before Court of Justice pending

def translate_status(status):
    if(status == 'Pending'): return 'Application Filed'
    if(status == 'Ended'): return 'Application withdrawn'
    if(status == 'Expired'): return 'Registration cancelled'
    if(status == 'Registered'): return 'Registration published'
    return status

def translate_event(kind):
    if(kind == 'Filed'): return 'Application Filed'
    if(kind == 'Registered'): return 'Registration published'
    if(kind == 'Published'): return 'Application published'
    if(kind == 'Opposed'): return 'Opposition pending'
    if(kind == 'Withdrawn'): return 'Application withdrawn'
    return kind
