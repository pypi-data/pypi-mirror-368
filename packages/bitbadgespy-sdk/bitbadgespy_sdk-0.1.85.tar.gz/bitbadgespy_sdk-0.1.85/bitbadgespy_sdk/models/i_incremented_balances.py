# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Pages** (`manageUtilityPages`)   Create, update, and delete utility pages on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List
from bitbadgespy_sdk.models.i_balance import IBalance
from bitbadgespy_sdk.models.i_recurring_ownership_times import IRecurringOwnershipTimes
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IIncrementedBalances(BaseModel):
    """
    IIncrementedBalances
    """ # noqa: E501
    start_balances: List[IBalance] = Field(description="The starting balances for each transfer. Order number corresponds to the number of times we increment.", alias="startBalances")
    increment_badge_ids_by: NumberType = Field(description="The amount to increment the badge IDs by after each transfer.", alias="incrementBadgeIdsBy")
    increment_ownership_times_by: NumberType = Field(description="The amount to increment the owned times by after each transfer. Incompatible with durationFromTimestamp.", alias="incrementOwnershipTimesBy")
    duration_from_timestamp: NumberType = Field(description="The number of unix milliseconds to approve starting from now. Incompatible with incrementOwnershipTimesBy.", alias="durationFromTimestamp")
    allow_override_timestamp: StrictBool = Field(description="Whether to allow the override timestamp to be used.", alias="allowOverrideTimestamp")
    recurring_ownership_times: IRecurringOwnershipTimes = Field(description="The recurring ownership times for the approval.", alias="recurringOwnershipTimes")
    allow_override_with_any_valid_badge: StrictBool = Field(description="Whether to allow the override with any valid badge.", alias="allowOverrideWithAnyValidBadge")
    __properties: ClassVar[List[str]] = ["startBalances", "incrementBadgeIdsBy", "incrementOwnershipTimesBy", "durationFromTimestamp", "allowOverrideTimestamp", "recurringOwnershipTimes", "allowOverrideWithAnyValidBadge"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of IIncrementedBalances from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in start_balances (list)
        _items = []
        if self.start_balances:
            for _item_start_balances in self.start_balances:
                if _item_start_balances:
                    _items.append(_item_start_balances.to_dict())
            _dict['startBalances'] = _items
        # override the default output from pydantic by calling `to_dict()` of increment_badge_ids_by
        if self.increment_badge_ids_by:
            _dict['incrementBadgeIdsBy'] = self.increment_badge_ids_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of increment_ownership_times_by
        if self.increment_ownership_times_by:
            _dict['incrementOwnershipTimesBy'] = self.increment_ownership_times_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of duration_from_timestamp
        if self.duration_from_timestamp:
            _dict['durationFromTimestamp'] = self.duration_from_timestamp.to_dict()
        # override the default output from pydantic by calling `to_dict()` of recurring_ownership_times
        if self.recurring_ownership_times:
            _dict['recurringOwnershipTimes'] = self.recurring_ownership_times.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IIncrementedBalances from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "startBalances": [IBalance.from_dict(_item) for _item in obj["startBalances"]] if obj.get("startBalances") is not None else None,
            "incrementBadgeIdsBy": NumberType.from_dict(obj["incrementBadgeIdsBy"]) if obj.get("incrementBadgeIdsBy") is not None else None,
            "incrementOwnershipTimesBy": NumberType.from_dict(obj["incrementOwnershipTimesBy"]) if obj.get("incrementOwnershipTimesBy") is not None else None,
            "durationFromTimestamp": NumberType.from_dict(obj["durationFromTimestamp"]) if obj.get("durationFromTimestamp") is not None else None,
            "allowOverrideTimestamp": obj.get("allowOverrideTimestamp"),
            "recurringOwnershipTimes": IRecurringOwnershipTimes.from_dict(obj["recurringOwnershipTimes"]) if obj.get("recurringOwnershipTimes") is not None else None,
            "allowOverrideWithAnyValidBadge": obj.get("allowOverrideWithAnyValidBadge")
        })
        return _obj


