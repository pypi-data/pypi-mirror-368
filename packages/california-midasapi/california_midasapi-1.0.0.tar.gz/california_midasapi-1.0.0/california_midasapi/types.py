from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
from dateutil import parser

@dataclass
class RateListItem():
    RateID: str
    SignalType: str
    Description: str
    LastUpdated: Optional[str] = None

@dataclass
class ValueInfoItem:
    ValueName: str
    DateStart: str
    DateEnd: str
    DayStart: str
    DayEnd: str
    TimeStart: str
    TimeEnd: str
    value: float
    Unit: str

    __startDateTime = None
    def GetStart(self) -> datetime:
        """Get the start of this tariff as a python datetime"""
        if self.__startDateTime is None:
            self.__startDateTime = parser.parse(f"{self.DateStart} {self.TimeStart}Z")
        return self.__startDateTime

    __endDateTime = None
    def GetEnd(self) -> datetime:
        """Get the end of this tariff as a python datetime"""
        if self.__endDateTime is None:
            self.__endDateTime = parser.parse(f"{self.DateEnd} {self.TimeEnd}Z")

            """Correct end dates that incorrectly cross over into next day (#1)"""
            startDate = parser.parse(self.DateStart)
            endDate = parser.parse(self.DateEnd)
            if endDate - startDate == timedelta(days=1) and self.DayStart == self.DayEnd:
                self.__endDateTime = parser.parse(f"{self.DateStart} {self.TimeEnd}Z")

        return self.__endDateTime

@dataclass
class RateInfo:
    RateID: str
    SystemTime_UTC: str
    RateName: str
    RateType: str
    Sector: str
    API_Url: str
    RatePlan_Url: str
    EndUse: str
    AltRateName1: str
    AltRateName2: str
    SignupCloseDate: str
    ValueInformation: list[ValueInfoItem] = field(default_factory=list)
    """The list of tariffs"""

    def GetActiveTariffs(self, time: datetime) -> list[ValueInfoItem]:
        """Gets all tariffs that are active at the specified time."""
        timestamp = time.timestamp()
        return list(filter(lambda t: t.GetStart().timestamp() < timestamp and t.GetEnd().timestamp() > timestamp, self.ValueInformation))

    def GetCurrentTariffs(self) -> list[ValueInfoItem]:
        """Gets all tariffs that are currently active."""
        return self.GetActiveTariffs(datetime.now())
        
