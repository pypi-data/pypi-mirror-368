from .data import aircraft
from .data import airport
from .data import aliases
from .data import assignment
from .data import commodity
from .data import config
from .data import facility
from .data import fbo
from .data import flight
from .data import member
from .data import status
from .data import summary


#: FSEconomy APIs and versions
API_VERSIONS = {
    'data': 'https://server.fseconomy.net/data',
    'fse': 'https://server.fseconomy.net/rest/fse/api',
    'static': 'https://server.fseconomy.net/static',
    'v1': 'https://server.fseconomy.net/rest/api',
    'v2': 'https://server.fseconomy.net/rest/api/v2'
}


#: Server maintenance token string
MAINTENANCE = "Currently Closed for Maintenance"


#: FSEconomy Data Feeds with their respective parameters and parser function
DATA_FEEDS = {
    'aircraft status by registration': {
        'query': 'aircraft',
        'search': 'status',
        'rakey': False,
        'params': ['aircraftreg'],
        'decode': status.decode
    },
    'aircraft configs': {
        'query': 'aircraft',
        'search': 'configs',
        'rakey': False,
        'decode': config.decode
    },
    'aircraft aliases': {
        'query': 'aircraft',
        'search': 'aliases',
        'rakey': False,
        'decode': aliases.decode
    },
    'aircraft for sale': {
        'query': 'aircraft',
        'search': 'forsale',
        'rakey': False,
        'decode': aircraft.decode
    },
    'aircraft by makemodel': {
        'query': 'aircraft',
        'search': 'makemodel',
        'rakey': False,
        'params': ['makemodel'],
        'decode': aircraft.decode
    },
    'aircraft by ownername': {
        'query': 'aircraft',
        'search': 'ownername',
        'rakey': False,
        'params': ['ownername'],
        'decode': aircraft.decode
    },
    'aircraft by registration': {
        'query': 'aircraft',
        'search': 'registration',
        'rakey': False,
        'params': ['aircraftreg'],
        'decode': aircraft.decode
    },
    'aircraft by id': {
        'query': 'aircraft',
        'search': 'serialnumber',
        'rakey': False,
        'params': ['serialnumber'],
        'decode': aircraft.decode
    },
    'aircraft by key': {
        'query': 'aircraft',
        'search': 'key',
        'rakey': True,
        'decode': aircraft.decode
    },
    'assignments by key': {
        'query': 'assignments',
        'search': 'key',
        'rakey': True,
        'decode': assignment.decode
    },
    'commodities by key': {
        'query': 'commodities',
        'search': 'key',
        'rakey': True,
        'decode': commodity.decode
    },
    'facilities by key': {
        'query': 'Facilities',
        'search': 'key',
        'rakey': True,
        'decode': facility.decode
    },
    'fbos by key': {
        'query': 'fbos',
        'search': 'key',
        'rakey': True,
        'decode': fbo.decode
    },
    'fbos for sale': {
        'query': 'fbos',
        'search': 'forsale',
        'rakey': False,
        'decode': fbo.decode
    },
    'fbo monthly summary by icao': {
        'query': 'fbos',
        'search': 'monthlysummary',
        'rakey': True,
        'params': ['month', 'year', 'icao'],
        'decode': summary.decode
    },
    'flight logs by key month year': {
        'query': 'flightlogs',
        'search': 'monthyear',
        'rakey': True,
        'params': ['month', 'year'],
        'decode': flight.decode
    },
    'flight logs by reg month year': {
        'query': 'flightlogs',
        'search': 'monthyear',
        'rakey': False,
        'params': ['aircraftreg', 'month', 'year'],
        'decode': flight.decode
    },
    'flight logs by serialnumber month year': {
        'query': 'flightlogs',
        'search': 'monthyear',
        'rakey': False,
        'params': ['serialnumber', 'month', 'year'],
        'decode': flight.decode
    },
    'flight logs by key from id': {
        'query': 'flightlogs',
        'search': 'id',
        'rakey': True,
        'params': ['fromid'],
        'decode': flight.decode
    },
    'flight logs by key from id for all group aircraft': {
        'query': 'flightlogs',
        'search': 'id',
        'rakey': True,
        'params': ['fromid', 'type'],
        'decode': flight.decode
    },
    'flight logs by reg from id': {
        'query': 'flightlogs',
        'search': 'id',
        'rakey': False,
        'params': ['fromid', 'aircraftreg'],
        'decode': flight.decode
    },
    'flight logs by serialnumber from id': {
        'query': 'flightlogs',
        'search': 'id',
        'rakey': False,
        'params': ['fromid', 'serialnumber'],
        'decode': flight.decode
    },
    'group members': {
        'query': 'group',
        'search': 'members',
        'rakey': True,
        'decode': member.decode
    }
}


DATA_FILES = {
    'airports': {
        'filename': 'airports.csv',
        'decode': airport.decode
    }
}
