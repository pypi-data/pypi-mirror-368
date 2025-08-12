render = 'JSON'
source = 'national'

# TN/M/100/901864 # madrid
# TN/E/2002/001864 # etrangere
# TN/T/2019/001877 # local
# TN/S/2005/001886
appnum_mask = ['AP/(T|E|S|M)/\\d{4}/(\\d*)']

# 100/901864
# 2009/002484
# 001818
regnum_mask = [ '\\d*/(\\d*)',
                '(\\d*)' ]

