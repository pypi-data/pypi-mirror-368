# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital tokens, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Pages** (`manageUtilityPages`)   Create, update, and delete utility pages on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from bitbadgespy_sdk.models.i_bit_badges_collection import IBitBadgesCollection

class TestIBitBadgesCollection(unittest.TestCase):
    """IBitBadgesCollection unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> IBitBadgesCollection:
        """Test IBitBadgesCollection
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `IBitBadgesCollection`
        """
        model = IBitBadgesCollection()
        if include_optional:
            return IBitBadgesCollection(
                doc_id = '',
                id = '',
                collection_id = '',
                collection_metadata_timeline = None,
                badge_metadata_timeline = None,
                balances_type = 'Standard',
                off_chain_balances_metadata_timeline = [
                    bitbadgespy_sdk.models.i_off_chain_balances_metadata_timeline.iOffChainBalancesMetadataTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        off_chain_balances_metadata = bitbadgespy_sdk.models.i_off_chain_balances_metadata.iOffChainBalancesMetadata(
                            uri = '', 
                            custom_data = '', ), )
                    ],
                custom_data_timeline = [
                    bitbadgespy_sdk.models.i_custom_data_timeline.iCustomDataTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        custom_data = '', )
                    ],
                manager_timeline = [
                    bitbadgespy_sdk.models.i_manager_timeline.iManagerTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        manager = '', )
                    ],
                collection_permissions = bitbadgespy_sdk.models.i_collection_permissions.iCollectionPermissions(
                    can_delete_collection = [
                        bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                            permanently_permitted_times = [
                                {
                                    'key' : null
                                    }
                                ], 
                            permanently_forbidden_times = [
                                {
                                    'key' : null
                                    }
                                ], )
                        ], 
                    can_archive_collection = [
                        bitbadgespy_sdk.models.i_timed_update_permission.iTimedUpdatePermission(
                            timeline_times = [
                                
                                ], 
                            permanently_permitted_times = [
                                
                                ], 
                            permanently_forbidden_times = [
                                
                                ], )
                        ], 
                    can_update_off_chain_balances_metadata = [
                        bitbadgespy_sdk.models.i_timed_update_permission.iTimedUpdatePermission(
                            timeline_times = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_standards = [
                        
                        ], 
                    can_update_custom_data = [
                        
                        ], 
                    can_update_manager = [
                        
                        ], 
                    can_update_collection_metadata = [
                        
                        ], 
                    can_update_valid_badge_ids = [
                        bitbadgespy_sdk.models.i_badge_ids_action_permission.iBadgeIdsActionPermission(
                            badge_ids = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_badge_metadata = [
                        bitbadgespy_sdk.models.i_timed_update_with_badge_ids_permission.iTimedUpdateWithBadgeIdsPermission(
                            timeline_times = , 
                            badge_ids = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_collection_approvals = [
                        bitbadgespy_sdk.models.i_collection_approval_permission.iCollectionApprovalPermission(
                            from_list_id = '', 
                            from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                                list_id = '', 
                                addresses = [
                                    ''
                                    ], 
                                whitelist = True, 
                                uri = '', 
                                custom_data = '', 
                                created_by = '', ), 
                            to_list_id = '', 
                            to_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                                list_id = '', 
                                addresses = [
                                    ''
                                    ], 
                                whitelist = True, 
                                uri = '', 
                                custom_data = '', ), 
                            initiated_by_list_id = '', 
                            initiated_by_list = , 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            permanently_permitted_times = [
                                
                                ], 
                            permanently_forbidden_times = [
                                
                                ], )
                        ], ),
                collection_approvals = None,
                standards_timeline = [
                    bitbadgespy_sdk.models.i_standards_timeline.iStandardsTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        standards = [
                            ''
                            ], )
                    ],
                is_archived_timeline = [
                    bitbadgespy_sdk.models.i_is_archived_timeline.iIsArchivedTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        is_archived = True, )
                    ],
                default_balances = bitbadgespy_sdk.models.i_user_balance_store.iUserBalanceStore(
                    balances = [
                        bitbadgespy_sdk.models.i_balance.iBalance(
                            amount = null, 
                            badge_ids = [
                                {
                                    'key' : null
                                    }
                                ], 
                            ownership_times = [
                                {
                                    'key' : null
                                    }
                                ], )
                        ], 
                    incoming_approvals = [
                        bitbadgespy_sdk.models.i_user_incoming_approval.iUserIncomingApproval(
                            from_list_id = '', 
                            from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
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
                                custom_data = '', ), 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            uri = '', 
                            custom_data = '', 
                            approval_criteria = bitbadgespy_sdk.models.i_incoming_approval_criteria.iIncomingApprovalCriteria(
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
                                must_own_badges = [
                                    bitbadgespy_sdk.models.i_must_own_badge.iMustOwnBadge(
                                        collection_id = '', 
                                        amount_range = , 
                                        ownership_times = [
                                            
                                            ], 
                                        badge_ids = [
                                            
                                            ], 
                                        override_with_current_time = True, 
                                        must_satisfy_for_all_assets = True, )
                                    ], 
                                predetermined_balances = bitbadgespy_sdk.models.i_predetermined_balances.iPredeterminedBalances(
                                    manual_balances = [
                                        bitbadgespy_sdk.models.i_manual_balances.iManualBalances(
                                            balances = [
                                                bitbadgespy_sdk.models.i_balance.iBalance(
                                                    amount = null, 
                                                    badge_ids = [
                                                        
                                                        ], 
                                                    ownership_times = [
                                                        
                                                        ], )
                                                ], )
                                        ], 
                                    incremented_balances = bitbadgespy_sdk.models.i_incremented_balances.iIncrementedBalances(
                                        start_balances = [
                                            
                                            ], 
                                        increment_badge_ids_by = null, 
                                        increment_ownership_times_by = null, 
                                        duration_from_timestamp = null, 
                                        allow_override_timestamp = True, 
                                        recurring_ownership_times = bitbadgespy_sdk.models.i_recurring_ownership_times.iRecurringOwnershipTimes(
                                            start_time = null, 
                                            interval_length = null, 
                                            charge_period_length = null, ), 
                                        allow_override_with_any_valid_badge = True, ), 
                                    order_calculation_method = bitbadgespy_sdk.models.i_predetermined_order_calculation_method.iPredeterminedOrderCalculationMethod(
                                        use_overall_num_transfers = True, 
                                        use_per_to_address_num_transfers = True, 
                                        use_per_from_address_num_transfers = True, 
                                        use_per_initiated_by_address_num_transfers = True, 
                                        use_merkle_challenge_leaf_index = True, 
                                        challenge_tracker_id = '', ), ), 
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
                                auto_deletion_options = bitbadgespy_sdk.models.i_auto_deletion_options.iAutoDeletionOptions(
                                    after_one_use = True, 
                                    after_overall_max_num_transfers = True, 
                                    allow_counterparty_purge = True, 
                                    allow_purge_if_expired = True, ), 
                                require_from_equals_initiated_by = True, 
                                require_from_does_not_equal_initiated_by = True, 
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
                            version = null, )
                        ], 
                    outgoing_approvals = [
                        bitbadgespy_sdk.models.i_user_outgoing_approval.iUserOutgoingApproval(
                            to_list_id = '', 
                            to_list = , 
                            initiated_by_list_id = '', 
                            initiated_by_list = , 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            uri = '', 
                            custom_data = '', 
                            version = null, )
                        ], 
                    user_permissions = bitbadgespy_sdk.models.i_user_permissions.iUserPermissions(
                        can_update_outgoing_approvals = [
                            bitbadgespy_sdk.models.i_user_outgoing_approval_permission.iUserOutgoingApprovalPermission(
                                to_list_id = '', 
                                to_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_incoming_approvals = [
                            bitbadgespy_sdk.models.i_user_incoming_approval_permission.iUserIncomingApprovalPermission(
                                from_list_id = '', 
                                from_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_self_initiated_outgoing_transfers = [
                            bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_self_initiated_incoming_transfers = [
                            bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_all_incoming_transfers = [
                            
                            ], ), 
                    auto_approve_self_initiated_outgoing_transfers = True, 
                    auto_approve_self_initiated_incoming_transfers = True, 
                    auto_approve_all_incoming_transfers = True, ),
                created_by = '',
                created_block = None,
                created_timestamp = None,
                update_history = [
                    bitbadgespy_sdk.models.i_update_history.iUpdateHistory(
                        tx_hash = '', 
                        block = null, 
                        block_timestamp = null, 
                        timestamp = null, )
                    ],
                valid_badge_ids = [
                    {
                        'key' : null
                        }
                    ],
                mint_escrow_address = '',
                cosmos_coin_wrapper_paths = None,
                invariants = bitbadgespy_sdk.models.i_collection_invariants.iCollectionInvariants(
                    no_custom_ownership_times = True, ),
                activity = [
                    bitbadgespy_sdk.models.i_transfer_activity_doc.iTransferActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        to = [
                            ''
                            ], 
                        from = '', 
                        balances = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        collection_id = '', 
                        memo = '', 
                        precalculate_balances_from_approval = bitbadgespy_sdk.models.i_approval_identifier_details.iApprovalIdentifierDetails(
                            approval_id = '', 
                            approval_level = '', 
                            approver_address = '', 
                            version = null, ), 
                        prioritized_approvals = [
                            bitbadgespy_sdk.models.i_approval_identifier_details.iApprovalIdentifierDetails(
                                approval_id = '', 
                                approval_level = '', 
                                approver_address = '', 
                                version = null, )
                            ], 
                        initiated_by = '', 
                        tx_hash = '', 
                        precalculation_options = bitbadgespy_sdk.models.i_precalculation_options.iPrecalculationOptions(
                            override_timestamp = null, 
                            badge_ids_override = [
                                
                                ], ), 
                        coin_transfers = [
                            bitbadgespy_sdk.models.i_coin_transfer_item.iCoinTransferItem(
                                from = '', 
                                to = '', 
                                amount = null, 
                                denom = '', 
                                is_protocol_fee = True, )
                            ], 
                        approvals_used = [
                            
                            ], 
                        badge_id = null, 
                        price = null, 
                        volume = null, 
                        denom = '', )
                    ],
                owners = [
                    bitbadgespy_sdk.models.i_balance_doc.iBalanceDoc(
                        balances = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        incoming_approvals = [
                            bitbadgespy_sdk.models.i_user_incoming_approval.iUserIncomingApproval(
                                from_list_id = '', 
                                from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
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
                                    custom_data = '', ), 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                uri = '', 
                                custom_data = '', 
                                approval_criteria = bitbadgespy_sdk.models.i_incoming_approval_criteria.iIncomingApprovalCriteria(
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
                                    must_own_badges = [
                                        bitbadgespy_sdk.models.i_must_own_badge.iMustOwnBadge(
                                            collection_id = '', 
                                            amount_range = , 
                                            ownership_times = [
                                                
                                                ], 
                                            badge_ids = [
                                                
                                                ], 
                                            override_with_current_time = True, 
                                            must_satisfy_for_all_assets = True, )
                                        ], 
                                    predetermined_balances = bitbadgespy_sdk.models.i_predetermined_balances.iPredeterminedBalances(
                                        manual_balances = [
                                            bitbadgespy_sdk.models.i_manual_balances.iManualBalances(
                                                balances = [
                                                    bitbadgespy_sdk.models.i_balance.iBalance(
                                                        amount = null, 
                                                        badge_ids = [
                                                            
                                                            ], 
                                                        ownership_times = [
                                                            
                                                            ], )
                                                    ], )
                                            ], 
                                        incremented_balances = bitbadgespy_sdk.models.i_incremented_balances.iIncrementedBalances(
                                            start_balances = [
                                                
                                                ], 
                                            increment_badge_ids_by = null, 
                                            increment_ownership_times_by = null, 
                                            duration_from_timestamp = null, 
                                            allow_override_timestamp = True, 
                                            recurring_ownership_times = bitbadgespy_sdk.models.i_recurring_ownership_times.iRecurringOwnershipTimes(
                                                start_time = null, 
                                                interval_length = null, 
                                                charge_period_length = null, ), 
                                            allow_override_with_any_valid_badge = True, ), 
                                        order_calculation_method = bitbadgespy_sdk.models.i_predetermined_order_calculation_method.iPredeterminedOrderCalculationMethod(
                                            use_overall_num_transfers = True, 
                                            use_per_to_address_num_transfers = True, 
                                            use_per_from_address_num_transfers = True, 
                                            use_per_initiated_by_address_num_transfers = True, 
                                            use_merkle_challenge_leaf_index = True, 
                                            challenge_tracker_id = '', ), ), 
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
                                    auto_deletion_options = bitbadgespy_sdk.models.i_auto_deletion_options.iAutoDeletionOptions(
                                        after_one_use = True, 
                                        after_overall_max_num_transfers = True, 
                                        allow_counterparty_purge = True, 
                                        allow_purge_if_expired = True, ), 
                                    require_from_equals_initiated_by = True, 
                                    require_from_does_not_equal_initiated_by = True, 
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
                                version = null, )
                            ], 
                        outgoing_approvals = [
                            bitbadgespy_sdk.models.i_user_outgoing_approval.iUserOutgoingApproval(
                                to_list_id = '', 
                                to_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                uri = '', 
                                custom_data = '', 
                                version = null, )
                            ], 
                        user_permissions = bitbadgespy_sdk.models.i_user_permissions.iUserPermissions(
                            can_update_outgoing_approvals = [
                                bitbadgespy_sdk.models.i_user_outgoing_approval_permission.iUserOutgoingApprovalPermission(
                                    to_list_id = '', 
                                    to_list = , 
                                    initiated_by_list_id = '', 
                                    initiated_by_list = , 
                                    transfer_times = [
                                        
                                        ], 
                                    badge_ids = [
                                        
                                        ], 
                                    ownership_times = [
                                        
                                        ], 
                                    approval_id = '', 
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_incoming_approvals = [
                                bitbadgespy_sdk.models.i_user_incoming_approval_permission.iUserIncomingApprovalPermission(
                                    from_list_id = '', 
                                    from_list = , 
                                    initiated_by_list_id = '', 
                                    initiated_by_list = , 
                                    transfer_times = [
                                        
                                        ], 
                                    badge_ids = [
                                        
                                        ], 
                                    ownership_times = [
                                        
                                        ], 
                                    approval_id = '', 
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_self_initiated_outgoing_transfers = [
                                bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_self_initiated_incoming_transfers = [
                                bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_all_incoming_transfers = [
                                
                                ], ), 
                        auto_approve_self_initiated_outgoing_transfers = True, 
                        auto_approve_self_initiated_incoming_transfers = True, 
                        auto_approve_all_incoming_transfers = True, 
                        _doc_id = '', 
                        _id = '', 
                        collection_id = '', 
                        bitbadges_address = '', 
                        on_chain = True, 
                        uri = '', 
                        fetched_at = null, 
                        fetched_at_block = null, 
                        is_permanent = True, 
                        content_hash = '', 
                        update_history = [
                            bitbadgespy_sdk.models.i_update_history.iUpdateHistory(
                                tx_hash = '', 
                                block = null, 
                                block_timestamp = null, 
                                timestamp = , )
                            ], )
                    ],
                challenge_trackers = [
                    bitbadgespy_sdk.models.i_merkle_challenge_tracker_doc.iMerkleChallengeTrackerDoc(
                        _doc_id = '', 
                        _id = '', 
                        collection_id = '', 
                        challenge_tracker_id = '', 
                        approval_id = '', 
                        approval_level = 'collection', 
                        approver_address = '', 
                        used_leaf_indices = [
                            bitbadgespy_sdk.models.i_used_leaf_status.iUsedLeafStatus(
                                leaf_index = null, 
                                used_by = '', )
                            ], )
                    ],
                approval_trackers = [
                    bitbadgespy_sdk.models.i_approval_tracker_doc.iApprovalTrackerDoc(
                        collection_id = '', 
                        approval_id = '', 
                        amount_tracker_id = '', 
                        approval_level = '', 
                        approver_address = '', 
                        tracker_type = '', 
                        approved_address = '', 
                        _doc_id = '', 
                        _id = '', 
                        num_transfers = null, 
                        amounts = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        last_updated_at = null, )
                    ],
                listings = [
                    {
                        'key' : null
                        }
                    ],
                nsfw = bitbadgespy_sdk.models.i_collection_nsfw.iCollectionNSFW(
                    badge_ids = null, 
                    reason = '', ),
                reported = bitbadgespy_sdk.models.i_collection_nsfw.iCollectionNSFW(
                    badge_ids = null, 
                    reason = '', ),
                views = {
                    'key' : bitbadgespy_sdk.models.i_bit_badges_collection_views_value.iBitBadgesCollection_views_value(
                        ids = [
                            ''
                            ], 
                        type = '', 
                        pagination = bitbadgespy_sdk.models.pagination_info.PaginationInfo(
                            bookmark = '', 
                            has_more = True, ), )
                    },
                claims = [
                    {
                        'key' : null
                        }
                    ],
                stats = bitbadgespy_sdk.models.i_collection_stats_doc.iCollectionStatsDoc(
                    _doc_id = '', 
                    _id = '', 
                    overall_volume = [
                        bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                            amount = null, 
                            denom = '', )
                        ], 
                    daily_volume = [
                        bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                            amount = null, 
                            denom = '', )
                        ], 
                    weekly_volume = [
                        
                        ], 
                    monthly_volume = [
                        
                        ], 
                    yearly_volume = [
                        
                        ], 
                    last_updated_at = null, 
                    collection_id = '', 
                    floor_prices = [
                        
                        ], 
                    unique_owners = [
                        bitbadgespy_sdk.models.i_balance.iBalance(
                            amount = null, 
                            badge_ids = [
                                {
                                    'key' : null
                                    }
                                ], 
                            ownership_times = [
                                {
                                    'key' : null
                                    }
                                ], )
                        ], 
                    floor_price_history = [
                        bitbadgespy_sdk.models.i_floor_price_history.iFloorPriceHistory(
                            floor_price = , 
                            updated_at = null, )
                        ], 
                    payout_rewards = [
                        
                        ], ),
                badge_floor_prices = [
                    bitbadgespy_sdk.models.i_badge_floor_price_doc.iBadgeFloorPriceDoc(
                        _doc_id = '', 
                        _id = '', 
                        collection_id = '', 
                        badge_id = null, 
                        floor_prices = [
                            bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                                amount = null, 
                                denom = '', )
                            ], 
                        floor_price_history = [
                            bitbadgespy_sdk.models.i_floor_price_history.iFloorPriceHistory(
                                floor_price = bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                                    amount = null, 
                                    denom = '', ), 
                                updated_at = null, )
                            ], )
                    ]
            )
        else:
            return IBitBadgesCollection(
                doc_id = '',
                collection_id = '',
                collection_metadata_timeline = None,
                badge_metadata_timeline = None,
                balances_type = 'Standard',
                off_chain_balances_metadata_timeline = [
                    bitbadgespy_sdk.models.i_off_chain_balances_metadata_timeline.iOffChainBalancesMetadataTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        off_chain_balances_metadata = bitbadgespy_sdk.models.i_off_chain_balances_metadata.iOffChainBalancesMetadata(
                            uri = '', 
                            custom_data = '', ), )
                    ],
                custom_data_timeline = [
                    bitbadgespy_sdk.models.i_custom_data_timeline.iCustomDataTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        custom_data = '', )
                    ],
                manager_timeline = [
                    bitbadgespy_sdk.models.i_manager_timeline.iManagerTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        manager = '', )
                    ],
                collection_permissions = bitbadgespy_sdk.models.i_collection_permissions.iCollectionPermissions(
                    can_delete_collection = [
                        bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                            permanently_permitted_times = [
                                {
                                    'key' : null
                                    }
                                ], 
                            permanently_forbidden_times = [
                                {
                                    'key' : null
                                    }
                                ], )
                        ], 
                    can_archive_collection = [
                        bitbadgespy_sdk.models.i_timed_update_permission.iTimedUpdatePermission(
                            timeline_times = [
                                
                                ], 
                            permanently_permitted_times = [
                                
                                ], 
                            permanently_forbidden_times = [
                                
                                ], )
                        ], 
                    can_update_off_chain_balances_metadata = [
                        bitbadgespy_sdk.models.i_timed_update_permission.iTimedUpdatePermission(
                            timeline_times = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_standards = [
                        
                        ], 
                    can_update_custom_data = [
                        
                        ], 
                    can_update_manager = [
                        
                        ], 
                    can_update_collection_metadata = [
                        
                        ], 
                    can_update_valid_badge_ids = [
                        bitbadgespy_sdk.models.i_badge_ids_action_permission.iBadgeIdsActionPermission(
                            badge_ids = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_badge_metadata = [
                        bitbadgespy_sdk.models.i_timed_update_with_badge_ids_permission.iTimedUpdateWithBadgeIdsPermission(
                            timeline_times = , 
                            badge_ids = [
                                
                                ], 
                            permanently_permitted_times = , 
                            permanently_forbidden_times = , )
                        ], 
                    can_update_collection_approvals = [
                        bitbadgespy_sdk.models.i_collection_approval_permission.iCollectionApprovalPermission(
                            from_list_id = '', 
                            from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                                list_id = '', 
                                addresses = [
                                    ''
                                    ], 
                                whitelist = True, 
                                uri = '', 
                                custom_data = '', 
                                created_by = '', ), 
                            to_list_id = '', 
                            to_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
                                list_id = '', 
                                addresses = [
                                    ''
                                    ], 
                                whitelist = True, 
                                uri = '', 
                                custom_data = '', ), 
                            initiated_by_list_id = '', 
                            initiated_by_list = , 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            permanently_permitted_times = [
                                
                                ], 
                            permanently_forbidden_times = [
                                
                                ], )
                        ], ),
                collection_approvals = None,
                standards_timeline = [
                    bitbadgespy_sdk.models.i_standards_timeline.iStandardsTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        standards = [
                            ''
                            ], )
                    ],
                is_archived_timeline = [
                    bitbadgespy_sdk.models.i_is_archived_timeline.iIsArchivedTimeline(
                        timeline_times = [
                            {
                                'key' : null
                                }
                            ], 
                        is_archived = True, )
                    ],
                default_balances = bitbadgespy_sdk.models.i_user_balance_store.iUserBalanceStore(
                    balances = [
                        bitbadgespy_sdk.models.i_balance.iBalance(
                            amount = null, 
                            badge_ids = [
                                {
                                    'key' : null
                                    }
                                ], 
                            ownership_times = [
                                {
                                    'key' : null
                                    }
                                ], )
                        ], 
                    incoming_approvals = [
                        bitbadgespy_sdk.models.i_user_incoming_approval.iUserIncomingApproval(
                            from_list_id = '', 
                            from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
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
                                custom_data = '', ), 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            uri = '', 
                            custom_data = '', 
                            approval_criteria = bitbadgespy_sdk.models.i_incoming_approval_criteria.iIncomingApprovalCriteria(
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
                                must_own_badges = [
                                    bitbadgespy_sdk.models.i_must_own_badge.iMustOwnBadge(
                                        collection_id = '', 
                                        amount_range = , 
                                        ownership_times = [
                                            
                                            ], 
                                        badge_ids = [
                                            
                                            ], 
                                        override_with_current_time = True, 
                                        must_satisfy_for_all_assets = True, )
                                    ], 
                                predetermined_balances = bitbadgespy_sdk.models.i_predetermined_balances.iPredeterminedBalances(
                                    manual_balances = [
                                        bitbadgespy_sdk.models.i_manual_balances.iManualBalances(
                                            balances = [
                                                bitbadgespy_sdk.models.i_balance.iBalance(
                                                    amount = null, 
                                                    badge_ids = [
                                                        
                                                        ], 
                                                    ownership_times = [
                                                        
                                                        ], )
                                                ], )
                                        ], 
                                    incremented_balances = bitbadgespy_sdk.models.i_incremented_balances.iIncrementedBalances(
                                        start_balances = [
                                            
                                            ], 
                                        increment_badge_ids_by = null, 
                                        increment_ownership_times_by = null, 
                                        duration_from_timestamp = null, 
                                        allow_override_timestamp = True, 
                                        recurring_ownership_times = bitbadgespy_sdk.models.i_recurring_ownership_times.iRecurringOwnershipTimes(
                                            start_time = null, 
                                            interval_length = null, 
                                            charge_period_length = null, ), 
                                        allow_override_with_any_valid_badge = True, ), 
                                    order_calculation_method = bitbadgespy_sdk.models.i_predetermined_order_calculation_method.iPredeterminedOrderCalculationMethod(
                                        use_overall_num_transfers = True, 
                                        use_per_to_address_num_transfers = True, 
                                        use_per_from_address_num_transfers = True, 
                                        use_per_initiated_by_address_num_transfers = True, 
                                        use_merkle_challenge_leaf_index = True, 
                                        challenge_tracker_id = '', ), ), 
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
                                auto_deletion_options = bitbadgespy_sdk.models.i_auto_deletion_options.iAutoDeletionOptions(
                                    after_one_use = True, 
                                    after_overall_max_num_transfers = True, 
                                    allow_counterparty_purge = True, 
                                    allow_purge_if_expired = True, ), 
                                require_from_equals_initiated_by = True, 
                                require_from_does_not_equal_initiated_by = True, 
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
                            version = null, )
                        ], 
                    outgoing_approvals = [
                        bitbadgespy_sdk.models.i_user_outgoing_approval.iUserOutgoingApproval(
                            to_list_id = '', 
                            to_list = , 
                            initiated_by_list_id = '', 
                            initiated_by_list = , 
                            transfer_times = [
                                
                                ], 
                            badge_ids = [
                                
                                ], 
                            ownership_times = [
                                
                                ], 
                            approval_id = '', 
                            uri = '', 
                            custom_data = '', 
                            version = null, )
                        ], 
                    user_permissions = bitbadgespy_sdk.models.i_user_permissions.iUserPermissions(
                        can_update_outgoing_approvals = [
                            bitbadgespy_sdk.models.i_user_outgoing_approval_permission.iUserOutgoingApprovalPermission(
                                to_list_id = '', 
                                to_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_incoming_approvals = [
                            bitbadgespy_sdk.models.i_user_incoming_approval_permission.iUserIncomingApprovalPermission(
                                from_list_id = '', 
                                from_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_self_initiated_outgoing_transfers = [
                            bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_self_initiated_incoming_transfers = [
                            bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                permanently_permitted_times = [
                                    
                                    ], 
                                permanently_forbidden_times = [
                                    
                                    ], )
                            ], 
                        can_update_auto_approve_all_incoming_transfers = [
                            
                            ], ), 
                    auto_approve_self_initiated_outgoing_transfers = True, 
                    auto_approve_self_initiated_incoming_transfers = True, 
                    auto_approve_all_incoming_transfers = True, ),
                created_by = '',
                created_block = None,
                created_timestamp = None,
                update_history = [
                    bitbadgespy_sdk.models.i_update_history.iUpdateHistory(
                        tx_hash = '', 
                        block = null, 
                        block_timestamp = null, 
                        timestamp = null, )
                    ],
                valid_badge_ids = [
                    {
                        'key' : null
                        }
                    ],
                mint_escrow_address = '',
                cosmos_coin_wrapper_paths = None,
                invariants = bitbadgespy_sdk.models.i_collection_invariants.iCollectionInvariants(
                    no_custom_ownership_times = True, ),
                activity = [
                    bitbadgespy_sdk.models.i_transfer_activity_doc.iTransferActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        to = [
                            ''
                            ], 
                        from = '', 
                        balances = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        collection_id = '', 
                        memo = '', 
                        precalculate_balances_from_approval = bitbadgespy_sdk.models.i_approval_identifier_details.iApprovalIdentifierDetails(
                            approval_id = '', 
                            approval_level = '', 
                            approver_address = '', 
                            version = null, ), 
                        prioritized_approvals = [
                            bitbadgespy_sdk.models.i_approval_identifier_details.iApprovalIdentifierDetails(
                                approval_id = '', 
                                approval_level = '', 
                                approver_address = '', 
                                version = null, )
                            ], 
                        initiated_by = '', 
                        tx_hash = '', 
                        precalculation_options = bitbadgespy_sdk.models.i_precalculation_options.iPrecalculationOptions(
                            override_timestamp = null, 
                            badge_ids_override = [
                                
                                ], ), 
                        coin_transfers = [
                            bitbadgespy_sdk.models.i_coin_transfer_item.iCoinTransferItem(
                                from = '', 
                                to = '', 
                                amount = null, 
                                denom = '', 
                                is_protocol_fee = True, )
                            ], 
                        approvals_used = [
                            
                            ], 
                        badge_id = null, 
                        price = null, 
                        volume = null, 
                        denom = '', )
                    ],
                owners = [
                    bitbadgespy_sdk.models.i_balance_doc.iBalanceDoc(
                        balances = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        incoming_approvals = [
                            bitbadgespy_sdk.models.i_user_incoming_approval.iUserIncomingApproval(
                                from_list_id = '', 
                                from_list = bitbadgespy_sdk.models.i_address_list.iAddressList(
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
                                    custom_data = '', ), 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                uri = '', 
                                custom_data = '', 
                                approval_criteria = bitbadgespy_sdk.models.i_incoming_approval_criteria.iIncomingApprovalCriteria(
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
                                    must_own_badges = [
                                        bitbadgespy_sdk.models.i_must_own_badge.iMustOwnBadge(
                                            collection_id = '', 
                                            amount_range = , 
                                            ownership_times = [
                                                
                                                ], 
                                            badge_ids = [
                                                
                                                ], 
                                            override_with_current_time = True, 
                                            must_satisfy_for_all_assets = True, )
                                        ], 
                                    predetermined_balances = bitbadgespy_sdk.models.i_predetermined_balances.iPredeterminedBalances(
                                        manual_balances = [
                                            bitbadgespy_sdk.models.i_manual_balances.iManualBalances(
                                                balances = [
                                                    bitbadgespy_sdk.models.i_balance.iBalance(
                                                        amount = null, 
                                                        badge_ids = [
                                                            
                                                            ], 
                                                        ownership_times = [
                                                            
                                                            ], )
                                                    ], )
                                            ], 
                                        incremented_balances = bitbadgespy_sdk.models.i_incremented_balances.iIncrementedBalances(
                                            start_balances = [
                                                
                                                ], 
                                            increment_badge_ids_by = null, 
                                            increment_ownership_times_by = null, 
                                            duration_from_timestamp = null, 
                                            allow_override_timestamp = True, 
                                            recurring_ownership_times = bitbadgespy_sdk.models.i_recurring_ownership_times.iRecurringOwnershipTimes(
                                                start_time = null, 
                                                interval_length = null, 
                                                charge_period_length = null, ), 
                                            allow_override_with_any_valid_badge = True, ), 
                                        order_calculation_method = bitbadgespy_sdk.models.i_predetermined_order_calculation_method.iPredeterminedOrderCalculationMethod(
                                            use_overall_num_transfers = True, 
                                            use_per_to_address_num_transfers = True, 
                                            use_per_from_address_num_transfers = True, 
                                            use_per_initiated_by_address_num_transfers = True, 
                                            use_merkle_challenge_leaf_index = True, 
                                            challenge_tracker_id = '', ), ), 
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
                                    auto_deletion_options = bitbadgespy_sdk.models.i_auto_deletion_options.iAutoDeletionOptions(
                                        after_one_use = True, 
                                        after_overall_max_num_transfers = True, 
                                        allow_counterparty_purge = True, 
                                        allow_purge_if_expired = True, ), 
                                    require_from_equals_initiated_by = True, 
                                    require_from_does_not_equal_initiated_by = True, 
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
                                version = null, )
                            ], 
                        outgoing_approvals = [
                            bitbadgespy_sdk.models.i_user_outgoing_approval.iUserOutgoingApproval(
                                to_list_id = '', 
                                to_list = , 
                                initiated_by_list_id = '', 
                                initiated_by_list = , 
                                transfer_times = [
                                    
                                    ], 
                                badge_ids = [
                                    
                                    ], 
                                ownership_times = [
                                    
                                    ], 
                                approval_id = '', 
                                uri = '', 
                                custom_data = '', 
                                version = null, )
                            ], 
                        user_permissions = bitbadgespy_sdk.models.i_user_permissions.iUserPermissions(
                            can_update_outgoing_approvals = [
                                bitbadgespy_sdk.models.i_user_outgoing_approval_permission.iUserOutgoingApprovalPermission(
                                    to_list_id = '', 
                                    to_list = , 
                                    initiated_by_list_id = '', 
                                    initiated_by_list = , 
                                    transfer_times = [
                                        
                                        ], 
                                    badge_ids = [
                                        
                                        ], 
                                    ownership_times = [
                                        
                                        ], 
                                    approval_id = '', 
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_incoming_approvals = [
                                bitbadgespy_sdk.models.i_user_incoming_approval_permission.iUserIncomingApprovalPermission(
                                    from_list_id = '', 
                                    from_list = , 
                                    initiated_by_list_id = '', 
                                    initiated_by_list = , 
                                    transfer_times = [
                                        
                                        ], 
                                    badge_ids = [
                                        
                                        ], 
                                    ownership_times = [
                                        
                                        ], 
                                    approval_id = '', 
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_self_initiated_outgoing_transfers = [
                                bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_self_initiated_incoming_transfers = [
                                bitbadgespy_sdk.models.i_action_permission.iActionPermission(
                                    permanently_permitted_times = [
                                        
                                        ], 
                                    permanently_forbidden_times = [
                                        
                                        ], )
                                ], 
                            can_update_auto_approve_all_incoming_transfers = [
                                
                                ], ), 
                        auto_approve_self_initiated_outgoing_transfers = True, 
                        auto_approve_self_initiated_incoming_transfers = True, 
                        auto_approve_all_incoming_transfers = True, 
                        _doc_id = '', 
                        _id = '', 
                        collection_id = '', 
                        bitbadges_address = '', 
                        on_chain = True, 
                        uri = '', 
                        fetched_at = null, 
                        fetched_at_block = null, 
                        is_permanent = True, 
                        content_hash = '', 
                        update_history = [
                            bitbadgespy_sdk.models.i_update_history.iUpdateHistory(
                                tx_hash = '', 
                                block = null, 
                                block_timestamp = null, 
                                timestamp = , )
                            ], )
                    ],
                challenge_trackers = [
                    bitbadgespy_sdk.models.i_merkle_challenge_tracker_doc.iMerkleChallengeTrackerDoc(
                        _doc_id = '', 
                        _id = '', 
                        collection_id = '', 
                        challenge_tracker_id = '', 
                        approval_id = '', 
                        approval_level = 'collection', 
                        approver_address = '', 
                        used_leaf_indices = [
                            bitbadgespy_sdk.models.i_used_leaf_status.iUsedLeafStatus(
                                leaf_index = null, 
                                used_by = '', )
                            ], )
                    ],
                approval_trackers = [
                    bitbadgespy_sdk.models.i_approval_tracker_doc.iApprovalTrackerDoc(
                        collection_id = '', 
                        approval_id = '', 
                        amount_tracker_id = '', 
                        approval_level = '', 
                        approver_address = '', 
                        tracker_type = '', 
                        approved_address = '', 
                        _doc_id = '', 
                        _id = '', 
                        num_transfers = null, 
                        amounts = [
                            bitbadgespy_sdk.models.i_balance.iBalance(
                                amount = null, 
                                badge_ids = [
                                    {
                                        'key' : null
                                        }
                                    ], 
                                ownership_times = [
                                    {
                                        'key' : null
                                        }
                                    ], )
                            ], 
                        last_updated_at = null, )
                    ],
                listings = [
                    {
                        'key' : null
                        }
                    ],
                views = {
                    'key' : bitbadgespy_sdk.models.i_bit_badges_collection_views_value.iBitBadgesCollection_views_value(
                        ids = [
                            ''
                            ], 
                        type = '', 
                        pagination = bitbadgespy_sdk.models.pagination_info.PaginationInfo(
                            bookmark = '', 
                            has_more = True, ), )
                    },
                claims = [
                    {
                        'key' : null
                        }
                    ],
        )
        """

    def testIBitBadgesCollection(self):
        """Test IBitBadgesCollection"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
