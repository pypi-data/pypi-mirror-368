render = 'JSON'
source = 'national'

# MD/D/1/936430
# SZ/T/1986/460
# SA/T/1977/61
# A/D/1/807290
appnum_mask = [ 'SZ/(T|D)/\\d{4}/(\\d*)',
                'SZ/(T|D)/(\\d{1,3})/\\d{4}',
                'SZ/(T|D)/\\d{1,3}/(\\d*)',
                'MD/(D)/1/(\\d*)',
                '([A-C])/D/1/(\\d*)',
                '(SA)/(T|D)/\\d{4}/(\\d*)',
                '(GB)/T/\\d{4}/(\\d*)' ]
