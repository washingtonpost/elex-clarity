# mapping a partial contest names to IDs
# these get slugified and partially matched in order
# against slugified contest names
STATE_OFFICE_ID_MAPS = {
    "GA": {
        'US President': 'P',
        'President of the United States': 'P',
        'US Senate (Loeffler) - Special': 'S2',
        'US Senat': 'S', # covers both US Senate and U.S. Senator
        "United States Senat": "S",  # covers both US Senate and U.S. Senator
        "United States House": "H",
        'US Congress': 'H',
        'US House': 'H',
        'United States Congress': 'H',
        "United States Rep": "H",
        'US Rep': 'H',
        'Governor': 'G',
        'Secretary of State': 'R'
    },
    "WV": {
        'PRESIDENT': 'P',
        'U.S. SENATOR': 'S'
    },
    "CA": {
    },
    "IA": {
        'US President': 'P',
        'President of the United States': 'P',
        'US Senat': 'S', # covers both US Senate and U.S. Senator
        "United States Senat": "S",  # covers both US Senate and U.S. Senator
        "United States House": "H",
        'US Congress': 'H',
        'US House': 'H',
        'United States Congress': 'H',
        "United States Rep": "H",
        'US Rep': 'H',
        'Governor': 'G',
        'Secretary of State': 'R'
    },
    "AR": {
        'US President': 'P',
        'President of the United States': 'P',
        'US Senat': 'S', # covers both US Senate and U.S. Senator
        "United States Senat": "S",  # covers both US Senate and U.S. Senator
        "United States House": "H",
        'US Congress': 'H',
        'US House': 'H',
        'United States Congress': 'H',
        "United States Rep": "H",
        'US Rep': 'H',
        'Governor': 'G',
        'Secretary of State': 'R'
    }
}

STATE_RACE_TYPE_MAPS = {
    "GA": {
        'US Senate - Rep': 'R',
        'REP - US Senate': 'R',
        'DEM - US Senate': 'D',
        'US Senate - Dem': 'D',
        'Governor - Rep': 'R',
        'REP - Governor': 'R',
        'DEM - Governor': 'D',
        'Governor - Dem': 'D',
        'Secretary of State - Rep': 'R',
        'REP - Secretary of State': 'R',
        'DEM - Secretary of State': 'D',
        'Secretary of State - Dem': 'D',
        'Primary': 'P',
        "US Senate/ Senado de los EE.UU. - Rep": 'R',
        'US Senate/ Senado de los EE.UU. - Dem': 'D',
        'Governor/Gobernador - Rep': 'R',
        'Governor/Gobernador - Dem': 'D',
        'Secretary of State/ Secretario de Estado - Rep': 'R',
        'Secretary of State/ Secretario de Estado - Dem': 'D'
    }
}
