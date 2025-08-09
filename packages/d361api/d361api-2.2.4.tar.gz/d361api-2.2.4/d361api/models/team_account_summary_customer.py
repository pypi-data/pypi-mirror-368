"""
Compatibility module for TeamAccountSummaryCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.team_account_summary_customer.
"""

try:
    from d361api.d361api.team_account_summary_customer import TeamAccountSummaryCustomer
    __all__ = ['TeamAccountSummaryCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TeamAccountSummaryCustomer = getattr(d361api, 'TeamAccountSummaryCustomer', None)
        if TeamAccountSummaryCustomer is None:
            raise ImportError(f"Could not find TeamAccountSummaryCustomer in d361api module")
        __all__ = ['TeamAccountSummaryCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TeamAccountSummaryCustomer: {e}", ImportWarning)
        __all__ = []
