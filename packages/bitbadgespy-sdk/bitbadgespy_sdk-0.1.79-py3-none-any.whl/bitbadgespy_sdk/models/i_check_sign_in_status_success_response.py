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
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_bluesky import ICheckSignInStatusSuccessResponseBluesky
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_discord import ICheckSignInStatusSuccessResponseDiscord
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_facebook import ICheckSignInStatusSuccessResponseFacebook
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_farcaster import ICheckSignInStatusSuccessResponseFarcaster
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_github import ICheckSignInStatusSuccessResponseGithub
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_google import ICheckSignInStatusSuccessResponseGoogle
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_google_calendar import ICheckSignInStatusSuccessResponseGoogleCalendar
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_linked_in import ICheckSignInStatusSuccessResponseLinkedIn
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_mailchimp import ICheckSignInStatusSuccessResponseMailchimp
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_meetup import ICheckSignInStatusSuccessResponseMeetup
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_reddit import ICheckSignInStatusSuccessResponseReddit
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_shopify import ICheckSignInStatusSuccessResponseShopify
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_slack import ICheckSignInStatusSuccessResponseSlack
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_strava import ICheckSignInStatusSuccessResponseStrava
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_telegram import ICheckSignInStatusSuccessResponseTelegram
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_twitch import ICheckSignInStatusSuccessResponseTwitch
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_twitter import ICheckSignInStatusSuccessResponseTwitter
from bitbadgespy_sdk.models.i_check_sign_in_status_success_response_youtube import ICheckSignInStatusSuccessResponseYoutube
from bitbadgespy_sdk.models.o_auth_scope_details_with_id import OAuthScopeDetailsWithId
from bitbadgespy_sdk.models.supported_chain import SupportedChain
from typing import Optional, Set
from typing_extensions import Self

