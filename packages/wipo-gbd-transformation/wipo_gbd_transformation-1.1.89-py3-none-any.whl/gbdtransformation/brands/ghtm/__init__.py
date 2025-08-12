render = 'JSON'
source = 'national'

# GH/T/2006/1880
# MD/M/1/1187738 # madrid
appnum_mask = [ 'GH/T/\\d{4}/(\\d*)',
                'GH/T/(\\d{1,3})/(\\d*)',
                '(WP)/T/\\d{4}/(\\d*)',
                'MD/(T|M)/\\d{4}/(\\d*)',
                'MD/(M)/1/(\\d*)' ,
                'GH/(M)/2/(\\d*)' ,
                'B/(M)/1/(\\d*)' ]
