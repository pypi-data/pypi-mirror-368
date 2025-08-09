# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Pages** (`manageUtilityPages`)   Create, update, and delete utility pages on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from bitbadgespy_sdk.models.i_bit_badges_user_info import IBitBadgesUserInfo

class TestIBitBadgesUserInfo(unittest.TestCase):
    """IBitBadgesUserInfo unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> IBitBadgesUserInfo:
        """Test IBitBadgesUserInfo
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `IBitBadgesUserInfo`
        """
        model = IBitBadgesUserInfo()
        if include_optional:
            return IBitBadgesUserInfo(
                doc_id = '',
                id = '',
                public_key = '',
                account_number = None,
                pub_key_type = '',
                bitbadges_address = '',
                eth_address = '',
                btc_address = '',
                thor_address = '',
                sequence = None,
                balances = [
                    bitbadgespy_sdk.models.i_cosmos_coin.iCosmosCoin(
                        amount = null, 
                        denom = '', )
                    ],
                fetched_profile = 'full',
                embedded_wallet_address = '',
                seen_activity = None,
                created_at = None,
                discord = '',
                twitter = '',
                github = '',
                telegram = '',
                bluesky = '',
                readme = '',
                custom_links = [
                    bitbadgespy_sdk.models.i_custom_link.iCustomLink(
                        title = '', 
                        url = '', 
                        image = '', )
                    ],
                hidden_badges = [
                    bitbadgespy_sdk.models.i_batch_badge_details.iBatchBadgeDetails(
                        collection_id = '', 
                        badge_ids = [
                            {
                                'key' : null
                                }
                            ], )
                    ],
                hidden_lists = [
                    ''
                    ],
                custom_pages = bitbadgespy_sdk.models.i_bit_badges_user_info_custom_pages.iBitBadgesUserInfo_customPages(
                    badges = [
                        bitbadgespy_sdk.models.i_custom_page.iCustomPage(
                            title = '', 
                            description = '', 
                            items = [
                                bitbadgespy_sdk.models.i_batch_badge_details.iBatchBadgeDetails(
                                    collection_id = '', 
                                    badge_ids = [
                                        {
                                            'key' : null
                                            }
                                        ], )
                                ], )
                        ], 
                    lists = [
                        bitbadgespy_sdk.models.i_custom_list_page.iCustomListPage(
                            title = '', 
                            description = '', 
                            items = [
                                ''
                                ], )
                        ], ),
                watchlists = bitbadgespy_sdk.models.i_bit_badges_user_info_watchlists.iBitBadgesUserInfo_watchlists(
                    badges = [
                        bitbadgespy_sdk.models.i_custom_page.iCustomPage(
                            title = '', 
                            description = '', 
                            items = [
                                bitbadgespy_sdk.models.i_batch_badge_details.iBatchBadgeDetails(
                                    collection_id = '', 
                                    badge_ids = [
                                        {
                                            'key' : null
                                            }
                                        ], )
                                ], )
                        ], 
                    lists = [
                        bitbadgespy_sdk.models.i_custom_list_page.iCustomListPage(
                            title = '', 
                            description = '', 
                            items = [
                                ''
                                ], )
                        ], ),
                profile_pic_url = '',
                banner_image = '',
                username = '',
                latest_signed_in_chain = 'Bitcoin',
                notifications = {
                    'key' : null
                    },
                social_connections = {
                    'key' : null
                    },
                public_social_connections = {
                    'key' : null
                    },
                approved_sign_in_methods = bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods.iBitBadgesUserInfo_approvedSignInMethods(
                    discord = bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_discord.iBitBadgesUserInfo_approvedSignInMethods_discord(
                        scopes = [
                            bitbadgespy_sdk.models.o_auth_scope_details.OAuthScopeDetails(
                                scope_name = '', 
                                options = bitbadgespy_sdk.models.options.options(), )
                            ], 
                        username = '', 
                        discriminator = '', 
                        id = '', ), 
                    github = bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_github.iBitBadgesUserInfo_approvedSignInMethods_github(
                        scopes = [
                            bitbadgespy_sdk.models.o_auth_scope_details.OAuthScopeDetails(
                                scope_name = '', 
                                options = bitbadgespy_sdk.models.options.options(), )
                            ], 
                        username = '', 
                        id = '', ), 
                    google = bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_google.iBitBadgesUserInfo_approvedSignInMethods_google(
                        scopes = , 
                        username = '', 
                        id = '', ), 
                    twitter = bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_google.iBitBadgesUserInfo_approvedSignInMethods_google(
                        scopes = , 
                        username = '', 
                        id = '', ), 
                    facebook = , 
                    addresses = [
                        bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_addresses_inner.iBitBadgesUserInfo_approvedSignInMethods_addresses_inner(
                            address = '', 
                            scopes = , )
                        ], 
                    passwords = [
                        bitbadgespy_sdk.models.i_bit_badges_user_info_approved_sign_in_methods_passwords_inner.iBitBadgesUserInfo_approvedSignInMethods_passwords_inner(
                            password_hash = '', 
                            salt = '', 
                            scopes = , )
                        ], ),
                resolved_name = '',
                avatar = '',
                sol_address = '',
                chain = 'Bitcoin',
                airdropped = True,
                collected = [
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
                            {
                                'key' : null
                                }
                            ], 
                        outgoing_approvals = [
                            {
                                'key' : null
                                }
                            ], 
                        user_permissions = {
                            'key' : null
                            }, 
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
                list_activity = [
                    bitbadgespy_sdk.models.i_list_activity_doc.iListActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        list_id = '', 
                        initiated_by = '', 
                        added_to_list = True, 
                        addresses = [
                            ''
                            ], 
                        tx_hash = '', )
                    ],
                claim_activity = [
                    bitbadgespy_sdk.models.i_claim_activity_doc.iClaimActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        success = True, 
                        claim_id = '', 
                        claim_attempt_id = '', 
                        bitbadges_address = '', 
                        claim_type = 'standalone', )
                    ],
                points_activity = [
                    bitbadgespy_sdk.models.i_points_activity_doc.iPointsActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        bitbadges_address = '', 
                        old_points = null, 
                        new_points = null, 
                        application_id = '', 
                        page_id = '', )
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
                address_lists = [
                    null
                    ],
                claim_alerts = [
                    bitbadgespy_sdk.models.i_claim_alert_doc.iClaimAlertDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        from = '', 
                        bitbadges_addresses = [
                            ''
                            ], 
                        collection_id = '', 
                        message = '', )
                    ],
                siwbb_requests = [
                    bitbadgespy_sdk.models.i_siwbb_request_doc.iSIWBBRequestDoc(
                        _doc_id = '', 
                        _id = '', 
                        code = '', 
                        bitbadges_address = '', 
                        address = '', 
                        chain = 'Bitcoin', 
                        name = '', 
                        description = '', 
                        image = '', 
                        scopes = [
                            bitbadgespy_sdk.models.o_auth_scope_details.OAuthScopeDetails(
                                scope_name = '', 
                                options = bitbadgespy_sdk.models.options.options(), )
                            ], 
                        expires_at = null, 
                        created_at = null, 
                        deleted_at = , 
                        client_id = '', 
                        redirect_uri = '', 
                        code_challenge = '', 
                        code_challenge_method = 'S256', )
                    ],
                address = '',
                nsfw = bitbadgespy_sdk.models.i_bit_badges_user_info_nsfw.iBitBadgesUserInfo_nsfw(
                    reason = '', ),
                reported = bitbadgespy_sdk.models.i_bit_badges_user_info_reported.iBitBadgesUserInfo_reported(
                    reason = '', ),
                views = {
                    'key' : bitbadgespy_sdk.models.i_bit_badges_user_info_views_value.iBitBadgesUserInfo_views_value(
                        ids = [
                            ''
                            ], 
                        type = '', 
                        pagination = bitbadgespy_sdk.models.pagination_info.PaginationInfo(
                            bookmark = '', 
                            has_more = True, ), )
                    },
                alias = bitbadgespy_sdk.models.i_bit_badges_user_info_alias.iBitBadgesUserInfo_alias(
                    collection_id = '', 
                    list_id = '', ),
                creator_credits = bitbadgespy_sdk.models.i_creator_credits_doc.iCreatorCreditsDoc(
                    _doc_id = '', 
                    _id = '', 
                    credits = null, 
                    credits_limit = null, )
            )
        else:
            return IBitBadgesUserInfo(
                doc_id = '',
                public_key = '',
                account_number = None,
                pub_key_type = '',
                bitbadges_address = '',
                eth_address = '',
                btc_address = '',
                thor_address = '',
                sol_address = '',
                chain = 'Bitcoin',
                collected = [
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
                            {
                                'key' : null
                                }
                            ], 
                        outgoing_approvals = [
                            {
                                'key' : null
                                }
                            ], 
                        user_permissions = {
                            'key' : null
                            }, 
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
                list_activity = [
                    bitbadgespy_sdk.models.i_list_activity_doc.iListActivityDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        list_id = '', 
                        initiated_by = '', 
                        added_to_list = True, 
                        addresses = [
                            ''
                            ], 
                        tx_hash = '', )
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
                address_lists = [
                    null
                    ],
                claim_alerts = [
                    bitbadgespy_sdk.models.i_claim_alert_doc.iClaimAlertDoc(
                        _doc_id = '', 
                        _id = '', 
                        timestamp = null, 
                        block = null, 
                        _notifications_handled = True, 
                        private = True, 
                        from = '', 
                        bitbadges_addresses = [
                            ''
                            ], 
                        collection_id = '', 
                        message = '', )
                    ],
                siwbb_requests = [
                    bitbadgespy_sdk.models.i_siwbb_request_doc.iSIWBBRequestDoc(
                        _doc_id = '', 
                        _id = '', 
                        code = '', 
                        bitbadges_address = '', 
                        address = '', 
                        chain = 'Bitcoin', 
                        name = '', 
                        description = '', 
                        image = '', 
                        scopes = [
                            bitbadgespy_sdk.models.o_auth_scope_details.OAuthScopeDetails(
                                scope_name = '', 
                                options = bitbadgespy_sdk.models.options.options(), )
                            ], 
                        expires_at = null, 
                        created_at = null, 
                        deleted_at = , 
                        client_id = '', 
                        redirect_uri = '', 
                        code_challenge = '', 
                        code_challenge_method = 'S256', )
                    ],
                address = '',
                views = {
                    'key' : bitbadgespy_sdk.models.i_bit_badges_user_info_views_value.iBitBadgesUserInfo_views_value(
                        ids = [
                            ''
                            ], 
                        type = '', 
                        pagination = bitbadgespy_sdk.models.pagination_info.PaginationInfo(
                            bookmark = '', 
                            has_more = True, ), )
                    },
        )
        """

    def testIBitBadgesUserInfo(self):
        """Test IBitBadgesUserInfo"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
