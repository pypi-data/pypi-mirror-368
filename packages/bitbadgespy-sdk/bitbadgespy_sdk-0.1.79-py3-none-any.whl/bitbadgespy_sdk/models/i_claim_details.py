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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from bitbadgespy_sdk.models.i_challenge_tracker_id_details import IChallengeTrackerIdDetails
from bitbadgespy_sdk.models.i_claim_cache_policy import IClaimCachePolicy
from bitbadgespy_sdk.models.i_claim_details_template_info import IClaimDetailsTemplateInfo
from bitbadgespy_sdk.models.i_claim_reward import IClaimReward
from bitbadgespy_sdk.models.i_metadata import IMetadata
from bitbadgespy_sdk.models.i_predetermined_balances import IPredeterminedBalances
from bitbadgespy_sdk.models.i_satisfy_method import ISatisfyMethod
from bitbadgespy_sdk.models.integration_plugin_details import IntegrationPluginDetails
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IClaimDetails(BaseModel):
    """
    IClaimDetails
    """ # noqa: E501
    includes_private_params: StrictBool = Field(description="Whether the claim fetch includes private params", alias="_includesPrivateParams")
    claim_id: StrictStr = Field(description="Unique claim ID.", alias="claimId")
    created_by: Optional[StrictStr] = Field(default=None, description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="createdBy")
    managed_by: Optional[StrictStr] = Field(default=None, description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="managedBy")
    collection_id: Optional[StrictStr] = Field(default=None, alias="collectionId")
    standalone_claim: Optional[StrictBool] = Field(default=None, description="Standalone claims are not linked with a badge or list.", alias="standaloneClaim")
    list_id: Optional[StrictStr] = Field(default=None, description="Address list ID that the claim is for (if applicable - list claims).", alias="listId")
    tracker_details: Optional[IChallengeTrackerIdDetails] = Field(default=None, description="The tracker details for the claim (if applicable - collection claims).", alias="trackerDetails")
    balances_to_set: Optional[IPredeterminedBalances] = Field(default=None, description="The balances to set for the claim.  Only used for claims for collections that have off-chain indexed balances and are assigning balances based on the claim.", alias="balancesToSet")
    plugins: List[IntegrationPluginDetails] = Field(description="Claim plugins. These are the criteria that must pass for a user to claim.")
    rewards: Optional[List[IClaimReward]] = Field(default=None, description="Rewards for the claim.")
    estimated_cost: Optional[StrictStr] = Field(default=None, description="Estimated cost for the claim.", alias="estimatedCost")
    show_in_search_results: Optional[StrictBool] = Field(default=None, description="If true, the claim will be shown in search results", alias="showInSearchResults")
    categories: Optional[List[StrictStr]] = Field(default=None, description="The categories of the claim")
    estimated_time: Optional[StrictStr] = Field(default=None, description="Estimated time to satisfy the claim's requirements.", alias="estimatedTime")
    manual_distribution: Optional[StrictBool] = Field(default=None, description="If manual distribution is enabled, we do not handle any distribution of claim codes. We leave that up to the claim creator.  Only applicable for on-chain badge claims. This is only used in advanced self-hosted cases.", alias="manualDistribution")
    approach: Optional[StrictStr] = Field(default=None, description="How the claim is expected to be completed. This is for display purposes for the frontend.  Available options: - in-site (default): The claim is expected to be completed in-site. - api: The claim is expected to be completed via an API call. - zapier: The claim is expected to be completed via Zapier auto-completion.  Typically, you will use the in-site approach")
    seed_code: Optional[StrictStr] = Field(default=None, description="Seed code for the claim. Only used for on-chain badge claims.  This is how we produce all reserved codes for the on-chain merkle challenge / proofs.", alias="seedCode")
    metadata: Optional[IMetadata] = Field(default=None, description="Metadata for the claim.")
    assign_method: Optional[StrictStr] = Field(default=None, description="Algorithm to determine the claim number order. Blank is just incrementing claim numbers.  For most cases, you will not need to specify this.", alias="assignMethod")
    last_updated: Optional[NumberType] = Field(default=None, description="Last updated timestamp for the claim.", alias="lastUpdated")
    version: NumberType = Field(description="The version of the claim.")
    satisfy_method: Optional[ISatisfyMethod] = Field(default=None, description="Custom satisfaction logic.  If left blank, all plugins must pass for the claim to be satisfied. Otherwise, you can specify a custom method to determine if the claim is satisfied.", alias="satisfyMethod")
    cache_policy: Optional[IClaimCachePolicy] = Field(default=None, description="Cache policy for the claim. Only needed for on-demand claims.", alias="cachePolicy")
    template_info: Optional[IClaimDetailsTemplateInfo] = Field(default=None, alias="_templateInfo")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_includesPrivateParams", "claimId", "createdBy", "managedBy", "collectionId", "standaloneClaim", "listId", "trackerDetails", "balancesToSet", "plugins", "rewards", "estimatedCost", "showInSearchResults", "categories", "estimatedTime", "manualDistribution", "approach", "seedCode", "metadata", "assignMethod", "lastUpdated", "version", "satisfyMethod", "cachePolicy", "_templateInfo"]

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
        """Create an instance of IClaimDetails from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * Fields in `self.additional_properties` are added to the output dict.
        """
        excluded_fields: Set[str] = set([
            "additional_properties",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of tracker_details
        if self.tracker_details:
            _dict['trackerDetails'] = self.tracker_details.to_dict()
        # override the default output from pydantic by calling `to_dict()` of balances_to_set
        if self.balances_to_set:
            _dict['balancesToSet'] = self.balances_to_set.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in plugins (list)
        _items = []
        if self.plugins:
            for _item_plugins in self.plugins:
                if _item_plugins:
                    _items.append(_item_plugins.to_dict())
            _dict['plugins'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in rewards (list)
        _items = []
        if self.rewards:
            for _item_rewards in self.rewards:
                if _item_rewards:
                    _items.append(_item_rewards.to_dict())
            _dict['rewards'] = _items
        # override the default output from pydantic by calling `to_dict()` of metadata
        if self.metadata:
            _dict['metadata'] = self.metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of last_updated
        if self.last_updated:
            _dict['lastUpdated'] = self.last_updated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of satisfy_method
        if self.satisfy_method:
            _dict['satisfyMethod'] = self.satisfy_method.to_dict()
        # override the default output from pydantic by calling `to_dict()` of cache_policy
        if self.cache_policy:
            _dict['cachePolicy'] = self.cache_policy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of template_info
        if self.template_info:
            _dict['_templateInfo'] = self.template_info.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IClaimDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_includesPrivateParams": obj.get("_includesPrivateParams"),
            "claimId": obj.get("claimId"),
            "createdBy": obj.get("createdBy"),
            "managedBy": obj.get("managedBy"),
            "collectionId": obj.get("collectionId"),
            "standaloneClaim": obj.get("standaloneClaim"),
            "listId": obj.get("listId"),
            "trackerDetails": IChallengeTrackerIdDetails.from_dict(obj["trackerDetails"]) if obj.get("trackerDetails") is not None else None,
            "balancesToSet": IPredeterminedBalances.from_dict(obj["balancesToSet"]) if obj.get("balancesToSet") is not None else None,
            "plugins": [IntegrationPluginDetails.from_dict(_item) for _item in obj["plugins"]] if obj.get("plugins") is not None else None,
            "rewards": [IClaimReward.from_dict(_item) for _item in obj["rewards"]] if obj.get("rewards") is not None else None,
            "estimatedCost": obj.get("estimatedCost"),
            "showInSearchResults": obj.get("showInSearchResults"),
            "categories": obj.get("categories"),
            "estimatedTime": obj.get("estimatedTime"),
            "manualDistribution": obj.get("manualDistribution"),
            "approach": obj.get("approach"),
            "seedCode": obj.get("seedCode"),
            "metadata": IMetadata.from_dict(obj["metadata"]) if obj.get("metadata") is not None else None,
            "assignMethod": obj.get("assignMethod"),
            "lastUpdated": NumberType.from_dict(obj["lastUpdated"]) if obj.get("lastUpdated") is not None else None,
            "version": NumberType.from_dict(obj["version"]) if obj.get("version") is not None else None,
            "satisfyMethod": ISatisfyMethod.from_dict(obj["satisfyMethod"]) if obj.get("satisfyMethod") is not None else None,
            "cachePolicy": IClaimCachePolicy.from_dict(obj["cachePolicy"]) if obj.get("cachePolicy") is not None else None,
            "_templateInfo": IClaimDetailsTemplateInfo.from_dict(obj["_templateInfo"]) if obj.get("_templateInfo") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


