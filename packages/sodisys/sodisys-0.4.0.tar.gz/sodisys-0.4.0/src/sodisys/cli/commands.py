import datetime
import asyncclick as click
from asyncclick import Context
from rich import print


@click.command()
@click.pass_context
async def checkin_status(ctx: Context) -> None:
    live = await ctx.obj["sodisys"].get_live()

    if live.last_slot is None:
        print("No checkin data available for today")
        return

    print(
        "checkin at",
        live.last_slot.get_checkin_timestamp(
            datetime.timezone(datetime.timedelta(hours=2))
        ),
    )
    print(
        "checkout at",
        live.last_slot.get_checkout_timestamp(
            datetime.timezone(datetime.timedelta(hours=2))
        ),
    )


@click.command()
@click.pass_context
async def user_info(ctx: Context) -> None:
    data = await ctx.obj["sodisys"].get_data()

    print("first name:", data.user_details.firstname)
    print("last name:", data.user_details.lastname)
