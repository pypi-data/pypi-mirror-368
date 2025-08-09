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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from bitbadgespy_sdk.models.i_approval_tracker_doc import IApprovalTrackerDoc
from bitbadgespy_sdk.models.i_balance_doc import IBalanceDoc
from bitbadgespy_sdk.models.i_batch_badge_details import IBatchBadgeDetails
from bitbadgespy_sdk.models.i_bit_badges_user_info_alias import IBitBadgesUserInfoAlias
from bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods import IBitBadgesUserInfoApprovedSignInMethods
from bitbadgespy_sdk.models.i_bit_badges_user_info_custom_pages import IBitBadgesUserInfoCustomPages
from bitbadgespy_sdk.models.i_bit_badges_user_info_nsfw import IBitBadgesUserInfoNsfw
from bitbadgespy_sdk.models.i_bit_badges_user_info_reported import IBitBadgesUserInfoReported
from bitbadgespy_sdk.models.i_bit_badges_user_info_views_value import IBitBadgesUserInfoViewsValue
from bitbadgespy_sdk.models.i_bit_badges_user_info_watchlists import IBitBadgesUserInfoWatchlists
from bitbadgespy_sdk.models.i_claim_activity_doc import IClaimActivityDoc
from bitbadgespy_sdk.models.i_claim_alert_doc import IClaimAlertDoc
from bitbadgespy_sdk.models.i_cosmos_coin import ICosmosCoin
from bitbadgespy_sdk.models.i_creator_credits_doc import ICreatorCreditsDoc
from bitbadgespy_sdk.models.i_custom_link import ICustomLink
from bitbadgespy_sdk.models.i_list_activity_doc import IListActivityDoc
from bitbadgespy_sdk.models.i_merkle_challenge_tracker_doc import IMerkleChallengeTrackerDoc
from bitbadgespy_sdk.models.i_notification_preferences import INotificationPreferences
from bitbadgespy_sdk.models.i_points_activity_doc import IPointsActivityDoc
from bitbadgespy_sdk.models.i_social_connections import ISocialConnections
from bitbadgespy_sdk.models.i_transfer_activity_doc import ITransferActivityDoc
from bitbadgespy_sdk.models.isiwbb_request_doc import ISIWBBRequestDoc
from bitbadgespy_sdk.models.number_type import NumberType
from bitbadgespy_sdk.models.supported_chain import SupportedChain
from typing import Optional, Set
from typing_extensions import Self

