"""
Compatibility module for TeamAccountSummaryCustomerListCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.team_account_summary_customer_list_customer_api_response.
"""

try:
    from d361api.d361api.team_account_summary_customer_list_customer_api_response import TeamAccountSummaryCustomerListCustomerApiResponse
    __all__ = ['TeamAccountSummaryCustomerListCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TeamAccountSummaryCustomerListCustomerApiResponse = getattr(d361api, 'TeamAccountSummaryCustomerListCustomerApiResponse', None)
        if TeamAccountSummaryCustomerListCustomerApiResponse is None:
            raise ImportError(f"Could not find TeamAccountSummaryCustomerListCustomerApiResponse in d361api module")
        __all__ = ['TeamAccountSummaryCustomerListCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TeamAccountSummaryCustomerListCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
