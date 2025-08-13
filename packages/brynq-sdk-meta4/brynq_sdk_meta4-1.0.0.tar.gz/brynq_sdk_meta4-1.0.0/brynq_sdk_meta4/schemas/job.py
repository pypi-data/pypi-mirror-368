"""
Meta4 Job schema based on EQU_Interfaz_Puestos specification.

This schema defines the structure for job data that will be exported to Meta4 HR system.
The schema includes movement type, job information, and date fields with proper formatting.

"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime


class JobSchema(BaseModel):
    """
    Pydantic schema for Meta4 Job data.
    Based on EQU_Interfaz_Puestos specification.
    """

    # Movement Information
    movement_type: Literal["-28", "-29"] = Field(description="Tipo de movimiento", example="-28", alias="Tipo de movimiento", max_length=3)

    # Job Information
    job_id: Optional[str] = Field(None, description="ID Puesto", example="100", alias="ID Puesto", max_length=8)
    job_name: Optional[str] = Field(None, description="Nombre Puesto", example="Puesto 1", alias="Nombre Puesto", max_length=62)
    start_date: Optional[datetime] = Field(None, description="Fecha inicio", example="01/01/1800", alias="Fecha Inicio", max_length=10)
    end_date: Optional[datetime] = Field(None, description="Fecha fin", example="01/01/180", alias="Fecha Fin ", max_length=10)
    cno_subcode: Optional[str] = Field(None, description="ID Subcódigo CNO del Puesto", example="1120", alias="CNO", max_length=4)

    @model_validator(mode='after')
    def validate_movement_requirements(self):
        """Validate mandatory fields based on movement_type"""
        if self.movement_type == "-28":
            # All fields are mandatory for CREATE (-28)
            mandatory_fields_create = ['job_id', 'job_name', 'start_date', 'end_date', 'cno_subcode']
            for field_name in mandatory_fields_create:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for CREATE (-28) movement")
        elif self.movement_type == "-29":
            # Only basic fields are mandatory for UPDATE (-29)
            mandatory_fields_update = ['job_id', 'job_name']
            for field_name in mandatory_fields_update:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for UPDATE (-29) movement")
        return self

    # --- DATETIME PARSE ---
    @field_validator("start_date", "end_date", mode="before")
    def parse_dd_mm_yyyy(cls, v):
        if v in (None, "") or isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%d/%m/%Y")

    class Config:
        json_encoders = {datetime: lambda d: d.strftime("%d/%m/%Y")}
        allow_population_by_field_name = True
        populate_by_name = True