class IBitBadgesUserInfo(BaseModel):
    """
    
    """ # noqa: E501
    doc_id: StrictStr = Field(description="A unique stringified document ID", alias="_docId")
    id: Optional[StrictStr] = Field(default=None, description="A unique document ID (Mongo DB ObjectID)", alias="_id")
    public_key: StrictStr = Field(description="The public key of the account", alias="publicKey")
    account_number: NumberType = Field(description="The account number of the account. This is the account number registered on the BitBadges blockchain.", alias="accountNumber")
    pub_key_type: StrictStr = Field(description="The public key type of the account", alias="pubKeyType")
    bitbadges_address: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="bitbadgesAddress")
    eth_address: StrictStr = Field(description="The Eth address of the account", alias="ethAddress")
    btc_address: StrictStr = Field(description="The Bitcoin address of the account", alias="btcAddress")
    thor_address: StrictStr = Field(description="The Thorchain address of the account", alias="thorAddress")
    sequence: Optional[NumberType] = Field(default=None, description="The sequence of the account. This is the nonce for the blockchain for this account")
    balances: Optional[List[ICosmosCoin]] = Field(default=None, description="The BADGE balance of the account and other sdk.coin balances")
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
    custom_pages: Optional[IBitBadgesUserInfoCustomPages] = Field(default=None, alias="customPages")
    watchlists: Optional[IBitBadgesUserInfoWatchlists] = None
    profile_pic_url: Optional[StrictStr] = Field(default=None, description="The profile picture URL of the account", alias="profilePicUrl")
    banner_image: Optional[StrictStr] = Field(default=None, description="The banner image URL of the account", alias="bannerImage")
    username: Optional[StrictStr] = Field(default=None, description="The username of the account")
    latest_signed_in_chain: Optional[SupportedChain] = Field(default=None, description="The latest chain the user signed in with", alias="latestSignedInChain")
    notifications: Optional[INotificationPreferences] = Field(default=None, description="The notifications of the account")
    social_connections: Optional[ISocialConnections] = Field(default=None, description="Social connections stored for the account", alias="socialConnections")
    public_social_connections: Optional[ISocialConnections] = Field(default=None, description="Public social connections stored for the account", alias="publicSocialConnections")
    approved_sign_in_methods: Optional[IBitBadgesUserInfoApprovedSignInMethods] = Field(default=None, alias="approvedSignInMethods")
    resolved_name: Optional[StrictStr] = Field(default=None, description="The resolved name of the account (e.g. ENS name).", alias="resolvedName")
    avatar: Optional[StrictStr] = Field(default=None, description="The avatar of the account.")
    sol_address: StrictStr = Field(description="The Solana address of the account. Note: This may be empty if we do not have it yet. Solana -> BitBadges address conversions are one-way, and we cannot convert a BitBadges address to a Solana address without prior knowledge.", alias="solAddress")
    chain: SupportedChain = Field(description="The chain of the account.")
    airdropped: Optional[StrictBool] = Field(default=None, description="Indicates whether the account has claimed their airdrop.")
    collected: List[IBalanceDoc] = Field(description="A list of badges that the account has collected. Paginated and fetched as needed. To be used in conjunction with views.")
    activity: List[ITransferActivityDoc] = Field(description="A list of transfer activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.")
    list_activity: List[IListActivityDoc] = Field(description="A list of list activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="listActivity")
    claim_activity: Optional[List[IClaimActivityDoc]] = Field(default=None, description="A list of claim activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="claimActivity")
    points_activity: Optional[List[IPointsActivityDoc]] = Field(default=None, description="A list of points activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="pointsActivity")
    challenge_trackers: List[IMerkleChallengeTrackerDoc] = Field(description="A list of merkle challenge activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="challengeTrackers")
    approval_trackers: List[IApprovalTrackerDoc] = Field(description="A list of approvals tracker activity items for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="approvalTrackers")
    address_lists: List[Any] = Field(description="A list of address lists for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="addressLists")
    claim_alerts: List[IClaimAlertDoc] = Field(description="A list of claim alerts for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="claimAlerts")
    siwbb_requests: List[ISIWBBRequestDoc] = Field(description="A list of SIWBB requests for the account. Paginated and fetched as needed. To be used in conjunction with views.", alias="siwbbRequests")
    address: StrictStr = Field(description="A native address is an address that is native to the user's chain. For example, an Ethereum address is native to Ethereum (0x...). If this type is used, we support any native address type. We do not require conversion to a BitBadges address like the BitBadgesAddress type.")
    nsfw: Optional[IBitBadgesUserInfoNsfw] = None
    reported: Optional[IBitBadgesUserInfoReported] = None
    views: Dict[str, IBitBadgesUserInfoViewsValue] = Field(description="The views for this collection and their pagination Doc. Views will only include the doc _ids. Use the pagination to fetch more.  For example, if you want to fetch the activity for a view, you would use the view's pagination to fetch the doc _ids, then use the corresponding activity array to find the matching docs.")
    alias: Optional[IBitBadgesUserInfoAlias] = None
    creator_credits: Optional[ICreatorCreditsDoc] = Field(default=None, description="The credits for the account.", alias="creatorCredits")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["_docId", "_id", "publicKey", "accountNumber", "pubKeyType", "bitbadgesAddress", "ethAddress", "btcAddress", "thorAddress", "sequence", "balances", "fetchedProfile", "embeddedWalletAddress", "seenActivity", "createdAt", "discord", "twitter", "github", "telegram", "bluesky", "readme", "customLinks", "hiddenBadges", "hiddenLists", "customPages", "watchlists", "profilePicUrl", "bannerImage", "username", "latestSignedInChain", "notifications", "socialConnections", "publicSocialConnections", "approvedSignInMethods", "resolvedName", "avatar", "solAddress", "chain", "airdropped", "collected", "activity", "listActivity", "claimActivity", "pointsActivity", "challengeTrackers", "approvalTrackers", "addressLists", "claimAlerts", "siwbbRequests", "address", "nsfw", "reported", "views", "alias", "creatorCredits"]

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
        """Create an instance of IBitBadgesUserInfo from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of account_number
        if self.account_number:
            _dict['accountNumber'] = self.account_number.to_dict()
        # override the default output from pydantic by calling `to_dict()` of sequence
        if self.sequence:
            _dict['sequence'] = self.sequence.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in balances (list)
        _items = []
        if self.balances:
            for _item_balances in self.balances:
                if _item_balances:
                    _items.append(_item_balances.to_dict())
            _dict['balances'] = _items
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
        # override the default output from pydantic by calling `to_dict()` of each item in collected (list)
        _items = []
        if self.collected:
            for _item_collected in self.collected:
                if _item_collected:
                    _items.append(_item_collected.to_dict())
            _dict['collected'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in activity (list)
        _items = []
        if self.activity:
            for _item_activity in self.activity:
                if _item_activity:
                    _items.append(_item_activity.to_dict())
            _dict['activity'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in list_activity (list)
        _items = []
        if self.list_activity:
            for _item_list_activity in self.list_activity:
                if _item_list_activity:
                    _items.append(_item_list_activity.to_dict())
            _dict['listActivity'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in claim_activity (list)
        _items = []
        if self.claim_activity:
            for _item_claim_activity in self.claim_activity:
                if _item_claim_activity:
                    _items.append(_item_claim_activity.to_dict())
            _dict['claimActivity'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in points_activity (list)
        _items = []
        if self.points_activity:
            for _item_points_activity in self.points_activity:
                if _item_points_activity:
                    _items.append(_item_points_activity.to_dict())
            _dict['pointsActivity'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in challenge_trackers (list)
        _items = []
        if self.challenge_trackers:
            for _item_challenge_trackers in self.challenge_trackers:
                if _item_challenge_trackers:
                    _items.append(_item_challenge_trackers.to_dict())
            _dict['challengeTrackers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in approval_trackers (list)
        _items = []
        if self.approval_trackers:
            for _item_approval_trackers in self.approval_trackers:
                if _item_approval_trackers:
                    _items.append(_item_approval_trackers.to_dict())
            _dict['approvalTrackers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in claim_alerts (list)
        _items = []
        if self.claim_alerts:
            for _item_claim_alerts in self.claim_alerts:
                if _item_claim_alerts:
                    _items.append(_item_claim_alerts.to_dict())
            _dict['claimAlerts'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in siwbb_requests (list)
        _items = []
        if self.siwbb_requests:
            for _item_siwbb_requests in self.siwbb_requests:
                if _item_siwbb_requests:
                    _items.append(_item_siwbb_requests.to_dict())
            _dict['siwbbRequests'] = _items
        # override the default output from pydantic by calling `to_dict()` of nsfw
        if self.nsfw:
            _dict['nsfw'] = self.nsfw.to_dict()
        # override the default output from pydantic by calling `to_dict()` of reported
        if self.reported:
            _dict['reported'] = self.reported.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each value in views (dict)
        _field_dict = {}
        if self.views:
            for _key_views in self.views:
                if self.views[_key_views]:
                    _field_dict[_key_views] = self.views[_key_views].to_dict()
            _dict['views'] = _field_dict
        # override the default output from pydantic by calling `to_dict()` of alias
        if self.alias:
            _dict['alias'] = self.alias.to_dict()
        # override the default output from pydantic by calling `to_dict()` of creator_credits
        if self.creator_credits:
            _dict['creatorCredits'] = self.creator_credits.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IBitBadgesUserInfo from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_docId": obj.get("_docId"),
            "_id": obj.get("_id"),
            "publicKey": obj.get("publicKey"),
            "accountNumber": NumberType.from_dict(obj["accountNumber"]) if obj.get("accountNumber") is not None else None,
            "pubKeyType": obj.get("pubKeyType"),
            "bitbadgesAddress": obj.get("bitbadgesAddress"),
            "ethAddress": obj.get("ethAddress"),
            "btcAddress": obj.get("btcAddress"),
            "thorAddress": obj.get("thorAddress"),
            "sequence": NumberType.from_dict(obj["sequence"]) if obj.get("sequence") is not None else None,
            "balances": [ICosmosCoin.from_dict(_item) for _item in obj["balances"]] if obj.get("balances") is not None else None,
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
            "customPages": IBitBadgesUserInfoCustomPages.from_dict(obj["customPages"]) if obj.get("customPages") is not None else None,
            "watchlists": IBitBadgesUserInfoWatchlists.from_dict(obj["watchlists"]) if obj.get("watchlists") is not None else None,
            "profilePicUrl": obj.get("profilePicUrl"),
            "bannerImage": obj.get("bannerImage"),
            "username": obj.get("username"),
            "latestSignedInChain": obj.get("latestSignedInChain"),
            "notifications": INotificationPreferences.from_dict(obj["notifications"]) if obj.get("notifications") is not None else None,
            "socialConnections": ISocialConnections.from_dict(obj["socialConnections"]) if obj.get("socialConnections") is not None else None,
            "publicSocialConnections": ISocialConnections.from_dict(obj["publicSocialConnections"]) if obj.get("publicSocialConnections") is not None else None,
            "approvedSignInMethods": IBitBadgesUserInfoApprovedSignInMethods.from_dict(obj["approvedSignInMethods"]) if obj.get("approvedSignInMethods") is not None else None,
            "resolvedName": obj.get("resolvedName"),
            "avatar": obj.get("avatar"),
            "solAddress": obj.get("solAddress"),
            "chain": obj.get("chain"),
            "airdropped": obj.get("airdropped"),
            "collected": [IBalanceDoc.from_dict(_item) for _item in obj["collected"]] if obj.get("collected") is not None else None,
            "activity": [ITransferActivityDoc.from_dict(_item) for _item in obj["activity"]] if obj.get("activity") is not None else None,
            "listActivity": [IListActivityDoc.from_dict(_item) for _item in obj["listActivity"]] if obj.get("listActivity") is not None else None,
            "claimActivity": [IClaimActivityDoc.from_dict(_item) for _item in obj["claimActivity"]] if obj.get("claimActivity") is not None else None,
            "pointsActivity": [IPointsActivityDoc.from_dict(_item) for _item in obj["pointsActivity"]] if obj.get("pointsActivity") is not None else None,
            "challengeTrackers": [IMerkleChallengeTrackerDoc.from_dict(_item) for _item in obj["challengeTrackers"]] if obj.get("challengeTrackers") is not None else None,
            "approvalTrackers": [IApprovalTrackerDoc.from_dict(_item) for _item in obj["approvalTrackers"]] if obj.get("approvalTrackers") is not None else None,
            "addressLists": obj.get("addressLists"),
            "claimAlerts": [IClaimAlertDoc.from_dict(_item) for _item in obj["claimAlerts"]] if obj.get("claimAlerts") is not None else None,
            "siwbbRequests": [ISIWBBRequestDoc.from_dict(_item) for _item in obj["siwbbRequests"]] if obj.get("siwbbRequests") is not None else None,
            "address": obj.get("address"),
            "nsfw": IBitBadgesUserInfoNsfw.from_dict(obj["nsfw"]) if obj.get("nsfw") is not None else None,
            "reported": IBitBadgesUserInfoReported.from_dict(obj["reported"]) if obj.get("reported") is not None else None,
            "views": dict(
                (_k, IBitBadgesUserInfoViewsValue.from_dict(_v))
                for _k, _v in obj["views"].items()
            )
            if obj.get("views") is not None
            else None,
            "alias": IBitBadgesUserInfoAlias.from_dict(obj["alias"]) if obj.get("alias") is not None else None,
            "creatorCredits": ICreatorCreditsDoc.from_dict(obj["creatorCredits"]) if obj.get("creatorCredits") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


