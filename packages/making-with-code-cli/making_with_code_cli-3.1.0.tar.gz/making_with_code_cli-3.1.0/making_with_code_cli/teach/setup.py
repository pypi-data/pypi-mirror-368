# teach/setup.py
# --------------
# Implements `mwc teach setup`

import click
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.setup.tasks import (
    choose_mwc_username,
    prompt_mwc_password,
    choose_work_dir,
)
from making_with_code_cli.settings import (
    get_settings_path,
    read_settings, 
    write_settings,
)
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

INTRO_MESSAGE = (
    "Welcome to Making with Code setup. "
    "This command will configure your teacher role. "
    "If you also have a student role, the same config file will be used "
    "by default. You can specify a separate config file using --config."
)

REQUIRED_TEACHER_SETTINGS = [
    'mwc_username',
    'mwc_accounts_token',
    'teacher_work_dir',
]

def check_required_teacher_settings(settings):
    missing_settings = [s for s in REQUIRED_TEACHER_SETTINGS if s not in settings]
    if missing_settings:
        click.echo(error("Some settings are missing. Please run mwc teach setup."))
    return not missing_settings
    
@click.command
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("--debug", is_flag=True, help="Show debug-level output")
def setup(config, debug):
    """Configure teacher settings"""
    click.echo(address(INTRO_MESSAGE))
    click.echo()
    settings = read_settings(config)
    if debug:
        sp = get_settings_path(config)
        click.echo(debug_fmt(f"Reading settings from {sp}"))
    settings['mwc_username'] = choose_mwc_username(settings.get("mwc_username"))
    api = MWCAccountsAPI()
    if settings.get('mwc_accounts_token'):
        try:
            status = api.get_status(settings['mwc_accounts_token'])
        except api.RequestFailed as bad_token:
            token = prompt_mwc_password(settings['mwc_username'])
            settings['mwc_accounts_token'] = token
            status = api.get_status(token)
    else:
        token = prompt_mwc_password(settings['mwc_username'])
        settings['mwc_accounts_token'] = token
        status = api.get_status(token)
    if debug:
        click.echo(debug_fmt("MWC Accounts Server status:"))
        click.echo(debug_fmt(str(status)))
    settings['teacher_work_dir'] = str(choose_work_dir(
        settings.get("teacher_work_dir"), 
        teacher=True
    ))
    write_settings(settings, config)