class ICheckSignInStatusSuccessResponse(BaseModel):
    """
    ICheckSignInStatusSuccessResponse
    """ # noqa: E501
    signed_in: StrictBool = Field(description="Indicates whether the user is signed in.", alias="signedIn")
    address: StrictStr = Field(description="A native address is an address that is native to the user's chain. For example, an Ethereum address is native to Ethereum (0x...). If this type is used, we support any native address type. We do not require conversion to a BitBadges address like the BitBadgesAddress type.")
    bitbadges_address: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="bitbadgesAddress")
    chain: SupportedChain
    scopes: List[OAuthScopeDetailsWithId] = Field(description="Approved scopes")
    message: StrictStr = Field(description="SiwbbMessage is the sign-in challenge strint to be signed by the user. It extends EIP 4361 Sign-In with Ethereum and adds additional fields for cross-chain compatibility and native asset ownership verification.  For example, 'https://bitbadges.io wants you to sign in with your Ethereum address ...'")
    email: Optional[StrictStr] = Field(default=None, description="The email of the session.")
    discord: Optional[ICheckSignInStatusSuccessResponseDiscord] = None
    twitter: Optional[ICheckSignInStatusSuccessResponseTwitter] = None
    github: Optional[ICheckSignInStatusSuccessResponseGithub] = None
    google: Optional[ICheckSignInStatusSuccessResponseGoogle] = None
    twitch: Optional[ICheckSignInStatusSuccessResponseTwitch] = None
    strava: Optional[ICheckSignInStatusSuccessResponseStrava] = None
    reddit: Optional[ICheckSignInStatusSuccessResponseReddit] = None
    meetup: Optional[ICheckSignInStatusSuccessResponseMeetup] = None
    bluesky: Optional[ICheckSignInStatusSuccessResponseBluesky] = None
    mailchimp: Optional[ICheckSignInStatusSuccessResponseMailchimp] = None
    facebook: Optional[ICheckSignInStatusSuccessResponseFacebook] = None
    linked_in: Optional[ICheckSignInStatusSuccessResponseLinkedIn] = Field(default=None, alias="linkedIn")
    shopify: Optional[ICheckSignInStatusSuccessResponseShopify] = None
    telegram: Optional[ICheckSignInStatusSuccessResponseTelegram] = None
    farcaster: Optional[ICheckSignInStatusSuccessResponseFarcaster] = None
    slack: Optional[ICheckSignInStatusSuccessResponseSlack] = None
    youtube: Optional[ICheckSignInStatusSuccessResponseYoutube] = None
    google_calendar: Optional[ICheckSignInStatusSuccessResponseGoogleCalendar] = Field(default=None, alias="googleCalendar")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["signedIn", "address", "bitbadgesAddress", "chain", "scopes", "message", "email", "discord", "twitter", "github", "google", "twitch", "strava", "reddit", "meetup", "bluesky", "mailchimp", "facebook", "linkedIn", "shopify", "telegram", "farcaster", "slack", "youtube", "googleCalendar"]

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
        """Create an instance of ICheckSignInStatusSuccessResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in scopes (list)
        _items = []
        if self.scopes:
            for _item_scopes in self.scopes:
                if _item_scopes:
                    _items.append(_item_scopes.to_dict())
            _dict['scopes'] = _items
        # override the default output from pydantic by calling `to_dict()` of discord
        if self.discord:
            _dict['discord'] = self.discord.to_dict()
        # override the default output from pydantic by calling `to_dict()` of twitter
        if self.twitter:
            _dict['twitter'] = self.twitter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of github
        if self.github:
            _dict['github'] = self.github.to_dict()
        # override the default output from pydantic by calling `to_dict()` of google
        if self.google:
            _dict['google'] = self.google.to_dict()
        # override the default output from pydantic by calling `to_dict()` of twitch
        if self.twitch:
            _dict['twitch'] = self.twitch.to_dict()
        # override the default output from pydantic by calling `to_dict()` of strava
        if self.strava:
            _dict['strava'] = self.strava.to_dict()
        # override the default output from pydantic by calling `to_dict()` of reddit
        if self.reddit:
            _dict['reddit'] = self.reddit.to_dict()
        # override the default output from pydantic by calling `to_dict()` of meetup
        if self.meetup:
            _dict['meetup'] = self.meetup.to_dict()
        # override the default output from pydantic by calling `to_dict()` of bluesky
        if self.bluesky:
            _dict['bluesky'] = self.bluesky.to_dict()
        # override the default output from pydantic by calling `to_dict()` of mailchimp
        if self.mailchimp:
            _dict['mailchimp'] = self.mailchimp.to_dict()
        # override the default output from pydantic by calling `to_dict()` of facebook
        if self.facebook:
            _dict['facebook'] = self.facebook.to_dict()
        # override the default output from pydantic by calling `to_dict()` of linked_in
        if self.linked_in:
            _dict['linkedIn'] = self.linked_in.to_dict()
        # override the default output from pydantic by calling `to_dict()` of shopify
        if self.shopify:
            _dict['shopify'] = self.shopify.to_dict()
        # override the default output from pydantic by calling `to_dict()` of telegram
        if self.telegram:
            _dict['telegram'] = self.telegram.to_dict()
        # override the default output from pydantic by calling `to_dict()` of farcaster
        if self.farcaster:
            _dict['farcaster'] = self.farcaster.to_dict()
        # override the default output from pydantic by calling `to_dict()` of slack
        if self.slack:
            _dict['slack'] = self.slack.to_dict()
        # override the default output from pydantic by calling `to_dict()` of youtube
        if self.youtube:
            _dict['youtube'] = self.youtube.to_dict()
        # override the default output from pydantic by calling `to_dict()` of google_calendar
        if self.google_calendar:
            _dict['googleCalendar'] = self.google_calendar.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ICheckSignInStatusSuccessResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "signedIn": obj.get("signedIn"),
            "address": obj.get("address"),
            "bitbadgesAddress": obj.get("bitbadgesAddress"),
            "chain": obj.get("chain"),
            "scopes": [OAuthScopeDetailsWithId.from_dict(_item) for _item in obj["scopes"]] if obj.get("scopes") is not None else None,
            "message": obj.get("message"),
            "email": obj.get("email"),
            "discord": ICheckSignInStatusSuccessResponseDiscord.from_dict(obj["discord"]) if obj.get("discord") is not None else None,
            "twitter": ICheckSignInStatusSuccessResponseTwitter.from_dict(obj["twitter"]) if obj.get("twitter") is not None else None,
            "github": ICheckSignInStatusSuccessResponseGithub.from_dict(obj["github"]) if obj.get("github") is not None else None,
            "google": ICheckSignInStatusSuccessResponseGoogle.from_dict(obj["google"]) if obj.get("google") is not None else None,
            "twitch": ICheckSignInStatusSuccessResponseTwitch.from_dict(obj["twitch"]) if obj.get("twitch") is not None else None,
            "strava": ICheckSignInStatusSuccessResponseStrava.from_dict(obj["strava"]) if obj.get("strava") is not None else None,
            "reddit": ICheckSignInStatusSuccessResponseReddit.from_dict(obj["reddit"]) if obj.get("reddit") is not None else None,
            "meetup": ICheckSignInStatusSuccessResponseMeetup.from_dict(obj["meetup"]) if obj.get("meetup") is not None else None,
            "bluesky": ICheckSignInStatusSuccessResponseBluesky.from_dict(obj["bluesky"]) if obj.get("bluesky") is not None else None,
            "mailchimp": ICheckSignInStatusSuccessResponseMailchimp.from_dict(obj["mailchimp"]) if obj.get("mailchimp") is not None else None,
            "facebook": ICheckSignInStatusSuccessResponseFacebook.from_dict(obj["facebook"]) if obj.get("facebook") is not None else None,
            "linkedIn": ICheckSignInStatusSuccessResponseLinkedIn.from_dict(obj["linkedIn"]) if obj.get("linkedIn") is not None else None,
            "shopify": ICheckSignInStatusSuccessResponseShopify.from_dict(obj["shopify"]) if obj.get("shopify") is not None else None,
            "telegram": ICheckSignInStatusSuccessResponseTelegram.from_dict(obj["telegram"]) if obj.get("telegram") is not None else None,
            "farcaster": ICheckSignInStatusSuccessResponseFarcaster.from_dict(obj["farcaster"]) if obj.get("farcaster") is not None else None,
            "slack": ICheckSignInStatusSuccessResponseSlack.from_dict(obj["slack"]) if obj.get("slack") is not None else None,
            "youtube": ICheckSignInStatusSuccessResponseYoutube.from_dict(obj["youtube"]) if obj.get("youtube") is not None else None,
            "googleCalendar": ICheckSignInStatusSuccessResponseGoogleCalendar.from_dict(obj["googleCalendar"]) if obj.get("googleCalendar") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


