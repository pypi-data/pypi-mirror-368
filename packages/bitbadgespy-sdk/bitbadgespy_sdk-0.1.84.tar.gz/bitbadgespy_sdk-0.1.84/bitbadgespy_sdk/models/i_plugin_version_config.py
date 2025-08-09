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
from bitbadgespy_sdk.models.i_plugin_version_config_claim_creator_redirect import IPluginVersionConfigClaimCreatorRedirect
from bitbadgespy_sdk.models.i_plugin_version_config_user_input_redirect import IPluginVersionConfigUserInputRedirect
from bitbadgespy_sdk.models.i_plugin_version_config_verification_call import IPluginVersionConfigVerificationCall
from bitbadgespy_sdk.models.json_body_input_schema import JsonBodyInputSchema
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IPluginVersionConfig(BaseModel):
    """
    IPluginVersionConfig
    """ # noqa: E501
    version: NumberType = Field(description="Version of the plugin")
    finalized: StrictBool = Field(description="True if the version is finalized")
    created_at: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdAt")
    last_updated: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="lastUpdated")
    reuse_for_non_indexed: StrictBool = Field(description="Reuse for nonindexed balances? Only applicable if is stateless, requires no user inputs, and requires no sessions.", alias="reuseForNonIndexed")
    receive_status_webhook: StrictBool = Field(description="Whether the plugin should receive status webhooks", alias="receiveStatusWebhook")
    skip_processing_webhook: Optional[StrictBool] = Field(default=None, description="Whether the plugin should skip processing webhooks. We will just auto-treat it as successful.", alias="skipProcessingWebhook")
    ignore_simulations: Optional[StrictBool] = Field(default=None, description="Ignore simulations?", alias="ignoreSimulations")
    state_function_preset: Optional[Any] = Field(description="Preset type for how the plugin state is to be maintained.", alias="stateFunctionPreset")
    duplicates_allowed: StrictBool = Field(description="Whether it makes sense for multiple of this plugin to be allowed", alias="duplicatesAllowed")
    requires_sessions: StrictBool = Field(description="This means that the plugin can be used w/o any session cookies or authentication.", alias="requiresSessions")
    requires_user_inputs: StrictBool = Field(description="This is a flag for being compatible with auto-triggered claims, meaning no user interaction is needed.", alias="requiresUserInputs")
    user_inputs_schema: List[JsonBodyInputSchema] = Field(alias="userInputsSchema")
    public_params_schema: List[JsonBodyInputSchema] = Field(alias="publicParamsSchema")
    private_params_schema: List[JsonBodyInputSchema] = Field(alias="privateParamsSchema")
    user_input_redirect: Optional[IPluginVersionConfigUserInputRedirect] = Field(default=None, alias="userInputRedirect")
    claim_creator_redirect: Optional[IPluginVersionConfigClaimCreatorRedirect] = Field(default=None, alias="claimCreatorRedirect")
    verification_call: Optional[IPluginVersionConfigVerificationCall] = Field(default=None, alias="verificationCall")
    custom_details_display: Optional[StrictStr] = Field(default=None, description="Custom details display for the plugin. Use {{publicParamKey}} to dynamically display the values of public parameters.  Example: \"This plugin checks for a minimum of {{publicBalanceParam}} balance.\"", alias="customDetailsDisplay")
    require_sign_in: Optional[StrictBool] = Field(default=None, description="Require BitBadges sign-in to use the plugin? This will ensure that any addresss received is actually verified by BitBadges. Otherwise, the address will be the claimee's address but it could be manually entered (if configuration allows).  We recommend keeping this false to allow for non-indexed support and also be more flexible for the claim creator's implementation.", alias="requireSignIn")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["version", "finalized", "createdAt", "lastUpdated", "reuseForNonIndexed", "receiveStatusWebhook", "skipProcessingWebhook", "ignoreSimulations", "stateFunctionPreset", "duplicatesAllowed", "requiresSessions", "requiresUserInputs", "userInputsSchema", "publicParamsSchema", "privateParamsSchema", "userInputRedirect", "claimCreatorRedirect", "verificationCall", "customDetailsDisplay", "requireSignIn"]

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
        """Create an instance of IPluginVersionConfig from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of last_updated
        if self.last_updated:
            _dict['lastUpdated'] = self.last_updated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in user_inputs_schema (list)
        _items = []
        if self.user_inputs_schema:
            for _item_user_inputs_schema in self.user_inputs_schema:
                if _item_user_inputs_schema:
                    _items.append(_item_user_inputs_schema.to_dict())
            _dict['userInputsSchema'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in public_params_schema (list)
        _items = []
        if self.public_params_schema:
            for _item_public_params_schema in self.public_params_schema:
                if _item_public_params_schema:
                    _items.append(_item_public_params_schema.to_dict())
            _dict['publicParamsSchema'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in private_params_schema (list)
        _items = []
        if self.private_params_schema:
            for _item_private_params_schema in self.private_params_schema:
                if _item_private_params_schema:
                    _items.append(_item_private_params_schema.to_dict())
            _dict['privateParamsSchema'] = _items
        # override the default output from pydantic by calling `to_dict()` of user_input_redirect
        if self.user_input_redirect:
            _dict['userInputRedirect'] = self.user_input_redirect.to_dict()
        # override the default output from pydantic by calling `to_dict()` of claim_creator_redirect
        if self.claim_creator_redirect:
            _dict['claimCreatorRedirect'] = self.claim_creator_redirect.to_dict()
        # override the default output from pydantic by calling `to_dict()` of verification_call
        if self.verification_call:
            _dict['verificationCall'] = self.verification_call.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        # set to None if state_function_preset (nullable) is None
        # and model_fields_set contains the field
        if self.state_function_preset is None and "state_function_preset" in self.model_fields_set:
            _dict['stateFunctionPreset'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IPluginVersionConfig from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "version": NumberType.from_dict(obj["version"]) if obj.get("version") is not None else None,
            "finalized": obj.get("finalized"),
            "createdAt": NumberType.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "lastUpdated": NumberType.from_dict(obj["lastUpdated"]) if obj.get("lastUpdated") is not None else None,
            "reuseForNonIndexed": obj.get("reuseForNonIndexed"),
            "receiveStatusWebhook": obj.get("receiveStatusWebhook"),
            "skipProcessingWebhook": obj.get("skipProcessingWebhook"),
            "ignoreSimulations": obj.get("ignoreSimulations"),
            "stateFunctionPreset": obj.get("stateFunctionPreset"),
            "duplicatesAllowed": obj.get("duplicatesAllowed"),
            "requiresSessions": obj.get("requiresSessions"),
            "requiresUserInputs": obj.get("requiresUserInputs"),
            "userInputsSchema": [JsonBodyInputSchema.from_dict(_item) for _item in obj["userInputsSchema"]] if obj.get("userInputsSchema") is not None else None,
            "publicParamsSchema": [JsonBodyInputSchema.from_dict(_item) for _item in obj["publicParamsSchema"]] if obj.get("publicParamsSchema") is not None else None,
            "privateParamsSchema": [JsonBodyInputSchema.from_dict(_item) for _item in obj["privateParamsSchema"]] if obj.get("privateParamsSchema") is not None else None,
            "userInputRedirect": IPluginVersionConfigUserInputRedirect.from_dict(obj["userInputRedirect"]) if obj.get("userInputRedirect") is not None else None,
            "claimCreatorRedirect": IPluginVersionConfigClaimCreatorRedirect.from_dict(obj["claimCreatorRedirect"]) if obj.get("claimCreatorRedirect") is not None else None,
            "verificationCall": IPluginVersionConfigVerificationCall.from_dict(obj["verificationCall"]) if obj.get("verificationCall") is not None else None,
            "customDetailsDisplay": obj.get("customDetailsDisplay"),
            "requireSignIn": obj.get("requireSignIn")
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


