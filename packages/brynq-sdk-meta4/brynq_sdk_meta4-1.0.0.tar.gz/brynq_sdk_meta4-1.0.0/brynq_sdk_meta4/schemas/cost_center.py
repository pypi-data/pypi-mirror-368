from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional


class CostCenterSchema(BaseModel):
    """
    Pydantic schema for Meta4 Cost Center data.
    Based on EQU_Interfaz_Centros_Coste specification.
    """

    # Movement Information
    movement_type: Literal["-36", "-37"] = Field(description="Tipo de movimiento", example="-36", alias="Tipo de movimiento", max_length=3)

    # Cost Center Information
    cost_center_id: Optional[str] = Field(None, description="ID Centro de Coste", example="C200", alias="ID Centro de Coste", max_length=50)
    cost_center_name: Optional[str] = Field(None, description="Nombre Centro de Coste", example="Centro de Coste Principal", alias="Nombre Centro de Coste", max_length=62)

    @model_validator(mode='after')
    def validate_movement_requirements(self):
        """Validate mandatory fields based on movement_type"""
        if self.movement_type == "-36":
            # All fields are mandatory for CREATE (-36)
            mandatory_fields_create = ['cost_center_id', 'cost_center_name']
            for field_name in mandatory_fields_create:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for CREATE (-36) movement")
        elif self.movement_type == "-37":
            # Only cost_center_id is mandatory for UPDATE (-37)
            mandatory_fields_update = ['cost_center_id']
            for field_name in mandatory_fields_update:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for UPDATE (-37) movement")
        return self

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
