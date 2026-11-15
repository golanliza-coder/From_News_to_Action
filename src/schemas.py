from pydantic import BaseModel, Field
from typing import List, Literal

class TrafficAccidentExtract(BaseModel):
    is_traffic_accident: bool = Field(
        description="True ONLY if the report describes a real traffic accident. False for protests, security incidents, or domestic events."
    )
    accident_severity: Literal['קלה', 'בינונית', 'קשה', 'קטלנית', 'לא מצוין'] = Field(
        default='לא מצוין',
        description="Medical severity of the injury. Must be 'לא מצוין' if not explicitly stated in the text."
    )
    location_raw_text: str = Field(
        description="Extracted raw Hebrew location string (e.g., highway number, interchange, street and city)."
    )
    involved_vehicles: List[str] = Field(
        default_factory=list,
        description="List of involved vehicles or road users (e.g., רכב פרטי, אופנוע, קורקינט חשמלי, הולך רגל)."
    )
