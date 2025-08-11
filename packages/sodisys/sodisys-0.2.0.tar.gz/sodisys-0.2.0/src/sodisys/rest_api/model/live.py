from pydantic import BaseModel
import datetime


class LastSlot(BaseModel):
    in_time: datetime.time | None
    out_time: datetime.time | None
    date: datetime.date

    def get_checkin_timestamp(
        self, timezone: datetime.timezone
    ) -> datetime.datetime | None:
        if self.in_time is None:
            return None
        return datetime.datetime.combine(self.date, self.in_time).astimezone(timezone)

    def get_checkout_timestamp(
        self, timezone: datetime.timezone
    ) -> datetime.datetime | None:
        if self.out_time is None:
            return None
        return datetime.datetime.combine(self.date, self.out_time).astimezone(timezone)


class LiveResponse(BaseModel):
    last_slot: LastSlot | None
