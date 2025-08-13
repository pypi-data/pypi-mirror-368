"""
Sparkfly API Client

A simplified wrapper around the generated OpenAPI client.
"""

import asyncio
import time
from typing import Optional, Callable
from .api_client import ApiClient
from .configuration import Configuration
from .api import (
    AuthenticationApi,
    CampaignsApi,
    StoresApi,
    OffersApi,
    OfferStatesApi,
    MembersApi,
    ItemsApi,
    OfferListsApi,
    ImpressionsApi,
    EmailOptInApi,
    TemplatesApi,
    AudiencesApi,
    BIStoreListsApi,
    CtmApi,
    EligibleItemSetsApi,
    MemberPrivacyApi,
    OfferPOSOfferCodesApi,
    POSOfferCodesApi,
    StoreListsApi,
)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        retry_on_exceptions: tuple = (Exception,),
        retry_condition: Optional[Callable[[Exception], bool]] = None,
    ):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Multiplier for delay after each retry
            retry_on_exceptions: Tuple of exceptions to retry on
            retry_condition: Optional function to determine if retry should occur
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retry_on_exceptions = retry_on_exceptions
        self.retry_condition = retry_condition


class Sparkfly:
    """
    A simplified async client for the Sparkfly Platform API.

    This client handles authentication automatically and provides
    easy access to all API endpoints with built-in retry logic.
    """

    def __init__(
        self,
        identity: str,
        key: str,
        environment: str = "staging",
        host: Optional[str] = None,
        token: Optional[str] = None,
        token_expires_at: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize the Sparkfly client.

        Args:
            identity: Your Sparkfly account identity
            key: Your Sparkfly account secret key
            environment: The environment to use ('staging' or 'production')
            host: Optional custom host URL (overrides environment).
                 Must be one of the valid Sparkfly base URLs:
                 - https://api-staging.sparkfly.com (staging)
                 - https://api.sparkfly.com (production)
                 The /v1.0 suffix will be added automatically
            token: Optional pre-existing auth token
            token_expires_at: Optional token expiration timestamp
            retry_config: Optional retry configuration (defaults to 3 retries, 1s delay)
        """
        self.identity = identity
        self.key = key
        self.environment = environment
        self.retry_config = retry_config or RetryConfig()

        # Determine the host URL
        if host:
            # Validate that the host is one of the valid base URLs
            valid_base_hosts = [
                "https://api-staging.sparkfly.com",
                "https://api.sparkfly.com",
            ]
            if host not in valid_base_hosts:
                raise ValueError(
                    f"Invalid host URL. Must be one of: {', '.join(valid_base_hosts)}"
                )

            # Always append /v1.0 to the base URL
            self.host = f"{host}/v1.0"
        elif environment.lower() == "production":
            self.host = "https://api.sparkfly.com/v1.0"
        elif environment.lower() == "staging":
            self.host = "https://api-staging.sparkfly.com/v1.0"
        else:
            raise ValueError("Environment must be 'staging' or 'production'")

        self._token = token
        self._token_expires_at = token_expires_at

        # Initialize the API client
        self._config = Configuration(
            host=self.host,
            api_key={
                "XAuthIdentity": identity,
                "XAuthKey": key,
            },
        )
        self._api_client = ApiClient(configuration=self._config)

        # Initialize API classes with retry wrappers
        self.auth: AuthenticationApi = self._create_retry_wrapper(AuthenticationApi)
        self.campaigns: CampaignsApi = self._create_retry_wrapper(CampaignsApi)
        self.stores: StoresApi = self._create_retry_wrapper(StoresApi)
        self.offers: OffersApi = self._create_retry_wrapper(OffersApi)
        self.offer_states: OfferStatesApi = self._create_retry_wrapper(OfferStatesApi)
        self.members: MembersApi = self._create_retry_wrapper(MembersApi)
        self.items: ItemsApi = self._create_retry_wrapper(ItemsApi)
        self.offer_lists: OfferListsApi = self._create_retry_wrapper(OfferListsApi)
        self.impressions: ImpressionsApi = self._create_retry_wrapper(ImpressionsApi)
        self.email_opt_in: EmailOptInApi = self._create_retry_wrapper(EmailOptInApi)
        self.templates: TemplatesApi = self._create_retry_wrapper(TemplatesApi)
        self.audiences: AudiencesApi = self._create_retry_wrapper(AudiencesApi)
        self.bi_store_lists: BIStoreListsApi = self._create_retry_wrapper(
            BIStoreListsApi
        )
        self.ctm: CtmApi = self._create_retry_wrapper(CtmApi)
        self.eligible_item_sets: EligibleItemSetsApi = self._create_retry_wrapper(
            EligibleItemSetsApi
        )
        self.member_privacy: MemberPrivacyApi = self._create_retry_wrapper(
            MemberPrivacyApi
        )
        self.offer_pos_offer_codes: OfferPOSOfferCodesApi = self._create_retry_wrapper(
            OfferPOSOfferCodesApi
        )
        self.pos_offer_codes: POSOfferCodesApi = self._create_retry_wrapper(
            POSOfferCodesApi
        )
        self.store_lists: StoreListsApi = self._create_retry_wrapper(StoreListsApi)

    def _create_retry_wrapper(self, api_class):
        """Create a wrapper class that automatically applies retry logic to all methods."""

        class RetryWrappedApi(api_class):
            def __init__(self, api_client, sparkfly_client):
                super().__init__(api_client)
                self._sparkfly_client = sparkfly_client

            def __getattribute__(self, name):
                """Override to wrap async methods with retry logic."""
                # Use object.__getattribute__ to avoid recursion
                attr = object.__getattribute__(self, name)

                # Only wrap async methods that are callable and not private
                # Exclude authentication methods to prevent infinite recursion
                if (
                    asyncio.iscoroutinefunction(attr)
                    and callable(attr)
                    and not name.startswith("_")
                    and not name.startswith("post_auth")  # Exclude auth methods
                ):
                    # Create a wrapped version that preserves the method binding
                    async def retry_wrapper(*args, **kwargs):
                        return await self._sparkfly_client._call_with_retry(
                            attr, *args, **kwargs
                        )

                    # Preserve the method name for better debugging and IDE discovery
                    retry_wrapper.__name__ = attr.__name__
                    retry_wrapper.__qualname__ = attr.__qualname__

                    return retry_wrapper

                return attr

        return RetryWrappedApi(self._api_client, self)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the underlying API client."""
        await self._api_client.close()

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        return self._token

    @property
    def token_expires_at(self) -> Optional[float]:
        """Get the token expiration timestamp."""
        return self._token_expires_at

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self._token or not self._token_expires_at:
            return False
        return time.time() < self._token_expires_at

    async def authenticate(self) -> str:
        """
        Authenticate with the Sparkfly API and get a token.

        Returns:
            The authentication token

        Raises:
            Exception: If authentication fails
        """
        try:
            # Request authentication token
            response = await self.auth.post_auth_with_http_info()

            # Extract the token from the response headers
            if hasattr(response, "headers") and "X-Auth-Token" in response.headers:
                self._token = response.headers["X-Auth-Token"]
            else:
                # Fallback: check if the token is in the API client configuration
                self._token = self._config.api_key.get("XAuthToken")

            if not self._token:
                raise Exception("No authentication token received from the API")

            # Set token expiration to 24 hours from now
            self._token_expires_at = time.time() + (24 * 60 * 60)  # 24 hours

            # Update the API client configuration with the token
            self._config.api_key["XAuthToken"] = self._token

            return self._token

        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    async def ensure_authenticated(self) -> str:
        """
        Ensure we have a valid authentication token.

        Returns:
            The authentication token
        """
        if not self.is_token_valid():
            return await self.authenticate()
        return self._token

    async def _call_with_retry(self, api_method, *args, **kwargs):
        """
        Call an API method with automatic authentication and retry logic.

        Args:
            api_method: The async API method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The API response
        """
        # Ensure we're authenticated
        await self.ensure_authenticated()

        # Apply retry logic
        last_exception = None
        delay = self.retry_config.base_delay

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return await api_method(*args, **kwargs)
            except self.retry_config.retry_on_exceptions as e:
                last_exception = e

                # Check if we should retry based on custom condition
                if (
                    self.retry_config.retry_condition
                    and not self.retry_config.retry_condition(e)
                ):
                    raise e

                # If this was the last attempt, raise the exception
                if attempt == self.retry_config.max_retries:
                    break

                # Wait before retrying
                await asyncio.sleep(delay)
                delay = min(
                    delay * self.retry_config.backoff_factor,
                    self.retry_config.max_delay,
                )

        # If we get here, all retries failed
        raise last_exception
