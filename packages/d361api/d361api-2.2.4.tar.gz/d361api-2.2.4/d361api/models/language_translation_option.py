"""
Compatibility module for LanguageTranslationOption.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language_translation_option.
"""

try:
    from d361api.d361api.language_translation_option import LanguageTranslationOption
    __all__ = ['LanguageTranslationOption']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        LanguageTranslationOption = getattr(d361api, 'LanguageTranslationOption', None)
        if LanguageTranslationOption is None:
            raise ImportError(f"Could not find LanguageTranslationOption in d361api module")
        __all__ = ['LanguageTranslationOption']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import LanguageTranslationOption: {e}", ImportWarning)
        __all__ = []
