render = 'JSON'
source = 'national'

# KH/1071853A/M # madrid
# KH/G/2018/5 # gi
# KH/49703/13 # domestic
appnum_mask = [ 'KH/(G)/\\d{4}/(.)',
                'KH/(.*)/(M)',
                'KH/(.*)/\\d{4}',
                'KH/(.*)/(\\d{2})']

regnum_mask = [ 'KH/\\d{4}/(\\d*)',
                'KH/M/(.*)' ]

