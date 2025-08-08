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

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from bitbadgespy_sdk.models.i_badge_metadata_timeline import IBadgeMetadataTimeline
from bitbadgespy_sdk.models.i_collection_approval import ICollectionApproval
from bitbadgespy_sdk.models.i_collection_invariants import ICollectionInvariants
from bitbadgespy_sdk.models.i_collection_metadata_timeline import ICollectionMetadataTimeline
from bitbadgespy_sdk.models.i_collection_permissions import ICollectionPermissions
from bitbadgespy_sdk.models.i_cosmos_coin_wrapper_path import ICosmosCoinWrapperPath
from bitbadgespy_sdk.models.i_custom_data_timeline import ICustomDataTimeline
from bitbadgespy_sdk.models.i_manager_timeline import IManagerTimeline
from bitbadgespy_sdk.models.i_off_chain_balances_metadata_timeline import IOffChainBalancesMetadataTimeline
from bitbadgespy_sdk.models.i_standards_timeline import IStandardsTimeline
from bitbadgespy_sdk.models.i_uint_range import IUintRange
from bitbadgespy_sdk.models.i_update_history import IUpdateHistory
from bitbadgespy_sdk.models.i_user_balance_store import IUserBalanceStore
from bitbadgespy_sdk.models.iis_archived_timeline import IIsArchivedTimeline
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class ICollectionDoc(BaseModel):
    """
    
    """ # noqa: E501
    doc_id: StrictStr = Field(description="A unique stringified document ID", alias="_docId")
    id: Optional[StrictStr] = Field(default=None, description="A unique document ID (Mongo DB ObjectID)", alias="_id")
    collection_id: StrictStr = Field(alias="collectionId")
    collection_metadata_timeline: List[ICollectionMetadataTimeline] = Field(description="The collection metadata timeline", alias="collectionMetadataTimeline")
    badge_metadata_timeline: List[IBadgeMetadataTimeline] = Field(description="The badge metadata timeline", alias="badgeMetadataTimeline")
    balances_type: StrictStr = Field(description="The type of balances (i.e. \"Standard\", \"Off-Chain - Indexed\", \"Non-Public, \"Off-Chain - Non-Indexed\")", alias="balancesType")
    off_chain_balances_metadata_timeline: List[IOffChainBalancesMetadataTimeline] = Field(description="The off-chain balances metadata timeline", alias="offChainBalancesMetadataTimeline")
    custom_data_timeline: List[ICustomDataTimeline] = Field(description="The custom data timeline", alias="customDataTimeline")
    manager_timeline: List[IManagerTimeline] = Field(description="The manager timeline", alias="managerTimeline")
    collection_permissions: ICollectionPermissions = Field(description="The collection permissions", alias="collectionPermissions")
    collection_approvals: List[ICollectionApproval] = Field(description="The collection approved transfers timeline", alias="collectionApprovals")
    standards_timeline: List[IStandardsTimeline] = Field(description="The standards timeline", alias="standardsTimeline")
    is_archived_timeline: List[IIsArchivedTimeline] = Field(description="The is archived timeline", alias="isArchivedTimeline")
    default_balances: IUserBalanceStore = Field(description="The default balances for users who have not interacted with the collection yet. Only used if collection has \"Standard\" balance type.", alias="defaultBalances")
    created_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="createdBy")
    created_block: NumberType = Field(description="The block number when this collection was created", alias="createdBlock")
    created_timestamp: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdTimestamp")
    update_history: List[IUpdateHistory] = Field(description="The update history of this collection", alias="updateHistory")
    valid_badge_ids: List[IUintRange] = Field(description="Valid badge IDs for the collection", alias="validBadgeIds")
    mint_escrow_address: StrictStr = Field(description="Mint escrow address", alias="mintEscrowAddress")
    cosmos_coin_wrapper_paths: List[ICosmosCoinWrapperPath] = Field(description="The IBC wrapper paths for the collection", alias="cosmosCoinWrapperPaths")
    invariants: ICollectionInvariants = Field(description="Collection-level invariants that cannot be broken. These are set upon genesis and cannot be modified.")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_docId", "_id", "collectionId", "collectionMetadataTimeline", "badgeMetadataTimeline", "balancesType", "offChainBalancesMetadataTimeline", "customDataTimeline", "managerTimeline", "collectionPermissions", "collectionApprovals", "standardsTimeline", "isArchivedTimeline", "defaultBalances", "createdBy", "createdBlock", "createdTimestamp", "updateHistory", "validBadgeIds", "mintEscrowAddress", "cosmosCoinWrapperPaths", "invariants"]

    @field_validator('balances_type')
    def balances_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['Standard', 'Off-Chain - Indexed', 'Non-Public', 'Off-Chain - Non-Indexed']):
            raise ValueError("must be one of enum values ('Standard', 'Off-Chain - Indexed', 'Non-Public', 'Off-Chain - Non-Indexed')")
        return value

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
        """Create an instance of ICollectionDoc from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in collection_metadata_timeline (list)
        _items = []
        if self.collection_metadata_timeline:
            for _item_collection_metadata_timeline in self.collection_metadata_timeline:
                if _item_collection_metadata_timeline:
                    _items.append(_item_collection_metadata_timeline.to_dict())
            _dict['collectionMetadataTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in badge_metadata_timeline (list)
        _items = []
        if self.badge_metadata_timeline:
            for _item_badge_metadata_timeline in self.badge_metadata_timeline:
                if _item_badge_metadata_timeline:
                    _items.append(_item_badge_metadata_timeline.to_dict())
            _dict['badgeMetadataTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in off_chain_balances_metadata_timeline (list)
        _items = []
        if self.off_chain_balances_metadata_timeline:
            for _item_off_chain_balances_metadata_timeline in self.off_chain_balances_metadata_timeline:
                if _item_off_chain_balances_metadata_timeline:
                    _items.append(_item_off_chain_balances_metadata_timeline.to_dict())
            _dict['offChainBalancesMetadataTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in custom_data_timeline (list)
        _items = []
        if self.custom_data_timeline:
            for _item_custom_data_timeline in self.custom_data_timeline:
                if _item_custom_data_timeline:
                    _items.append(_item_custom_data_timeline.to_dict())
            _dict['customDataTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in manager_timeline (list)
        _items = []
        if self.manager_timeline:
            for _item_manager_timeline in self.manager_timeline:
                if _item_manager_timeline:
                    _items.append(_item_manager_timeline.to_dict())
            _dict['managerTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of collection_permissions
        if self.collection_permissions:
            _dict['collectionPermissions'] = self.collection_permissions.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in collection_approvals (list)
        _items = []
        if self.collection_approvals:
            for _item_collection_approvals in self.collection_approvals:
                if _item_collection_approvals:
                    _items.append(_item_collection_approvals.to_dict())
            _dict['collectionApprovals'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in standards_timeline (list)
        _items = []
        if self.standards_timeline:
            for _item_standards_timeline in self.standards_timeline:
                if _item_standards_timeline:
                    _items.append(_item_standards_timeline.to_dict())
            _dict['standardsTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in is_archived_timeline (list)
        _items = []
        if self.is_archived_timeline:
            for _item_is_archived_timeline in self.is_archived_timeline:
                if _item_is_archived_timeline:
                    _items.append(_item_is_archived_timeline.to_dict())
            _dict['isArchivedTimeline'] = _items
        # override the default output from pydantic by calling `to_dict()` of default_balances
        if self.default_balances:
            _dict['defaultBalances'] = self.default_balances.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_block
        if self.created_block:
            _dict['createdBlock'] = self.created_block.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_timestamp
        if self.created_timestamp:
            _dict['createdTimestamp'] = self.created_timestamp.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in update_history (list)
        _items = []
        if self.update_history:
            for _item_update_history in self.update_history:
                if _item_update_history:
                    _items.append(_item_update_history.to_dict())
            _dict['updateHistory'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in valid_badge_ids (list)
        _items = []
        if self.valid_badge_ids:
            for _item_valid_badge_ids in self.valid_badge_ids:
                if _item_valid_badge_ids:
                    _items.append(_item_valid_badge_ids.to_dict())
            _dict['validBadgeIds'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in cosmos_coin_wrapper_paths (list)
        _items = []
        if self.cosmos_coin_wrapper_paths:
            for _item_cosmos_coin_wrapper_paths in self.cosmos_coin_wrapper_paths:
                if _item_cosmos_coin_wrapper_paths:
                    _items.append(_item_cosmos_coin_wrapper_paths.to_dict())
            _dict['cosmosCoinWrapperPaths'] = _items
        # override the default output from pydantic by calling `to_dict()` of invariants
        if self.invariants:
            _dict['invariants'] = self.invariants.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ICollectionDoc from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_docId": obj.get("_docId"),
            "_id": obj.get("_id"),
            "collectionId": obj.get("collectionId"),
            "collectionMetadataTimeline": [ICollectionMetadataTimeline.from_dict(_item) for _item in obj["collectionMetadataTimeline"]] if obj.get("collectionMetadataTimeline") is not None else None,
            "badgeMetadataTimeline": [IBadgeMetadataTimeline.from_dict(_item) for _item in obj["badgeMetadataTimeline"]] if obj.get("badgeMetadataTimeline") is not None else None,
            "balancesType": obj.get("balancesType"),
            "offChainBalancesMetadataTimeline": [IOffChainBalancesMetadataTimeline.from_dict(_item) for _item in obj["offChainBalancesMetadataTimeline"]] if obj.get("offChainBalancesMetadataTimeline") is not None else None,
            "customDataTimeline": [ICustomDataTimeline.from_dict(_item) for _item in obj["customDataTimeline"]] if obj.get("customDataTimeline") is not None else None,
            "managerTimeline": [IManagerTimeline.from_dict(_item) for _item in obj["managerTimeline"]] if obj.get("managerTimeline") is not None else None,
            "collectionPermissions": ICollectionPermissions.from_dict(obj["collectionPermissions"]) if obj.get("collectionPermissions") is not None else None,
            "collectionApprovals": [ICollectionApproval.from_dict(_item) for _item in obj["collectionApprovals"]] if obj.get("collectionApprovals") is not None else None,
            "standardsTimeline": [IStandardsTimeline.from_dict(_item) for _item in obj["standardsTimeline"]] if obj.get("standardsTimeline") is not None else None,
            "isArchivedTimeline": [IIsArchivedTimeline.from_dict(_item) for _item in obj["isArchivedTimeline"]] if obj.get("isArchivedTimeline") is not None else None,
            "defaultBalances": IUserBalanceStore.from_dict(obj["defaultBalances"]) if obj.get("defaultBalances") is not None else None,
            "createdBy": obj.get("createdBy"),
            "createdBlock": NumberType.from_dict(obj["createdBlock"]) if obj.get("createdBlock") is not None else None,
            "createdTimestamp": NumberType.from_dict(obj["createdTimestamp"]) if obj.get("createdTimestamp") is not None else None,
            "updateHistory": [IUpdateHistory.from_dict(_item) for _item in obj["updateHistory"]] if obj.get("updateHistory") is not None else None,
            "validBadgeIds": [IUintRange.from_dict(_item) for _item in obj["validBadgeIds"]] if obj.get("validBadgeIds") is not None else None,
            "mintEscrowAddress": obj.get("mintEscrowAddress"),
            "cosmosCoinWrapperPaths": [ICosmosCoinWrapperPath.from_dict(_item) for _item in obj["cosmosCoinWrapperPaths"]] if obj.get("cosmosCoinWrapperPaths") is not None else None,
            "invariants": ICollectionInvariants.from_dict(obj["invariants"]) if obj.get("invariants") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


