"""
Compatibility module for SectionTypeEnum.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.section_type_enum.
"""

try:
    from d361api.d361api.section_type_enum import SectionTypeEnum
    __all__ = ['SectionTypeEnum']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        SectionTypeEnum = getattr(d361api, 'SectionTypeEnum', None)
        if SectionTypeEnum is None:
            raise ImportError(f"Could not find SectionTypeEnum in d361api module")
        __all__ = ['SectionTypeEnum']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import SectionTypeEnum: {e}", ImportWarning)
        __all__ = []
