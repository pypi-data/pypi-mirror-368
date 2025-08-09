# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Pages** (`manageUtilityPages`)   Create, update, and delete utility pages on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from bitbadgespy_sdk.models.i_user_outgoing_approval import IUserOutgoingApproval

class TestIUserOutgoingApproval(unittest.TestCase):
    """IUserOutgoingApproval unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> IUserOutgoingApproval:
        """Test IUserOutgoingApproval
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `IUserOutgoingApproval`
        """
        model = IUserOutgoingApproval()
        if include_optional:
            return IUserOutgoingApproval(
                to_list_id = '',
                to_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                    list_id = '', 
                    addresses = [
                        ''
                        ], 
                    whitelist = True, 
                    uri = '', 
                    custom_data = '', 
                    created_by = '', ),
                initiated_by_list_id = '',
                initiated_by_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                    list_id = '', 
                    addresses = [
                        ''
                        ], 
                    whitelist = True, 
                    uri = '', 
                    custom_data = '', 
                    created_by = '', ),
                transfer_times = [
                    {
                        'key' : null
                        }
                    ],
                badge_ids = [
                    {
                        'key' : null
                        }
                    ],
                ownership_times = [
                    {
                        'key' : null
                        }
                    ],
                approval_id = '',
                uri = '',
                custom_data = '',
                approval_criteria = bitbadgespy_sdk.models.i_outgoing_approval_criteria.iOutgoingApprovalCriteria(
                    coin_transfers = [
                        bitbadgespy_sdk.models.i_coin_transfer.iCoinTransfer(
                            to = '', 
                            coins = [
                                bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                                    amount = null, 
                                    denom = '', )
                                ], 
                            override_from_with_approver_address = True, 
                            override_to_with_initiator = True, )
                        ], 
                    must_own_badges = [
                        bitbadgespy_sdk.models.i_must_own_badge.iMustOwnBadge(
                            collection_id = '', 
                            amount_range = {
                                'key' : null
                                }, 
                            ownership_times = [
                                {
                                    'key' : null
                                    }
                                ], 
                            badge_ids = [
                                
                                ], 
                            override_with_current_time = True, 
                            must_satisfy_for_all_assets = True, )
                        ], 
                    merkle_challenges = [
                        bitbadgespy_sdk.models.i_merkle_challenge.iMerkleChallenge(
                            root = '', 
                            expected_proof_length = null, 
                            use_creator_address_as_leaf = True, 
                            max_uses_per_leaf = null, 
                            uri = '', 
                            custom_data = '', 
                            challenge_tracker_id = '', 
                            leaf_signer = '', )
                        ], 
                    predetermined_balances = {
                        'key' : null
                        }, 
                    approval_amounts = bitbadgespy_sdk.models.i_approval_amounts.iApprovalAmounts(
                        overall_approval_amount = null, 
                        per_to_address_approval_amount = null, 
                        per_from_address_approval_amount = null, 
                        per_initiated_by_address_approval_amount = null, 
                        amount_tracker_id = '', 
                        reset_time_intervals = bitbadgespy_sdk.models.i_reset_time_intervals.iResetTimeIntervals(
                            start_time = null, 
                            interval_length = null, ), ), 
                    max_num_transfers = bitbadgespy_sdk.models.i_max_num_transfers.iMaxNumTransfers(
                        overall_max_num_transfers = null, 
                        per_to_address_max_num_transfers = null, 
                        per_from_address_max_num_transfers = null, 
                        per_initiated_by_address_max_num_transfers = null, 
                        amount_tracker_id = '', 
                        reset_time_intervals = bitbadgespy_sdk.models.i_reset_time_intervals.iResetTimeIntervals(
                            start_time = null, 
                            interval_length = null, ), ), 
                    require_to_equals_initiated_by = True, 
                    require_to_does_not_equal_initiated_by = True, 
                    auto_deletion_options = bitbadgespy_sdk.models.i_auto_deletion_options.iAutoDeletionOptions(
                        after_one_use = True, 
                        after_overall_max_num_transfers = True, 
                        allow_counterparty_purge = True, 
                        allow_purge_if_expired = True, ), 
                    dynamic_store_challenges = [
                        bitbadgespy_sdk.models.i_dynamic_store_challenge.iDynamicStoreChallenge(
                            store_id = null, )
                        ], 
                    eth_signature_challenges = [
                        bitbadgespy_sdk.models.i_eth_signature_challenge.iETHSignatureChallenge(
                            signer = '', 
                            challenge_tracker_id = '', 
                            uri = '', 
                            custom_data = '', )
                        ], ),
                version = None
            )
        else:
            return IUserOutgoingApproval(
                to_list_id = '',
                to_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                    list_id = '', 
                    addresses = [
                        ''
                        ], 
                    whitelist = True, 
                    uri = '', 
                    custom_data = '', 
                    created_by = '', ),
                initiated_by_list_id = '',
                initiated_by_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                    list_id = '', 
                    addresses = [
                        ''
                        ], 
                    whitelist = True, 
                    uri = '', 
                    custom_data = '', 
                    created_by = '', ),
                transfer_times = [
                    {
                        'key' : null
                        }
                    ],
                badge_ids = [
                    {
                        'key' : null
                        }
                    ],
                ownership_times = [
                    {
                        'key' : null
                        }
                    ],
                approval_id = '',
                version = None,
        )
        """

    def testIUserOutgoingApproval(self):
        """Test IUserOutgoingApproval"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
