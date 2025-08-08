"""Rules for the 'eggman' seed."""
from datoso_seed_eggman.dats import TeknoparrotDat

rules = [
    {
        'name': 'Teknoparrot Dat',
        '_class': TeknoparrotDat,
        'seed': 'eggman',
        'priority': 0,
        'rules': [
            {
                'key': 'author',
                'operator': 'contains',
                'value': 'EggmanPEI',
            },
            {
                'key': 'homepage',
                'operator': 'eq',
                'value': 'https://discord.gg/27Bsg5BzQN',
            },
        ],
    },
]


def get_rules() -> list:
    """Get the rules."""
    return rules
