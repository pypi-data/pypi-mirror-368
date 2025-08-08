"""Actions for the base seed."""
from datoso_seed_eggman.dats import SegaALLDotNetDat, TeknoparrotDat

actions = {
    '{dat_origin}/teknoparrot': [
        {
            'action': 'LoadDatFile',
            '_class': TeknoparrotDat,
        },
        {
            'action': 'DeleteOld',
            'folder': '{dat_destination}',
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}',
        },
        {
            'action': 'SaveToDatabase',
        },
    ],
    '{dat_origin}/segaalldotnet': [
        {
            'action': 'LoadDatFile',
            '_class': SegaALLDotNetDat,
        },
        {
            'action': 'DeleteOld',
            'folder': '{dat_destination}',
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}',
        },
        {
            'action': 'SaveToDatabase',
        },
    ],
    # '{dat_origin}/touhou': [
    #     {
    #         'action': 'LoadDatFile',
    #         '_class': TeknoparrotDat,
    #     },
    #     {
    #         'action': 'DeleteOld',
    #         'folder': '{dat_destination}',
    #     },
    #     {
    #         'action': 'Copy',
    #         'folder': '{dat_destination}',
    #     },
    #     {
    #         'action': 'SaveToDatabase',
    #     },
    # ],
}

def get_actions() -> dict:
    """Get the actions dictionary."""
    return actions
