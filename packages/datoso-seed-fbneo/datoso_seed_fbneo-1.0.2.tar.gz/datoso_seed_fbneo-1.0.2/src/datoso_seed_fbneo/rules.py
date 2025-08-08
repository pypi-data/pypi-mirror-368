"""Rules for the Finalburn Neo seed."""
from datoso_seed_fbneo.dats import FbneoDat

rules = [
    {
        'name': 'Fbneo Dat',
        '_class': FbneoDat,
        'seed': 'fbneo',
        'priority': 50,
        'rules': [
            {
                'key': 'url',
                'operator': 'contains',
                'value': 'neo-source.com',
            },
            {
                'key': 'author',
                'operator': 'eq',
                'value': 'FinalBurn Neo',
            },
        ],
    },
]


def get_rules() -> list:
    """Get the rules."""
    return rules
