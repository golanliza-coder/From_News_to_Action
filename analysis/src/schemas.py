from typing import List
from pydantic import BaseModel, Field


class TrafficAccidentExtract(BaseModel):
    is_traffic_accident: bool = Field(
        description="True אך ורק אם מדובר בתאונת דרכים הכוללת כלי רכב, אופנוע, קורקינט, אופניים או פגיעת רכב בהולך רגל. False עבור הפגנות, מחאות, פיגועים, אירועים ביטחוניים, קטטות, נפילות בבית או אירועים רפואיים שאינם תאונת דרכים."
    )
    accident_severity: str = Field(
        description="חומרת התאונה: light, moderate, severe, fatal, או 'not specified'"
    )
    vehicle_types: List[str] = Field(
        description="רשימת רכבים באנגלית: car, bus, motorcycle, bicycle, electric scooter, truck"
    )
    vulnerable_users_and_ages: str = Field(
        description="תיאור נפגעים פגיעים וגילאים (הולכי רגל, ילדים, קשישים) או 'none'"
    )
    human_factor: str = Field(
        description="גורם אנושי או 'not specified'"
    )
    verbal_location: str = Field(
        description="מיקום מדויק בישראל לחילוץ גיאוגרפי או 'not specified'"
    )
