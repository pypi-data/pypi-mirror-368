status = ['Ended', 'Expired', 'Pending', 'Registered', 'Unknown', 'Delete']

features = ['Word',
            'Stylized characters',
            'Figurative',
            'Combined',
            'Three dimensional',
            'Colour',
            'Sound',
            'Hologram',
            'Olfactory',
            'Motion',
            'Multimedia',
            'Position',
            'Pattern',
            'Touch',
            'Taste',
            'Tracer',
            'Other',
            'Undefined']

kinds = ['Individual','Collective','Certificate','Defensive','Other','Membership', 'Slogan']

events = ['Filed', 'Registered', 'Published', 'Pending', 'Inactive',
          'Opposed', 'Withdrawn', 'Expired', 'Examined', 'Invalidated',
          'Rejected', 'Abandoned', 'Suspended', 'Surrendered', 'Appealed',
          'Awaiting court action', 'Converted', 'Notification', 'Unknown']

st13_identifier = \
        { 'national': { 'trademark': '50',
                        'emblem': '51',
                        'ao': '52',
                        'gi': '52',
                        'other': '59' },
          'multinational': { 'trademark': '50' },
          # special case for internationals: by status and reference
          'international': { 'registered': '50',
                             'pending-basicapplicationnumber': '62',
                             'pending-basicregistrationnumber': '61',
                             'inn': '82',
                             'ao': '81',
                             'gi': '81',
                             'emblem': '80' },
          }
