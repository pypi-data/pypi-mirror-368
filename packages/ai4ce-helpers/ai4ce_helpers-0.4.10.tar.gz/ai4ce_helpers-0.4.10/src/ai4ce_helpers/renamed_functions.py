from .functions import get_mission_orbit, export_components
from deprecated import deprecated
import warnings

@deprecated(reason="This function is deprecated. Please use get_mission_orbit() instead.", category=DeprecationWarning)
def get_mission_info(project_id: int) -> dict:
    """Deprecation warning: This function is deprecated. Please use get_mission_orbit() instead."""
    warnings.warn("This function is deprecated. Please use get_mission_orbit() instead.", DeprecationWarning, stacklevel=2)
    return get_mission_orbit(project_id)

@deprecated(reason="This function is deprecated. Please use export_components() instead.", category=DeprecationWarning)
def get_all_decisions():
    """Deprecation warning: This function is deprecated. Please use export_components() instead."""
    warnings.warn("This function is deprecated. Please use export_components() instead.", DeprecationWarning, stacklevel=2)
    return export_components()