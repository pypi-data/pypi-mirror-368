"""DNS record management API."""

from __future__ import annotations

from namecheap_sdk.models import UserBalance

from .base import BaseAPI


class UserAPI(BaseAPI):
    """User management API."""

    def get_balance(self) -> UserBalance | None:
        """Get user balance."""
        result = self._request("namecheap.users.getBalances", model=UserBalance, path="UserGetBalancesResult")
        if isinstance(result, list):
            return result[0]
        return None
