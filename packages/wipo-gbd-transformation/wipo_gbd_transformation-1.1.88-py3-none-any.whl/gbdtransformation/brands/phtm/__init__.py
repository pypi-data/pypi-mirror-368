# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# PH/4/1981/00000115
# PH/M/0001/01573483 
# A/M/0001/01421820 B/M/0001/01364251 
appnum_mask = [ 'PH/\\d/\\d*/(\\d*)', 'PH/M/\\d*/(\\d*)', 'A/M/\\d*/(\\d*)', 'B/M/\\d*/(\\d*)' ]
regnum_mask = [ 'PH/\\d/\\d*/(\\d*)', 'PH/M/\\d*/(\\d*)', 'A/M/\\d*/(\\d*)', 'B/M/\\d*/(\\d*)' ]
