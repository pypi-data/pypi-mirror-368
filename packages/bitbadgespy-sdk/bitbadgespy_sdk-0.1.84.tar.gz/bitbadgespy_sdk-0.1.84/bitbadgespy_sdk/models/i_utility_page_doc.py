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
from bitbadgespy_sdk.models.i_estimated_cost import IEstimatedCost
from bitbadgespy_sdk.models.i_inherit_metadata_from import IInheritMetadataFrom
from bitbadgespy_sdk.models.i_linked_to import ILinkedTo
from bitbadgespy_sdk.models.i_metadata import IMetadata
from bitbadgespy_sdk.models.i_uint_range import IUintRange
from bitbadgespy_sdk.models.i_utility_page_content import IUtilityPageContent
from bitbadgespy_sdk.models.i_utility_page_doc_approval_status import IUtilityPageDocApprovalStatus
from bitbadgespy_sdk.models.i_utility_page_doc_home_page_view import IUtilityPageDocHomePageView
from bitbadgespy_sdk.models.i_utility_page_doc_views_by_period import IUtilityPageDocViewsByPeriod
from bitbadgespy_sdk.models.i_utility_page_link import IUtilityPageLink
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IUtilityPageDoc(BaseModel):
    """
    
    """ # noqa: E501
    doc_id: StrictStr = Field(description="A unique stringified document ID", alias="_docId")
    id: Optional[StrictStr] = Field(default=None, description="A unique document ID (Mongo DB ObjectID)", alias="_id")
    listing_id: StrictStr = Field(description="The listing ID", alias="listingId")
    type: StrictStr = Field(description="Type of the listing")
    created_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="createdBy")
    managed_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="managedBy")
    direct_link: Optional[StrictStr] = Field(default=None, description="The direct link for the listing. If specified, we will skip the entire content / listing page. Thus, content and links should be empty [].", alias="directLink")
    created_at: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdAt")
    last_updated: Optional[NumberType] = Field(default=None, description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="lastUpdated")
    metadata: IMetadata = Field(description="The overall metadata for the listing")
    inherit_metadata_from: Optional[IInheritMetadataFrom] = Field(default=None, description="Where to inherit metadata from? Only one can be specified.", alias="inheritMetadataFrom")
    content: List[IUtilityPageContent] = Field(description="The paginated content for the listing")
    links: List[IUtilityPageLink] = Field(description="The relevant links for the listing")
    display_times: Optional[IUintRange] = Field(default=None, description="Optional time range for when the listing should be shown", alias="displayTimes")
    visibility: StrictStr = Field(description="Visibility state of the listing")
    categories: List[StrictStr] = Field(description="The categories of the listing")
    approval_status: IUtilityPageDocApprovalStatus = Field(alias="approvalStatus")
    view_count: Optional[NumberType] = Field(default=None, description="The total view count for this listing. This is updated periodically from the view tracking document.", alias="viewCount")
    estimated_cost: Optional[IEstimatedCost] = Field(default=None, description="The estimated cost for this utility/service", alias="estimatedCost")
    estimated_time: Optional[StrictStr] = Field(default=None, description="The estimated time to complete or deliver this utility/service", alias="estimatedTime")
    views_by_period: Optional[IUtilityPageDocViewsByPeriod] = Field(default=None, alias="viewsByPeriod")
    linked_to: Optional[ILinkedTo] = Field(default=None, description="Linked details", alias="linkedTo")
    locale: Optional[StrictStr] = Field(default=None, description="Locale (ex: es, fr, etc.). If not specified, we assume en.")
    home_page_view: Optional[IUtilityPageDocHomePageView] = Field(default=None, alias="homePageView")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_docId", "_id", "listingId", "type", "createdBy", "managedBy", "directLink", "createdAt", "lastUpdated", "metadata", "inheritMetadataFrom", "content", "links", "displayTimes", "visibility", "categories", "approvalStatus", "viewCount", "estimatedCost", "estimatedTime", "viewsByPeriod", "linkedTo", "locale", "homePageView"]

    @field_validator('visibility')
    def visibility_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['public', 'private', 'unlisted']):
            raise ValueError("must be one of enum values ('public', 'private', 'unlisted')")
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
        """Create an instance of IUtilityPageDoc from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of last_updated
        if self.last_updated:
            _dict['lastUpdated'] = self.last_updated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of metadata
        if self.metadata:
            _dict['metadata'] = self.metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of inherit_metadata_from
        if self.inherit_metadata_from:
            _dict['inheritMetadataFrom'] = self.inherit_metadata_from.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in content (list)
        _items = []
        if self.content:
            for _item_content in self.content:
                if _item_content:
                    _items.append(_item_content.to_dict())
            _dict['content'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in links (list)
        _items = []
        if self.links:
            for _item_links in self.links:
                if _item_links:
                    _items.append(_item_links.to_dict())
            _dict['links'] = _items
        # override the default output from pydantic by calling `to_dict()` of display_times
        if self.display_times:
            _dict['displayTimes'] = self.display_times.to_dict()
        # override the default output from pydantic by calling `to_dict()` of approval_status
        if self.approval_status:
            _dict['approvalStatus'] = self.approval_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of view_count
        if self.view_count:
            _dict['viewCount'] = self.view_count.to_dict()
        # override the default output from pydantic by calling `to_dict()` of estimated_cost
        if self.estimated_cost:
            _dict['estimatedCost'] = self.estimated_cost.to_dict()
        # override the default output from pydantic by calling `to_dict()` of views_by_period
        if self.views_by_period:
            _dict['viewsByPeriod'] = self.views_by_period.to_dict()
        # override the default output from pydantic by calling `to_dict()` of linked_to
        if self.linked_to:
            _dict['linkedTo'] = self.linked_to.to_dict()
        # override the default output from pydantic by calling `to_dict()` of home_page_view
        if self.home_page_view:
            _dict['homePageView'] = self.home_page_view.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IUtilityPageDoc from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_docId": obj.get("_docId"),
            "_id": obj.get("_id"),
            "listingId": obj.get("listingId"),
            "type": obj.get("type"),
            "createdBy": obj.get("createdBy"),
            "managedBy": obj.get("managedBy"),
            "directLink": obj.get("directLink"),
            "createdAt": NumberType.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "lastUpdated": NumberType.from_dict(obj["lastUpdated"]) if obj.get("lastUpdated") is not None else None,
            "metadata": IMetadata.from_dict(obj["metadata"]) if obj.get("metadata") is not None else None,
            "inheritMetadataFrom": IInheritMetadataFrom.from_dict(obj["inheritMetadataFrom"]) if obj.get("inheritMetadataFrom") is not None else None,
            "content": [IUtilityPageContent.from_dict(_item) for _item in obj["content"]] if obj.get("content") is not None else None,
            "links": [IUtilityPageLink.from_dict(_item) for _item in obj["links"]] if obj.get("links") is not None else None,
            "displayTimes": IUintRange.from_dict(obj["displayTimes"]) if obj.get("displayTimes") is not None else None,
            "visibility": obj.get("visibility"),
            "categories": obj.get("categories"),
            "approvalStatus": IUtilityPageDocApprovalStatus.from_dict(obj["approvalStatus"]) if obj.get("approvalStatus") is not None else None,
            "viewCount": NumberType.from_dict(obj["viewCount"]) if obj.get("viewCount") is not None else None,
            "estimatedCost": IEstimatedCost.from_dict(obj["estimatedCost"]) if obj.get("estimatedCost") is not None else None,
            "estimatedTime": obj.get("estimatedTime"),
            "viewsByPeriod": IUtilityPageDocViewsByPeriod.from_dict(obj["viewsByPeriod"]) if obj.get("viewsByPeriod") is not None else None,
            "linkedTo": ILinkedTo.from_dict(obj["linkedTo"]) if obj.get("linkedTo") is not None else None,
            "locale": obj.get("locale"),
            "homePageView": IUtilityPageDocHomePageView.from_dict(obj["homePageView"]) if obj.get("homePageView") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


