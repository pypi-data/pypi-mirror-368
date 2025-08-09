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
from bitbadgespy_sdk.models.i_claim_builder_doc_action import IClaimBuilderDocAction
from bitbadgespy_sdk.models.i_claim_cache_policy import IClaimCachePolicy
from bitbadgespy_sdk.models.i_claim_reward import IClaimReward
from bitbadgespy_sdk.models.i_metadata import IMetadata
from bitbadgespy_sdk.models.i_satisfy_method import ISatisfyMethod
from bitbadgespy_sdk.models.integration_plugin_params import IntegrationPluginParams
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IClaimBuilderDoc(BaseModel):
    """
    
    """ # noqa: E501
    doc_id: StrictStr = Field(description="A unique stringified document ID", alias="_docId")
    id: Optional[StrictStr] = Field(default=None, description="A unique document ID (Mongo DB ObjectID)", alias="_id")
    cid: StrictStr = Field(description="The CID (content ID) of the document. This is used behind the scenes to handle off-chain vs on-chain data races.")
    created_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="createdBy")
    doc_claimed: StrictBool = Field(description="True if the document is claimed by the collection", alias="docClaimed")
    collection_id: StrictStr = Field(alias="collectionId")
    managed_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="managedBy")
    tracker_details: Optional[IChallengeTrackerIdDetails] = Field(default=None, description="Which challenge tracker is it tied to", alias="trackerDetails")
    deleted_at: Optional[NumberType] = Field(default=None, description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="deletedAt")
    plugins: List[IntegrationPluginParams] = Field(description="Dynamic checks to run in the form of plugins")
    plugin_ids: Optional[List[StrictStr]] = Field(default=None, description="For query purposes, the plugin IDs", alias="pluginIds")
    manual_distribution: Optional[StrictBool] = Field(default=None, description="If true, the claim codes are to be distributed manually. This doc will only be used for storage purposes. Only in use for legacy on-chain claims.", alias="manualDistribution")
    approach: Optional[StrictStr] = Field(default=None, description="The expected approach for the claim. This is for display purposes for the frontend.  Available options: - in-site: The claim is expected to be completed in-site. - api: The claim is expected to be completed via an API call. - zapier: The claim is expected to be completed via Zapier auto-completion.")
    metadata: Optional[IMetadata] = Field(default=None, description="Metadata for the claim")
    state: Dict[str, Any] = Field(description="The current state of each plugin")
    assign_method: Optional[StrictStr] = Field(default=None, description="Algorithm to determine the claaim number indices", alias="assignMethod")
    satisfy_method: Optional[ISatisfyMethod] = Field(default=None, description="Custom success logic. If not provided, we will default to AND logic with all plugins.", alias="satisfyMethod")
    action: IClaimBuilderDocAction
    rewards: Optional[List[IClaimReward]] = Field(default=None, description="Rewards to be shown upon a successful claim. If you need further gating, you can do this in two-steps.")
    estimated_cost: Optional[StrictStr] = Field(default=None, description="Estimated cost for the user", alias="estimatedCost")
    estimated_time: Optional[StrictStr] = Field(default=None, description="Estimated time to satisfy the claim's requirements", alias="estimatedTime")
    show_in_search_results: Optional[StrictBool] = Field(default=None, description="If true, the claim will be shown in search results", alias="showInSearchResults")
    categories: Optional[List[StrictStr]] = Field(default=None, description="The categories of the claim")
    last_updated: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="lastUpdated")
    created_at: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdAt")
    version: NumberType
    test_only: Optional[StrictBool] = Field(default=None, alias="testOnly")
    cache_policy: Optional[IClaimCachePolicy] = Field(default=None, description="For on-demand claims, we cache the result per user for a short period.  To help optimize performance, please provide a cache policy.  This is only applicable to on-demand claims.", alias="cachePolicy")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_docId", "_id", "cid", "createdBy", "docClaimed", "collectionId", "managedBy", "trackerDetails", "deletedAt", "plugins", "pluginIds", "manualDistribution", "approach", "metadata", "state", "assignMethod", "satisfyMethod", "action", "rewards", "estimatedCost", "estimatedTime", "showInSearchResults", "categories", "lastUpdated", "createdAt", "version", "testOnly", "cachePolicy"]

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
        """Create an instance of IClaimBuilderDoc from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of deleted_at
        if self.deleted_at:
            _dict['deletedAt'] = self.deleted_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in plugins (list)
        _items = []
        if self.plugins:
            for _item_plugins in self.plugins:
                if _item_plugins:
                    _items.append(_item_plugins.to_dict())
            _dict['plugins'] = _items
        # override the default output from pydantic by calling `to_dict()` of metadata
        if self.metadata:
            _dict['metadata'] = self.metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of satisfy_method
        if self.satisfy_method:
            _dict['satisfyMethod'] = self.satisfy_method.to_dict()
        # override the default output from pydantic by calling `to_dict()` of action
        if self.action:
            _dict['action'] = self.action.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in rewards (list)
        _items = []
        if self.rewards:
            for _item_rewards in self.rewards:
                if _item_rewards:
                    _items.append(_item_rewards.to_dict())
            _dict['rewards'] = _items
        # override the default output from pydantic by calling `to_dict()` of last_updated
        if self.last_updated:
            _dict['lastUpdated'] = self.last_updated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of cache_policy
        if self.cache_policy:
            _dict['cachePolicy'] = self.cache_policy.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IClaimBuilderDoc from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_docId": obj.get("_docId"),
            "_id": obj.get("_id"),
            "cid": obj.get("cid"),
            "createdBy": obj.get("createdBy"),
            "docClaimed": obj.get("docClaimed"),
            "collectionId": obj.get("collectionId"),
            "managedBy": obj.get("managedBy"),
            "trackerDetails": IChallengeTrackerIdDetails.from_dict(obj["trackerDetails"]) if obj.get("trackerDetails") is not None else None,
            "deletedAt": NumberType.from_dict(obj["deletedAt"]) if obj.get("deletedAt") is not None else None,
            "plugins": [IntegrationPluginParams.from_dict(_item) for _item in obj["plugins"]] if obj.get("plugins") is not None else None,
            "pluginIds": obj.get("pluginIds"),
            "manualDistribution": obj.get("manualDistribution"),
            "approach": obj.get("approach"),
            "metadata": IMetadata.from_dict(obj["metadata"]) if obj.get("metadata") is not None else None,
            "state": obj.get("state"),
            "assignMethod": obj.get("assignMethod"),
            "satisfyMethod": ISatisfyMethod.from_dict(obj["satisfyMethod"]) if obj.get("satisfyMethod") is not None else None,
            "action": IClaimBuilderDocAction.from_dict(obj["action"]) if obj.get("action") is not None else None,
            "rewards": [IClaimReward.from_dict(_item) for _item in obj["rewards"]] if obj.get("rewards") is not None else None,
            "estimatedCost": obj.get("estimatedCost"),
            "estimatedTime": obj.get("estimatedTime"),
            "showInSearchResults": obj.get("showInSearchResults"),
            "categories": obj.get("categories"),
            "lastUpdated": NumberType.from_dict(obj["lastUpdated"]) if obj.get("lastUpdated") is not None else None,
            "createdAt": NumberType.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "version": NumberType.from_dict(obj["version"]) if obj.get("version") is not None else None,
            "testOnly": obj.get("testOnly"),
            "cachePolicy": IClaimCachePolicy.from_dict(obj["cachePolicy"]) if obj.get("cachePolicy") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


