from pydantic import BaseModel, Field

class ReservationData(BaseModel):
    name: str = Field("",description="name of the person who made the reservation")
    #n_guests: int = Field(0,description="number of guests of the reservation")
    #phone: str = Field(description="phone number of the person who made the reservation")
    #date: str = Field(description="date of the reservation")
    #time: str = Field(description="time of the reservation")

def all_fields_filled(instance: BaseModel) -> bool:
    """
    Checks if all fields of a Pydantic model instance have values different from their defaults.

    Args:
        instance (BaseModel): The Pydantic model instance to check.

    Returns:
        bool: True if all fields have non-default values, False otherwise.
    """
    for field_name, field_info in instance.__fields__.items():
        default_value = field_info.default
        current_value = getattr(instance, field_name)
        
        # If the default value exists and the current value is the same, return False
        if default_value is not None and current_value == default_value:
            return False
    
    return True  # All fields have different values from their defaults

