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
from bitbadgespy_sdk.models.i_batch_badge_details import IBatchBadgeDetails
from bitbadgespy_sdk.models.i_custom_link import ICustomLink
from bitbadgespy_sdk.models.i_notification_preferences import INotificationPreferences
from bitbadgespy_sdk.models.i_profile_doc_approved_sign_in_methods import IProfileDocApprovedSignInMethods
from bitbadgespy_sdk.models.i_profile_doc_custom_pages import IProfileDocCustomPages
from bitbadgespy_sdk.models.i_profile_doc_watchlists import IProfileDocWatchlists
from bitbadgespy_sdk.models.i_social_connections import ISocialConnections
from bitbadgespy_sdk.models.number_type import NumberType
from bitbadgespy_sdk.models.supported_chain import SupportedChain
from typing import Optional, Set
from typing_extensions import Self

class IProfileDoc(BaseModel):
    """
    
    """ # noqa: E501
    doc_id: StrictStr = Field(description="A unique stringified document ID", alias="_docId")
    id: Optional[StrictStr] = Field(default=None, description="A unique document ID (Mongo DB ObjectID)", alias="_id")
    fetched_profile: Optional[StrictStr] = Field(default=None, description="Whether we have already fetched the profile or not", alias="fetchedProfile")
    embedded_wallet_address: Optional[StrictStr] = Field(default=None, description="Embedded wallet address", alias="embeddedWalletAddress")
    seen_activity: Optional[NumberType] = Field(default=None, description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="seenActivity")
    created_at: Optional[NumberType] = Field(default=None, description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdAt")
    discord: Optional[StrictStr] = Field(default=None, description="The Discord username of the account")
    twitter: Optional[StrictStr] = Field(default=None, description="The Twitter username of the account")
    github: Optional[StrictStr] = Field(default=None, description="The GitHub username of the account")
    telegram: Optional[StrictStr] = Field(default=None, description="The Telegram username of the account")
    bluesky: Optional[StrictStr] = Field(default=None, description="The Bluesky username of the account")
    readme: Optional[StrictStr] = Field(default=None, description="The readme of the account")
    custom_links: Optional[List[ICustomLink]] = Field(default=None, description="The custom links of the account", alias="customLinks")
    hidden_badges: Optional[List[IBatchBadgeDetails]] = Field(default=None, description="The hidden badges of the account", alias="hiddenBadges")
    hidden_lists: Optional[List[StrictStr]] = Field(default=None, description="The hidden lists of the account", alias="hiddenLists")
    custom_pages: Optional[IProfileDocCustomPages] = Field(default=None, alias="customPages")
    watchlists: Optional[IProfileDocWatchlists] = None
    profile_pic_url: Optional[StrictStr] = Field(default=None, description="The profile picture URL of the account", alias="profilePicUrl")
    banner_image: Optional[StrictStr] = Field(default=None, description="The banner image URL of the account", alias="bannerImage")
    username: Optional[StrictStr] = Field(default=None, description="The username of the account")
    latest_signed_in_chain: Optional[SupportedChain] = Field(default=None, description="The latest chain the user signed in with", alias="latestSignedInChain")
    sol_address: Optional[StrictStr] = Field(default=None, description="The Solana address of the profile, if applicable (bc we need it to convert)", alias="solAddress")
    notifications: Optional[INotificationPreferences] = Field(default=None, description="The notifications of the account")
    social_connections: Optional[ISocialConnections] = Field(default=None, description="Social connections stored for the account", alias="socialConnections")
    public_social_connections: Optional[ISocialConnections] = Field(default=None, description="Public social connections stored for the account", alias="publicSocialConnections")
    approved_sign_in_methods: Optional[IProfileDocApprovedSignInMethods] = Field(default=None, alias="approvedSignInMethods")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_docId", "_id", "fetchedProfile", "embeddedWalletAddress", "seenActivity", "createdAt", "discord", "twitter", "github", "telegram", "bluesky", "readme", "customLinks", "hiddenBadges", "hiddenLists", "customPages", "watchlists", "profilePicUrl", "bannerImage", "username", "latestSignedInChain", "solAddress", "notifications", "socialConnections", "publicSocialConnections", "approvedSignInMethods"]

    @field_validator('fetched_profile')
    def fetched_profile_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['full', 'partial']):
            raise ValueError("must be one of enum values ('full', 'partial')")
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
        """Create an instance of IProfileDoc from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of seen_activity
        if self.seen_activity:
            _dict['seenActivity'] = self.seen_activity.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in custom_links (list)
        _items = []
        if self.custom_links:
            for _item_custom_links in self.custom_links:
                if _item_custom_links:
                    _items.append(_item_custom_links.to_dict())
            _dict['customLinks'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in hidden_badges (list)
        _items = []
        if self.hidden_badges:
            for _item_hidden_badges in self.hidden_badges:
                if _item_hidden_badges:
                    _items.append(_item_hidden_badges.to_dict())
            _dict['hiddenBadges'] = _items
        # override the default output from pydantic by calling `to_dict()` of custom_pages
        if self.custom_pages:
            _dict['customPages'] = self.custom_pages.to_dict()
        # override the default output from pydantic by calling `to_dict()` of watchlists
        if self.watchlists:
            _dict['watchlists'] = self.watchlists.to_dict()
        # override the default output from pydantic by calling `to_dict()` of notifications
        if self.notifications:
            _dict['notifications'] = self.notifications.to_dict()
        # override the default output from pydantic by calling `to_dict()` of social_connections
        if self.social_connections:
            _dict['socialConnections'] = self.social_connections.to_dict()
        # override the default output from pydantic by calling `to_dict()` of public_social_connections
        if self.public_social_connections:
            _dict['publicSocialConnections'] = self.public_social_connections.to_dict()
        # override the default output from pydantic by calling `to_dict()` of approved_sign_in_methods
        if self.approved_sign_in_methods:
            _dict['approvedSignInMethods'] = self.approved_sign_in_methods.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IProfileDoc from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_docId": obj.get("_docId"),
            "_id": obj.get("_id"),
            "fetchedProfile": obj.get("fetchedProfile"),
            "embeddedWalletAddress": obj.get("embeddedWalletAddress"),
            "seenActivity": NumberType.from_dict(obj["seenActivity"]) if obj.get("seenActivity") is not None else None,
            "createdAt": NumberType.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "discord": obj.get("discord"),
            "twitter": obj.get("twitter"),
            "github": obj.get("github"),
            "telegram": obj.get("telegram"),
            "bluesky": obj.get("bluesky"),
            "readme": obj.get("readme"),
            "customLinks": [ICustomLink.from_dict(_item) for _item in obj["customLinks"]] if obj.get("customLinks") is not None else None,
            "hiddenBadges": [IBatchBadgeDetails.from_dict(_item) for _item in obj["hiddenBadges"]] if obj.get("hiddenBadges") is not None else None,
            "hiddenLists": obj.get("hiddenLists"),
            "customPages": IProfileDocCustomPages.from_dict(obj["customPages"]) if obj.get("customPages") is not None else None,
            "watchlists": IProfileDocWatchlists.from_dict(obj["watchlists"]) if obj.get("watchlists") is not None else None,
            "profilePicUrl": obj.get("profilePicUrl"),
            "bannerImage": obj.get("bannerImage"),
            "username": obj.get("username"),
            "latestSignedInChain": obj.get("latestSignedInChain"),
            "solAddress": obj.get("solAddress"),
            "notifications": INotificationPreferences.from_dict(obj["notifications"]) if obj.get("notifications") is not None else None,
            "socialConnections": ISocialConnections.from_dict(obj["socialConnections"]) if obj.get("socialConnections") is not None else None,
            "publicSocialConnections": ISocialConnections.from_dict(obj["publicSocialConnections"]) if obj.get("publicSocialConnections") is not None else None,
            "approvedSignInMethods": IProfileDocApprovedSignInMethods.from_dict(obj["approvedSignInMethods"]) if obj.get("approvedSignInMethods") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


