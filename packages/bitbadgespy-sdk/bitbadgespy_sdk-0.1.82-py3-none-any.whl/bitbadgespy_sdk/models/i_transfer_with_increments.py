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
from bitbadgespy_sdk.models.i_approval_identifier_details import IApprovalIdentifierDetails
from bitbadgespy_sdk.models.i_balance import IBalance
from bitbadgespy_sdk.models.i_merkle_proof import IMerkleProof
from bitbadgespy_sdk.models.i_precalculation_options import IPrecalculationOptions
from bitbadgespy_sdk.models.ieth_signature_proof import IETHSignatureProof
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class ITransferWithIncrements(BaseModel):
    """
    ITransferWithIncrements
    """ # noqa: E501
    var_from: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="from")
    to_addresses: List[StrictStr] = Field(description="The addresses to transfer to.", alias="toAddresses")
    balances: List[IBalance] = Field(description="The balances to transfer.")
    precalculate_balances_from_approval: Optional[IApprovalIdentifierDetails] = Field(default=None, description="If specified, we will precalculate from this approval and override the balances. This can only be used when the specified approval has predeterminedBalances set.", alias="precalculateBalancesFromApproval")
    merkle_proofs: Optional[List[IMerkleProof]] = Field(default=None, description="The merkle proofs that satisfy the mkerkle challenges in the approvals. If the transfer deducts from multiple approvals, we check all the merkle proofs and assert at least one is valid for every challenge.", alias="merkleProofs")
    eth_signature_proofs: Optional[List[IETHSignatureProof]] = Field(default=None, description="The ETH signature proofs that satisfy the ETH signature challenges in the approvals. If the transfer deducts from multiple approvals, we check all the ETH signature proofs and assert at least one is valid for every challenge.", alias="ethSignatureProofs")
    memo: Optional[StrictStr] = Field(default=None, description="Arbitrary memo for the transfer.")
    prioritized_approvals: Optional[List[IApprovalIdentifierDetails]] = Field(default=None, description="The prioritized approvals to use for the transfer. If specified, we will check these first.", alias="prioritizedApprovals")
    only_check_prioritized_collection_approvals: Optional[StrictBool] = Field(default=None, description="Whether or not to only check the prioritized approvals. If false, we will check all approvals with any prioritized first.  This only applies to the \"collection\" level approvals specified.", alias="onlyCheckPrioritizedCollectionApprovals")
    only_check_prioritized_incoming_approvals: Optional[StrictBool] = Field(default=None, description="Whether or not to only check the prioritized approvals. If false, we will check all approvals with any prioritized first.  This only applies to the \"incoming\" level approvals specified.", alias="onlyCheckPrioritizedIncomingApprovals")
    only_check_prioritized_outgoing_approvals: Optional[StrictBool] = Field(default=None, description="Whether or not to only check the prioritized approvals. If false, we will check all approvals with any prioritized first.  This only applies to the \"outgoing\" level approvals specified.", alias="onlyCheckPrioritizedOutgoingApprovals")
    precalculation_options: Optional[IPrecalculationOptions] = Field(default=None, description="The precalculation options for the transfer.", alias="precalculationOptions")
    affiliate_address: Optional[StrictStr] = Field(default=None, description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="affiliateAddress")
    num_attempts: Optional[NumberType] = Field(default=None, description="The number of times to attempt approval validation. If 0 / not specified, we default to only one.", alias="numAttempts")
    to_addresses_length: Optional[NumberType] = Field(default=None, description="The number of addresses to send the badges to. This takes priority over toAddresses.length (used when you don't know exact addresses (i.e. you know number of codes)).", alias="toAddressesLength")
    increment_badge_ids_by: Optional[NumberType] = Field(default=None, description="The number to increment the badgeIDs by for each transfer.", alias="incrementBadgeIdsBy")
    increment_ownership_times_by: Optional[NumberType] = Field(default=None, description="The number to increment the ownershipTimes by for each transfer.", alias="incrementOwnershipTimesBy")
    duration_from_timestamp: Optional[NumberType] = Field(default=None, description="The number of unix milliseconds to approve starting from now.", alias="durationFromTimestamp")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["from", "toAddresses", "balances", "precalculateBalancesFromApproval", "merkleProofs", "ethSignatureProofs", "memo", "prioritizedApprovals", "onlyCheckPrioritizedCollectionApprovals", "onlyCheckPrioritizedIncomingApprovals", "onlyCheckPrioritizedOutgoingApprovals", "precalculationOptions", "affiliateAddress", "numAttempts", "toAddressesLength", "incrementBadgeIdsBy", "incrementOwnershipTimesBy", "durationFromTimestamp"]

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
        """Create an instance of ITransferWithIncrements from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in balances (list)
        _items = []
        if self.balances:
            for _item_balances in self.balances:
                if _item_balances:
                    _items.append(_item_balances.to_dict())
            _dict['balances'] = _items
        # override the default output from pydantic by calling `to_dict()` of precalculate_balances_from_approval
        if self.precalculate_balances_from_approval:
            _dict['precalculateBalancesFromApproval'] = self.precalculate_balances_from_approval.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in merkle_proofs (list)
        _items = []
        if self.merkle_proofs:
            for _item_merkle_proofs in self.merkle_proofs:
                if _item_merkle_proofs:
                    _items.append(_item_merkle_proofs.to_dict())
            _dict['merkleProofs'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in eth_signature_proofs (list)
        _items = []
        if self.eth_signature_proofs:
            for _item_eth_signature_proofs in self.eth_signature_proofs:
                if _item_eth_signature_proofs:
                    _items.append(_item_eth_signature_proofs.to_dict())
            _dict['ethSignatureProofs'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in prioritized_approvals (list)
        _items = []
        if self.prioritized_approvals:
            for _item_prioritized_approvals in self.prioritized_approvals:
                if _item_prioritized_approvals:
                    _items.append(_item_prioritized_approvals.to_dict())
            _dict['prioritizedApprovals'] = _items
        # override the default output from pydantic by calling `to_dict()` of precalculation_options
        if self.precalculation_options:
            _dict['precalculationOptions'] = self.precalculation_options.to_dict()
        # override the default output from pydantic by calling `to_dict()` of num_attempts
        if self.num_attempts:
            _dict['numAttempts'] = self.num_attempts.to_dict()
        # override the default output from pydantic by calling `to_dict()` of to_addresses_length
        if self.to_addresses_length:
            _dict['toAddressesLength'] = self.to_addresses_length.to_dict()
        # override the default output from pydantic by calling `to_dict()` of increment_badge_ids_by
        if self.increment_badge_ids_by:
            _dict['incrementBadgeIdsBy'] = self.increment_badge_ids_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of increment_ownership_times_by
        if self.increment_ownership_times_by:
            _dict['incrementOwnershipTimesBy'] = self.increment_ownership_times_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of duration_from_timestamp
        if self.duration_from_timestamp:
            _dict['durationFromTimestamp'] = self.duration_from_timestamp.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ITransferWithIncrements from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "from": obj.get("from"),
            "toAddresses": obj.get("toAddresses"),
            "balances": [IBalance.from_dict(_item) for _item in obj["balances"]] if obj.get("balances") is not None else None,
            "precalculateBalancesFromApproval": IApprovalIdentifierDetails.from_dict(obj["precalculateBalancesFromApproval"]) if obj.get("precalculateBalancesFromApproval") is not None else None,
            "merkleProofs": [IMerkleProof.from_dict(_item) for _item in obj["merkleProofs"]] if obj.get("merkleProofs") is not None else None,
            "ethSignatureProofs": [IETHSignatureProof.from_dict(_item) for _item in obj["ethSignatureProofs"]] if obj.get("ethSignatureProofs") is not None else None,
            "memo": obj.get("memo"),
            "prioritizedApprovals": [IApprovalIdentifierDetails.from_dict(_item) for _item in obj["prioritizedApprovals"]] if obj.get("prioritizedApprovals") is not None else None,
            "onlyCheckPrioritizedCollectionApprovals": obj.get("onlyCheckPrioritizedCollectionApprovals"),
            "onlyCheckPrioritizedIncomingApprovals": obj.get("onlyCheckPrioritizedIncomingApprovals"),
            "onlyCheckPrioritizedOutgoingApprovals": obj.get("onlyCheckPrioritizedOutgoingApprovals"),
            "precalculationOptions": IPrecalculationOptions.from_dict(obj["precalculationOptions"]) if obj.get("precalculationOptions") is not None else None,
            "affiliateAddress": obj.get("affiliateAddress"),
            "numAttempts": NumberType.from_dict(obj["numAttempts"]) if obj.get("numAttempts") is not None else None,
            "toAddressesLength": NumberType.from_dict(obj["toAddressesLength"]) if obj.get("toAddressesLength") is not None else None,
            "incrementBadgeIdsBy": NumberType.from_dict(obj["incrementBadgeIdsBy"]) if obj.get("incrementBadgeIdsBy") is not None else None,
            "incrementOwnershipTimesBy": NumberType.from_dict(obj["incrementOwnershipTimesBy"]) if obj.get("incrementOwnershipTimesBy") is not None else None,
            "durationFromTimestamp": NumberType.from_dict(obj["durationFromTimestamp"]) if obj.get("durationFromTimestamp") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


