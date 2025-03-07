from pydantic import BaseModel, Field
from typing import Optional, Any
from icecream import ic

class ReservationData(BaseModel):
    name: str = Field(None,description="name of the person who is doing the reservation for a restaurant")
    n_guests: int = Field(0, description="number of guests of the reservation for a restaurant")
    phone: str = Field(None, description="phone number of the person who made the reservation")
    date: str = Field(None, description="date of the restaurant reservation")
    time: str = Field(None, description="time of the restaurant reservation")

def all_fields_filled(instance: BaseModel) -> bool:
    """
    Checks if all fields of a Pydantic model instance have values different from their defaults.

    Args:
        instance (BaseModel): The Pydantic model instance to check.

    Returns:
        bool: True if all fields have non-default values, False otherwise.
    """
    for field_name, field_info in instance.model_fields.items():
        default_value = field_info.default
        current_value = getattr(instance, field_name)
        
        # If the default value exists and the current value is the same, return False
        if current_value == default_value:
            return False
    
    return True  # All fields have different values from their defaults

from pydantic import BaseModel, Field


def first_field_not_filled(instance: BaseModel) -> Optional[str]:
    """
    Finds the first unmodified field in a Pydantic model and returns its description.

    Args:
        instance (BaseModel): The Pydantic model instance to check.

    Returns:
        Optional[str]: The description of the first unmodified field, or None if all are modified.
    """
    for field_name, field_info in instance.model_fields.items():  # Use `model_fields` in Pydantic v2
        default_value = field_info.default
        current_value = getattr(instance, field_name)

        # If the current value matches the default, return its description
        if current_value == default_value:
            return field_info.description if field_info.description else None
    
    return None  # All fields have been modified


def assign_if_default(instance: BaseModel, data: dict[str, Any]) -> None:
    """
    Assigns values from a dictionary to a Pydantic instance only if the attribute 
    still holds its default value.

    Args:
        instance (BaseModel): The instantiated Pydantic object.
        data (dict[str, Any]): The dictionary containing new values.
    """
    for field_name, field_info in instance.model_fields.items():
        default_value = field_info.default
        current_value = getattr(instance, field_name)

        # Check if the field has not been modified (is still at its default)
        # TODO: Validate each attribute (e.g., name format, phone number length)
        if default_value is not None:
            if current_value == default_value and field_name in data:
                setattr(instance, field_name, data[field_name])
        else:  # Handle the case where default is None
            if current_value is None and field_name in data:
                setattr(instance, field_name, data[field_name])



