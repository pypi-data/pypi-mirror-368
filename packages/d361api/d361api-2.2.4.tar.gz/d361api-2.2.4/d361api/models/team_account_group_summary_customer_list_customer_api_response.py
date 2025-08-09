"""
Compatibility module for TeamAccountGroupSummaryCustomerListCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.team_account_group_summary_customer_list_customer_api_response.
"""

try:
    from d361api.d361api.team_account_group_summary_customer_list_customer_api_response import TeamAccountGroupSummaryCustomerListCustomerApiResponse
    __all__ = ['TeamAccountGroupSummaryCustomerListCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TeamAccountGroupSummaryCustomerListCustomerApiResponse = getattr(d361api, 'TeamAccountGroupSummaryCustomerListCustomerApiResponse', None)
        if TeamAccountGroupSummaryCustomerListCustomerApiResponse is None:
            raise ImportError(f"Could not find TeamAccountGroupSummaryCustomerListCustomerApiResponse in d361api module")
        __all__ = ['TeamAccountGroupSummaryCustomerListCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TeamAccountGroupSummaryCustomerListCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
