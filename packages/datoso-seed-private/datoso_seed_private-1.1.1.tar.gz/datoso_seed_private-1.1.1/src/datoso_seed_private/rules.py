"""Rules for the private seed."""
from datoso_seed_nointro.dats import NoIntroDat

rules = [
    {
        'name': 'Private Dat',
        '_class': NoIntroDat,
        'seed': 'private',
        'priority': 80,
        'rules': [
            {
                'key': 'name',
                'operator': 'contains',
                'value': '(Private)',
            },
        ],
    },
]


def get_rules() -> list:
    """Get the rules."""
    return rules
