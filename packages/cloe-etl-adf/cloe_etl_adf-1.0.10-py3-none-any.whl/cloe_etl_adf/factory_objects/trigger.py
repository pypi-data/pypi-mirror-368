from datetime import datetime, timedelta
from typing import Literal

from cloe_metadata.utils import writer
from croniter import croniter
from pydantic import BaseModel, ConfigDict, Field


class ScheduleTriggerTypeProperties(BaseModel):
    recurrence: dict[str, str | dict[str, list[str]] | int]
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )

    @classmethod
    def transform_cron_to_recurrence(cls, cron: str, timezone: str) -> dict:
        d_tomorrow = datetime.today() + timedelta(days=1)
        cron_iter = croniter(cron, d_tomorrow)
        next_date = cron_iter.get_next(datetime)
        starttime = next_date.strftime("%Y-%m-%dT%H:%M:%S")
        base = datetime(2020, 1, 1, 0, 0)
        cron_iter = croniter(cron, base)
        next_date = cron_iter.get_next(datetime)
        minutes = []
        hours = []
        weekdays = []
        while (next_date - base) < timedelta(days=31):
            hours.append(next_date.hour)
            minutes.append(next_date.minute)
            weekdays.append(next_date.strftime("%A"))
            next_date = cron_iter.get_next(datetime)
        minutes = list(set(minutes))
        hours = list(set(hours))
        weekdays = list(set(weekdays))
        if len(minutes) != 60 or len(hours) != 24:
            schedule = {"hours": hours, "weekDays": weekdays, "minutes": minutes}
        elif len(weekdays) != 7:
            schedule = {"weekDays": weekdays}
        else:
            schedule = None
        if schedule:
            return {
                "frequency": "Week",
                "interval": 1,
                "startTime": starttime,
                "timeZone": timezone,
                "schedule": schedule,
            }
        return {
            "frequency": "Week",
            "interval": 1,
            "startTime": starttime,
            "timeZone": timezone,
        }


class TriggerProperties(BaseModel):
    annotations: list[str] = []
    runtime_state: Literal["Stopped"] = "Stopped"
    pipelines: list[dict[str, dict[str, str]]]
    arm_type: Literal["ScheduleTrigger"] = Field(
        default="ScheduleTrigger",
        alias="type",
    )
    type_properties: ScheduleTriggerTypeProperties
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )


class Trigger(BaseModel):
    name: str
    properties: TriggerProperties
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )
