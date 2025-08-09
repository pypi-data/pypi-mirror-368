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
from typing import Any, ClassVar, Dict, List, Optional
from bitbadgespy_sdk.models.i_approval_amounts import IApprovalAmounts
from bitbadgespy_sdk.models.i_auto_deletion_options import IAutoDeletionOptions
from bitbadgespy_sdk.models.i_coin_transfer import ICoinTransfer
from bitbadgespy_sdk.models.i_dynamic_store_challenge import IDynamicStoreChallenge
from bitbadgespy_sdk.models.i_max_num_transfers import IMaxNumTransfers
from bitbadgespy_sdk.models.i_merkle_challenge import IMerkleChallenge
from bitbadgespy_sdk.models.i_must_own_badge import IMustOwnBadge
from bitbadgespy_sdk.models.i_predetermined_balances import IPredeterminedBalances
from bitbadgespy_sdk.models.ieth_signature_challenge import IETHSignatureChallenge
from typing import Optional, Set
from typing_extensions import Self

class IOutgoingApprovalCriteria(BaseModel):
    """
    IOutgoingApprovalCriteria
    """ # noqa: E501
    coin_transfers: Optional[List[ICoinTransfer]] = Field(default=None, description="The BADGE or sdk.coin transfers to be executed upon every approval.", alias="coinTransfers")
    must_own_badges: Optional[List[IMustOwnBadge]] = Field(default=None, description="The list of must own badges that need valid proofs to be approved.", alias="mustOwnBadges")
    merkle_challenges: Optional[List[IMerkleChallenge]] = Field(default=None, description="The list of merkle challenges that need valid proofs to be approved.", alias="merkleChallenges")
    predetermined_balances: Optional[IPredeterminedBalances] = Field(default=None, description="The predetermined balances for each transfer. These allow approvals to use predetermined balance amounts rather than an incrementing tally system.", alias="predeterminedBalances")
    approval_amounts: Optional[IApprovalAmounts] = Field(default=None, description="The maximum approved amounts for this approval.", alias="approvalAmounts")
    max_num_transfers: Optional[IMaxNumTransfers] = Field(default=None, description="The max num transfers for this approval.", alias="maxNumTransfers")
    require_to_equals_initiated_by: Optional[StrictBool] = Field(default=None, description="Whether the to address must equal the initiatedBy address.", alias="requireToEqualsInitiatedBy")
    require_to_does_not_equal_initiated_by: Optional[StrictBool] = Field(default=None, description="Whether the to address must not equal the initiatedBy  address.", alias="requireToDoesNotEqualInitiatedBy")
    auto_deletion_options: Optional[IAutoDeletionOptions] = Field(default=None, description="Whether the approval should be deleted after one use.", alias="autoDeletionOptions")
    dynamic_store_challenges: Optional[List[IDynamicStoreChallenge]] = Field(default=None, description="The list of dynamic store challenges that the initiator must pass for approval.", alias="dynamicStoreChallenges")
    eth_signature_challenges: Optional[List[IETHSignatureChallenge]] = Field(default=None, description="The list of ETH signature challenges that the initiator must pass for approval.", alias="ethSignatureChallenges")
    __properties: ClassVar[List[str]] = ["coinTransfers", "mustOwnBadges", "merkleChallenges", "predeterminedBalances", "approvalAmounts", "maxNumTransfers", "requireToEqualsInitiatedBy", "requireToDoesNotEqualInitiatedBy", "autoDeletionOptions", "dynamicStoreChallenges", "ethSignatureChallenges"]

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
        """Create an instance of IOutgoingApprovalCriteria from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in coin_transfers (list)
        _items = []
        if self.coin_transfers:
            for _item_coin_transfers in self.coin_transfers:
                if _item_coin_transfers:
                    _items.append(_item_coin_transfers.to_dict())
            _dict['coinTransfers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in must_own_badges (list)
        _items = []
        if self.must_own_badges:
            for _item_must_own_badges in self.must_own_badges:
                if _item_must_own_badges:
                    _items.append(_item_must_own_badges.to_dict())
            _dict['mustOwnBadges'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in merkle_challenges (list)
        _items = []
        if self.merkle_challenges:
            for _item_merkle_challenges in self.merkle_challenges:
                if _item_merkle_challenges:
                    _items.append(_item_merkle_challenges.to_dict())
            _dict['merkleChallenges'] = _items
        # override the default output from pydantic by calling `to_dict()` of predetermined_balances
        if self.predetermined_balances:
            _dict['predeterminedBalances'] = self.predetermined_balances.to_dict()
        # override the default output from pydantic by calling `to_dict()` of approval_amounts
        if self.approval_amounts:
            _dict['approvalAmounts'] = self.approval_amounts.to_dict()
        # override the default output from pydantic by calling `to_dict()` of max_num_transfers
        if self.max_num_transfers:
            _dict['maxNumTransfers'] = self.max_num_transfers.to_dict()
        # override the default output from pydantic by calling `to_dict()` of auto_deletion_options
        if self.auto_deletion_options:
            _dict['autoDeletionOptions'] = self.auto_deletion_options.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in dynamic_store_challenges (list)
        _items = []
        if self.dynamic_store_challenges:
            for _item_dynamic_store_challenges in self.dynamic_store_challenges:
                if _item_dynamic_store_challenges:
                    _items.append(_item_dynamic_store_challenges.to_dict())
            _dict['dynamicStoreChallenges'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in eth_signature_challenges (list)
        _items = []
        if self.eth_signature_challenges:
            for _item_eth_signature_challenges in self.eth_signature_challenges:
                if _item_eth_signature_challenges:
                    _items.append(_item_eth_signature_challenges.to_dict())
            _dict['ethSignatureChallenges'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IOutgoingApprovalCriteria from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "coinTransfers": [ICoinTransfer.from_dict(_item) for _item in obj["coinTransfers"]] if obj.get("coinTransfers") is not None else None,
            "mustOwnBadges": [IMustOwnBadge.from_dict(_item) for _item in obj["mustOwnBadges"]] if obj.get("mustOwnBadges") is not None else None,
            "merkleChallenges": [IMerkleChallenge.from_dict(_item) for _item in obj["merkleChallenges"]] if obj.get("merkleChallenges") is not None else None,
            "predeterminedBalances": IPredeterminedBalances.from_dict(obj["predeterminedBalances"]) if obj.get("predeterminedBalances") is not None else None,
            "approvalAmounts": IApprovalAmounts.from_dict(obj["approvalAmounts"]) if obj.get("approvalAmounts") is not None else None,
            "maxNumTransfers": IMaxNumTransfers.from_dict(obj["maxNumTransfers"]) if obj.get("maxNumTransfers") is not None else None,
            "requireToEqualsInitiatedBy": obj.get("requireToEqualsInitiatedBy"),
            "requireToDoesNotEqualInitiatedBy": obj.get("requireToDoesNotEqualInitiatedBy"),
            "autoDeletionOptions": IAutoDeletionOptions.from_dict(obj["autoDeletionOptions"]) if obj.get("autoDeletionOptions") is not None else None,
            "dynamicStoreChallenges": [IDynamicStoreChallenge.from_dict(_item) for _item in obj["dynamicStoreChallenges"]] if obj.get("dynamicStoreChallenges") is not None else None,
            "ethSignatureChallenges": [IETHSignatureChallenge.from_dict(_item) for _item in obj["ethSignatureChallenges"]] if obj.get("ethSignatureChallenges") is not None else None
        })
        return _obj


