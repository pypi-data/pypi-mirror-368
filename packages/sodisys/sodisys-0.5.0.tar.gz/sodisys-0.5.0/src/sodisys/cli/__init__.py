from logging import INFO
from aiohttp.client import ClientSession
import asyncclick as click
from asyncclick.core import Context
import coloredlogs

from sodisys.sodisys import Sodisys
from sodisys.cli.commands import checkin_status
from sodisys.cli.commands import user_info


@click.group()
@click.version_option()
@click.option("username", "--user", help="Username used for login.", required=True)
@click.option("password", "--password", help="Password used for login.", required=True)
@click.pass_context
async def cli(  # noqa: PLR0913
    ctx: Context,
    username: str,
    password: str,
) -> None:
    coloredlogs.install(level=INFO)

    ctx.ensure_object(dict)
    ctx.obj["username"] = username
    ctx.obj["password"] = password

    session = ClientSession()
    sodisys = Sodisys(session)

    await sodisys.login(username, password)

    ctx.obj["session"] = session
    ctx.obj["sodisys"] = sodisys


cli.add_command(checkin_status)
cli.add_command(user_info)


@cli.result_callback()
@click.pass_context
async def disconnect(  # noqa: PLR0913
    ctx: Context,
    result: None,  # noqa: ARG001
    username: str,  # noqa: ARG001
    password: str,  # noqa: ARG001
) -> None:
    session: ClientSession = ctx.obj["session"]

    await session.close()
