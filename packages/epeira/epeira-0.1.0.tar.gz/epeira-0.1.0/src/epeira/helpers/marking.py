"""Convenience tools for marking classes and Fields."""
from pydantic import ConfigDict, Field

from epeira.helpers.parsing import get_default_archetype_prefix, get_subcomponent_indicator


def get_model_type(field):
    """Determine if the field has a model type and return it. Return None if not."""
    extra = getattr(field, "json_schema_extra", None)
    if extra and isinstance(extra, dict):
        return extra.get("model_type")
    return None

def model_archetype(cls, indicator=get_default_archetype_prefix()):
    """Mark a class as an archetype.

    This is a decorator.
    """
    # TODO: potentially check that archetype-parseable
    config = getattr(cls, 'model_config', ConfigDict())
    config = ConfigDict(**config, json_schema_extra={"is_archetype": True,
                                                     "archetype_indicator":indicator})
    cls.model_config = config
    return cls

def TypedModel(model_type: str, **kwargs):
    """Assign a model type to a field.

    Takes a string description of what model type it is.
    """
    return Field(..., json_schema_extra={"model_type": model_type}, **kwargs)

def is_subcomponent(field):
    """Check if a field has been marked as a subcomponent."""
    return get_model_type(field) == get_subcomponent_indicator()

def Subcomponent():
    """Make sure field is typed as a subcomponent."""
    return TypedModel(model_type=get_subcomponent_indicator())

def is_archetype(cls):
    """Check if a class is an archetype."""
    return cls.model_config.get("json_schema_extra", {}).get("is_archetype", False)

def set_not_archetype(cls):
    """Set flags to indicate class is from an archetype and is not an archetype."""
    json_extra = cls.model_config.get("json_schema_extra", {})
    json_extra["is_archetype"] = False
    json_extra["from_archetype"] = True
    cls.model_config["json_schema_extra"] = json_extra
    return cls

def is_from_archetype(cls):
    """Check if a class is from an archetype."""
    return cls.model_config.get("json_schema_extra", {}).get("from_archetype", False)

