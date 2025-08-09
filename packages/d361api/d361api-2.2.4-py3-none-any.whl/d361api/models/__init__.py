"""
Models compatibility layer for d361api package.

This module provides compatibility imports for all models that are already imported
in the main d361api package. This resolves import issues where individual model files
expect models to be available from 'd361api.models.*'.

The approach is to dynamically re-export all models that are already properly imported
in the main d361api.__init__.py file.
"""

# Import the main d361api module to get all the properly imported models
try:
    import d361api
    import inspect
    
    # Get all classes from the main d361api module
    for name in dir(d361api):
        obj = getattr(d361api, name)
        # Export classes that are models (not APIs, exceptions, or other utility classes)
        if (inspect.isclass(obj) and 
            not name.startswith('_') and
            not name.endswith('Api') and  # Exclude API classes
            name not in ['ApiClient', 'Configuration', 'ApiResponse'] and  # Exclude client classes
            not name.startswith('OpenApi') and not name.startswith('Api') and  # Exclude exception classes
            hasattr(obj, '__module__') and 
            'd361api.d361api.' in obj.__module__):  # Only include model classes
            globals()[name] = obj

except ImportError as e:
    # If we can't import the main d361api module, fall back to direct imports
    import warnings
    warnings.warn(f"Failed to import models from main d361api module: {e}", ImportWarning)
    
    # Fallback: try to import some common models directly
    try:
        from d361api.d361api.api_documentation_import_response_customer import ApiDocumentationImportResponseCustomer
        from d361api.d361api.create_article_request import CreateArticleRequest
        from d361api.d361api.create_article_response import CreateArticleResponse
        from d361api.d361api.get_articles_response_customer import GetArticlesResponseCustomer
        from d361api.d361api.base_response import BaseResponse
        from d361api.d361api.base_error import BaseError
        from d361api.d361api.base_information import BaseInformation
        from d361api.d361api.base_warning import BaseWarning
    except ImportError:
        warnings.warn("Failed to import even basic models directly", ImportWarning)