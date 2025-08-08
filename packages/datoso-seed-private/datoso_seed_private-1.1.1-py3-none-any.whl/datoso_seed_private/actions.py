"""Actions for the No-Intro seed."""
from datoso_seed_private.dats import PrivateDat

actions = {
    '{dat_origin}/{folder}': [
        {
            'action': 'LoadDatFile',
            '_class': PrivateDat,
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
}

def get_actions() -> dict:
    """Get the actions dictionary."""
    # TODO(laromicas): Add the other folder to actions if selected.
    # more_folders = ['Non-Game', 'Redump BIOS', 'Redump Custom', 'Source Code', 'Unofficial']   # noqa: ERA001
    folders = ['No-Intro', 'Non-Redump']
    new_actions = {}
    for folder in folders:
        folder_name = '{dat_origin}/' + folder
        new_actions[folder_name] = actions['{dat_origin}/{folder}']
    return new_actions
