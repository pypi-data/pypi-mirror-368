render = 'JSON'
source = 'national'

# BT/M/811870 # madrid
# A/M/807290 # madrid
# T/2000/1870
appnum_mask = [ 'BT/(M)/(\\d*)',
                '([A-Z])/(M)/(\\d*)',
                'T/\\d{4}/(\\d*)',
                '(\\d*)' ]
