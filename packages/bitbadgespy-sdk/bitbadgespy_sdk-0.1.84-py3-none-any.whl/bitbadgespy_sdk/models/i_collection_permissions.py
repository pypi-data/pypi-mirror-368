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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List
from bitbadgespy_sdk.models.i_action_permission import IActionPermission
from bitbadgespy_sdk.models.i_badge_ids_action_permission import IBadgeIdsActionPermission
from bitbadgespy_sdk.models.i_collection_approval_permission import ICollectionApprovalPermission
from bitbadgespy_sdk.models.i_timed_update_permission import ITimedUpdatePermission
from bitbadgespy_sdk.models.i_timed_update_with_badge_ids_permission import ITimedUpdateWithBadgeIdsPermission
from typing import Optional, Set
from typing_extensions import Self

class ICollectionPermissions(BaseModel):
    """
    ICollectionPermissions
    """ # noqa: E501
    can_delete_collection: List[IActionPermission] = Field(description="The permissions for deleting the collection.", alias="canDeleteCollection")
    can_archive_collection: List[ITimedUpdatePermission] = Field(description="The permissions for archiving the collection.", alias="canArchiveCollection")
    can_update_off_chain_balances_metadata: List[ITimedUpdatePermission] = Field(description="The permissions for updating the off-chain balances metadata.", alias="canUpdateOffChainBalancesMetadata")
    can_update_standards: List[ITimedUpdatePermission] = Field(description="The permissions for updating the standards.", alias="canUpdateStandards")
    can_update_custom_data: List[ITimedUpdatePermission] = Field(description="The permissions for updating the custom data.", alias="canUpdateCustomData")
    can_update_manager: List[ITimedUpdatePermission] = Field(description="The permissions for updating the manager.", alias="canUpdateManager")
    can_update_collection_metadata: List[ITimedUpdatePermission] = Field(description="The permissions for updating the collection metadata.", alias="canUpdateCollectionMetadata")
    can_update_valid_badge_ids: List[IBadgeIdsActionPermission] = Field(description="The permissions for creating more badges.", alias="canUpdateValidBadgeIds")
    can_update_badge_metadata: List[ITimedUpdateWithBadgeIdsPermission] = Field(description="The permissions for updating the badge metadata.", alias="canUpdateBadgeMetadata")
    can_update_collection_approvals: List[ICollectionApprovalPermission] = Field(description="The permissions for updating the collection approved transfers.", alias="canUpdateCollectionApprovals")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["canDeleteCollection", "canArchiveCollection", "canUpdateOffChainBalancesMetadata", "canUpdateStandards", "canUpdateCustomData", "canUpdateManager", "canUpdateCollectionMetadata", "canUpdateValidBadgeIds", "canUpdateBadgeMetadata", "canUpdateCollectionApprovals"]

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
        """Create an instance of ICollectionPermissions from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in can_delete_collection (list)
        _items = []
        if self.can_delete_collection:
            for _item_can_delete_collection in self.can_delete_collection:
                if _item_can_delete_collection:
                    _items.append(_item_can_delete_collection.to_dict())
            _dict['canDeleteCollection'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_archive_collection (list)
        _items = []
        if self.can_archive_collection:
            for _item_can_archive_collection in self.can_archive_collection:
                if _item_can_archive_collection:
                    _items.append(_item_can_archive_collection.to_dict())
            _dict['canArchiveCollection'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_off_chain_balances_metadata (list)
        _items = []
        if self.can_update_off_chain_balances_metadata:
            for _item_can_update_off_chain_balances_metadata in self.can_update_off_chain_balances_metadata:
                if _item_can_update_off_chain_balances_metadata:
                    _items.append(_item_can_update_off_chain_balances_metadata.to_dict())
            _dict['canUpdateOffChainBalancesMetadata'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_standards (list)
        _items = []
        if self.can_update_standards:
            for _item_can_update_standards in self.can_update_standards:
                if _item_can_update_standards:
                    _items.append(_item_can_update_standards.to_dict())
            _dict['canUpdateStandards'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_custom_data (list)
        _items = []
        if self.can_update_custom_data:
            for _item_can_update_custom_data in self.can_update_custom_data:
                if _item_can_update_custom_data:
                    _items.append(_item_can_update_custom_data.to_dict())
            _dict['canUpdateCustomData'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_manager (list)
        _items = []
        if self.can_update_manager:
            for _item_can_update_manager in self.can_update_manager:
                if _item_can_update_manager:
                    _items.append(_item_can_update_manager.to_dict())
            _dict['canUpdateManager'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_collection_metadata (list)
        _items = []
        if self.can_update_collection_metadata:
            for _item_can_update_collection_metadata in self.can_update_collection_metadata:
                if _item_can_update_collection_metadata:
                    _items.append(_item_can_update_collection_metadata.to_dict())
            _dict['canUpdateCollectionMetadata'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_valid_badge_ids (list)
        _items = []
        if self.can_update_valid_badge_ids:
            for _item_can_update_valid_badge_ids in self.can_update_valid_badge_ids:
                if _item_can_update_valid_badge_ids:
                    _items.append(_item_can_update_valid_badge_ids.to_dict())
            _dict['canUpdateValidBadgeIds'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_badge_metadata (list)
        _items = []
        if self.can_update_badge_metadata:
            for _item_can_update_badge_metadata in self.can_update_badge_metadata:
                if _item_can_update_badge_metadata:
                    _items.append(_item_can_update_badge_metadata.to_dict())
            _dict['canUpdateBadgeMetadata'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in can_update_collection_approvals (list)
        _items = []
        if self.can_update_collection_approvals:
            for _item_can_update_collection_approvals in self.can_update_collection_approvals:
                if _item_can_update_collection_approvals:
                    _items.append(_item_can_update_collection_approvals.to_dict())
            _dict['canUpdateCollectionApprovals'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ICollectionPermissions from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "canDeleteCollection": [IActionPermission.from_dict(_item) for _item in obj["canDeleteCollection"]] if obj.get("canDeleteCollection") is not None else None,
            "canArchiveCollection": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canArchiveCollection"]] if obj.get("canArchiveCollection") is not None else None,
            "canUpdateOffChainBalancesMetadata": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canUpdateOffChainBalancesMetadata"]] if obj.get("canUpdateOffChainBalancesMetadata") is not None else None,
            "canUpdateStandards": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canUpdateStandards"]] if obj.get("canUpdateStandards") is not None else None,
            "canUpdateCustomData": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canUpdateCustomData"]] if obj.get("canUpdateCustomData") is not None else None,
            "canUpdateManager": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canUpdateManager"]] if obj.get("canUpdateManager") is not None else None,
            "canUpdateCollectionMetadata": [ITimedUpdatePermission.from_dict(_item) for _item in obj["canUpdateCollectionMetadata"]] if obj.get("canUpdateCollectionMetadata") is not None else None,
            "canUpdateValidBadgeIds": [IBadgeIdsActionPermission.from_dict(_item) for _item in obj["canUpdateValidBadgeIds"]] if obj.get("canUpdateValidBadgeIds") is not None else None,
            "canUpdateBadgeMetadata": [ITimedUpdateWithBadgeIdsPermission.from_dict(_item) for _item in obj["canUpdateBadgeMetadata"]] if obj.get("canUpdateBadgeMetadata") is not None else None,
            "canUpdateCollectionApprovals": [ICollectionApprovalPermission.from_dict(_item) for _item in obj["canUpdateCollectionApprovals"]] if obj.get("canUpdateCollectionApprovals") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


