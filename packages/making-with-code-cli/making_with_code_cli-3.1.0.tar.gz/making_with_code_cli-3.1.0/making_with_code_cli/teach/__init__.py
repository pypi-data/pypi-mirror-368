import click
from making_with_code_cli.teach.setup import setup
from making_with_code_cli.teach.update import update
from making_with_code_cli.teach.status import status
from making_with_code_cli.teach.log import log
from making_with_code_cli.teach.patch import patch
from making_with_code_cli.teach.check import check

@click.group()
def teach():
    "Commands for teachers"

teach.add_command(setup)
teach.add_command(update)
teach.add_command(status)
teach.add_command(log)
teach.add_command(patch)
teach.add_command(check)
