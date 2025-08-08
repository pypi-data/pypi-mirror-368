# bitbadgespy-sdk
# Introduction
The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more.
For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api)
and use along with this reference.

Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).

# Getting Started

## Authentication
All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).

### API Key Authentication
Include your API key in the `x-api-key` header:
```
x-api-key: your-api-key-here
```

<br />

## User Authentication
Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:

### OAuth 2.0 (Sign In with BitBadges)
For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges.
See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.

You will pass the access token in the Authorization header:
```
Authorization: Bearer your-access-token-here
```

### Password Self-Approve Method
For automating actions for your own account:
1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`)
2. Sign in using:
```typescript
const { message } = await BitBadgesApi.getSignInChallenge(...);
const verificationRes = await BitBadgesApi.verifySignIn({
    message,
    signature: '', //Empty string
    password: '...'
})
```

Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).

### Scopes
Note that for proper authentication, you must have the proper scopes set.

See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in
the `scope` parameter of the SIWBB URL or set in your approved sign in settings.

Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this,
contact us.

### Available Scopes

- **Report** (`report`)
  Report users or collections.

- **Read Profile** (`readProfile`)
  Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.

- **Read Address Lists** (`readAddressLists`)
  Read private address lists on behalf of the user.

- **Manage Address Lists** (`manageAddressLists`)
  Create, update, and delete address lists on behalf of the user (private or public).

- **Manage Applications** (`manageApplications`)
  Create, update, and delete applications on behalf of the user.

- **Manage Claims** (`manageClaims`)
  Create, update, and delete claims on behalf of the user.

- **Manage Developer Apps** (`manageDeveloperApps`)
  Create, update, and delete developer apps on behalf of the user.

- **Manage Dynamic Stores** (`manageDynamicStores`)
  Create, update, and delete dynamic stores on behalf of the user.

- **Manage Utility Pages** (`manageUtilityPages`)
  Create, update, and delete utility pages on behalf of the user.

- **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)
  Sign In with BitBadges on behalf of the user.

- **Read Authentication Codes** (`readAuthenticationCodes`)
  Read Authentication Codes on behalf of the user.

- **Delete Authentication Codes** (`deleteAuthenticationCodes`)
  Delete Authentication Codes on behalf of the user.

- **Send Claim Alerts** (`sendClaimAlerts`)
  Send claim alerts on behalf of the user.

- **Read Claim Alerts** (`readClaimAlerts`)
  Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.

- **Read Private Claim Data** (`readPrivateClaimData`)
  Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).

- **Complete Claims** (`completeClaims`)
  Complete claims on behalf of the user.

- **Manage Off-Chain Balances** (`manageOffChainBalances`)
  Manage off-chain balances on behalf of the user.

- **Embedded Wallet** (`embeddedWallet`)
  Sign transactions on behalf of the user with their embedded wallet.

<br />

## SDK Integration
The recommended way to interact with the API is through our TypeScript/JavaScript SDK:

```typescript
import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";

// Initialize the API client
const api = new BitBadgesAPI({
  convertFunction: BigIntify,
  apiKey: 'your-api-key-here'
});

// Example: Fetch collections
const collections = await api.getCollections({
  collectionsToFetch: [{
    collectionId: 1n,
    metadataToFetch: {
      badgeIds: [{ start: 1n, end: 10n }]
    }
  }]
});
```

<br />

# Tiers
There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing
- Free tier
- Premium tier
- Enterprise tier

Rate limit headers included in responses:
- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)

# Response Formats

## Error Response

All API errors follow a consistent format:

```typescript
{
  // Serialized error object for debugging purposes
  // Advanced users can use this to debug issues
  error?: any;

  // UX-friendly error message that can be displayed to the user
  // Always present if error occurs
  errorMessage: string;

  // Authentication error flag
  // Present if the user is not authenticated
  unauthorized?: boolean;
}
```

<br />

## Pagination
Cursor-based pagination is used for list endpoints:
```typescript
{
  items: T[],
  bookmark: string, // Use this for the next page
  hasMore: boolean
}
```

<br />

# Best Practices
1. **Rate Limiting**: Implement proper rate limit handling
2. **Caching**: Cache responses when appropriate
3. **Error Handling**: Handle API errors gracefully
4. **Batch Operations**: Use batch endpoints when possible

# Additional Resources
- [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api)
- [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview)
- [Developer Portal](https://bitbadges.io/developer)
- [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs)
- [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)

# Support
- [Contact Page](https://bitbadges.io/contact)

This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 0.1
- Package version: 0.1.83
- Generator version: 7.12.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import bitbadgespy_sdk
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import bitbadgespy_sdk
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import bitbadgespy_sdk
from bitbadgespy_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.bitbadges.io/api/v0
# See configuration.py for a list of all supported configuration parameters.
configuration = bitbadgespy_sdk.Configuration(
    host = "https://api.bitbadges.io/api/v0"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: apiKey
configuration.api_key['apiKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['apiKey'] = 'Bearer'


# Enter a context with an instance of the API client
with bitbadgespy_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bitbadgespy_sdk.AccountsApi(api_client)
    x_api_key = 'x_api_key_example' # str | BitBadges API Key for authentication
    payload = bitbadgespy_sdk.IGetAccountPayload() # IGetAccountPayload | The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=) (optional)

    try:
        # Get Account
        api_response = api_instance.get_account(x_api_key, payload=payload)
        print("The response of AccountsApi->get_account:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi->get_account: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.bitbadges.io/api/v0*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AccountsApi* | [**get_account**](docs/AccountsApi.md#get_account) | **GET** /user | Get Account
*AccountsApi* | [**get_accounts**](docs/AccountsApi.md#get_accounts) | **POST** /users | Get Accounts - Batch
*AccountsApi* | [**get_address_lists_for_user**](docs/AccountsApi.md#get_address_lists_for_user) | **GET** /account/{address}/lists | Get Address Lists For User
*AccountsApi* | [**get_badges_view_for_user**](docs/AccountsApi.md#get_badges_view_for_user) | **GET** /account/{address}/badges/ | Get Badges For User
*AccountsApi* | [**get_claim_activity_for_user**](docs/AccountsApi.md#get_claim_activity_for_user) | **GET** /account/{address}/activity/claims | Get Claim Activity For User
*AccountsApi* | [**get_claim_alerts_for_user**](docs/AccountsApi.md#get_claim_alerts_for_user) | **GET** /account/{address}/claimAlerts | Get Claim Alerts For User
*AccountsApi* | [**get_list_activity_for_user**](docs/AccountsApi.md#get_list_activity_for_user) | **GET** /account/{address}/activity/lists | Get Lists Activity For User
*AccountsApi* | [**get_points_activity_for_user**](docs/AccountsApi.md#get_points_activity_for_user) | **GET** /account/{address}/activity/points | Get Points Activity For User
*AccountsApi* | [**get_siwbb_requests_for_user**](docs/AccountsApi.md#get_siwbb_requests_for_user) | **GET** /account/{address}/requests/siwbb | Get SIWBB Requests For User
*AccountsApi* | [**get_transfer_activity_for_user**](docs/AccountsApi.md#get_transfer_activity_for_user) | **GET** /account/{address}/activity/badges | Get Transfer Activity For User
*AddressListsApi* | [**create_address_lists**](docs/AddressListsApi.md#create_address_lists) | **POST** /addressLists | Creates Address Lists
*AddressListsApi* | [**delete_address_lists**](docs/AddressListsApi.md#delete_address_lists) | **DELETE** /addressLists | Delete Address Lists
*AddressListsApi* | [**get_address_list**](docs/AddressListsApi.md#get_address_list) | **GET** /addressList/{addressListId} | Get Address List
*AddressListsApi* | [**get_address_list_activity**](docs/AddressListsApi.md#get_address_list_activity) | **GET** /addressLists/{addressListId}/activity | Get Address List Activity
*AddressListsApi* | [**get_address_list_claims**](docs/AddressListsApi.md#get_address_list_claims) | **GET** /addressLists/{addressListId}/claims | Get Address List Claims
*AddressListsApi* | [**get_address_list_listings**](docs/AddressListsApi.md#get_address_list_listings) | **GET** /addressLists/{addressListId}/listings | Get Address List Listings
*AddressListsApi* | [**get_address_lists**](docs/AddressListsApi.md#get_address_lists) | **POST** /addressLists/fetch | Get Address Lists - Batch
*AddressListsApi* | [**update_address_list_addresses**](docs/AddressListsApi.md#update_address_list_addresses) | **PUT** /addressLists/addresses | Update Address List Addresses
*AddressListsApi* | [**update_address_list_core_details**](docs/AddressListsApi.md#update_address_list_core_details) | **PUT** /addressLists/coreDetails | Update Address List Core Details
*ApplicationsApi* | [**calculate_points**](docs/ApplicationsApi.md#calculate_points) | **POST** /applications/points | Calculate Points
*ApplicationsApi* | [**create_application**](docs/ApplicationsApi.md#create_application) | **POST** /applications | Create Application
*ApplicationsApi* | [**delete_application**](docs/ApplicationsApi.md#delete_application) | **DELETE** /applications | Delete Application
*ApplicationsApi* | [**get_application**](docs/ApplicationsApi.md#get_application) | **GET** /application/{applicationId} | Get Application
*ApplicationsApi* | [**get_applications**](docs/ApplicationsApi.md#get_applications) | **POST** /applications/fetch | Get Applications - Batch
*ApplicationsApi* | [**get_points_activity**](docs/ApplicationsApi.md#get_points_activity) | **GET** /applications/points/activity | Get Points Activity
*ApplicationsApi* | [**search_applications**](docs/ApplicationsApi.md#search_applications) | **GET** /applications/search | Search Applications
*ApplicationsApi* | [**update_application**](docs/ApplicationsApi.md#update_application) | **PUT** /applications | Update Application
*BadgesApi* | [**get_badge_activity**](docs/BadgesApi.md#get_badge_activity) | **GET** /collection/{collectionId}/{badgeId}/activity | Get Badge Activity
*BadgesApi* | [**get_badge_balance_by_address**](docs/BadgesApi.md#get_badge_balance_by_address) | **GET** /collection/{collectionId}/balance/{address} | Get Badge Balances By Address
*BadgesApi* | [**get_badge_balance_by_address_specific_badge**](docs/BadgesApi.md#get_badge_balance_by_address_specific_badge) | **GET** /collection/{collectionId}/balance/{address}/{badgeId} | Get Badge Balance By Address - Specific Badge
*BadgesApi* | [**get_badge_metadata**](docs/BadgesApi.md#get_badge_metadata) | **GET** /collection/{collectionId}/{badgeId}/metadata | Get Badge Metadata
*BadgesApi* | [**get_collection**](docs/BadgesApi.md#get_collection) | **GET** /collection/{collectionId} | Get Collection
*BadgesApi* | [**get_collection_amount_tracker_by_id**](docs/BadgesApi.md#get_collection_amount_tracker_by_id) | **GET** /api/v0/collection/amountTracker | Get Collection Amount Tracker By ID
*BadgesApi* | [**get_collection_amount_trackers**](docs/BadgesApi.md#get_collection_amount_trackers) | **GET** /collection/{collectionId}/amountTrackers | Get Collection Amount Trackers
*BadgesApi* | [**get_collection_challenge_tracker_by_id**](docs/BadgesApi.md#get_collection_challenge_tracker_by_id) | **GET** /api/v0/collection/challengeTracker | Get Collection Challenge Tracker By ID
*BadgesApi* | [**get_collection_challenge_trackers**](docs/BadgesApi.md#get_collection_challenge_trackers) | **GET** /collection/{collectionId}/challengeTrackers | Get Collection Challenge Trackers
*BadgesApi* | [**get_collection_claims**](docs/BadgesApi.md#get_collection_claims) | **GET** /collection/{collectionId}/claims | Get Collection Claims
*BadgesApi* | [**get_collection_listings**](docs/BadgesApi.md#get_collection_listings) | **GET** /collection/{collectionId}/listings | Get Collection Listings
*BadgesApi* | [**get_collection_owners**](docs/BadgesApi.md#get_collection_owners) | **GET** /collection/{collectionId}/owners | Get Collection Owners
*BadgesApi* | [**get_collection_transfer_activity**](docs/BadgesApi.md#get_collection_transfer_activity) | **GET** /collection/{collectionId}/activity | Get Collection Transfer Activity
*BadgesApi* | [**get_collections_batch**](docs/BadgesApi.md#get_collections_batch) | **POST** /collections | Get Collections - Batch
*BadgesApi* | [**get_owners_for_badge**](docs/BadgesApi.md#get_owners_for_badge) | **GET** /collection/{collectionId}/{badgeId}/owners | Get Badge Owners
*BadgesApi* | [**get_refresh_status**](docs/BadgesApi.md#get_refresh_status) | **GET** /collection/{collectionId}/refreshStatus | Get Refresh Status
*BadgesApi* | [**upload_balances**](docs/BadgesApi.md#upload_balances) | **POST** /api/v0/uploadBalances | Upload Balances
*ClaimAlertsApi* | [**send_claim_alert**](docs/ClaimAlertsApi.md#send_claim_alert) | **POST** /claimAlerts/send | Sends Claim Alert
*ClaimsApi* | [**check_claim_success**](docs/ClaimsApi.md#check_claim_success) | **GET** /claims/success/{claimId}/{address} | Check Claim Successes By User
*ClaimsApi* | [**complete_claim**](docs/ClaimsApi.md#complete_claim) | **POST** /claims/complete/{claimId}/{address} | Complete Claim
*ClaimsApi* | [**create_claim**](docs/ClaimsApi.md#create_claim) | **POST** /claims | Create Claim
*ClaimsApi* | [**delete_claim**](docs/ClaimsApi.md#delete_claim) | **DELETE** /claims | Delete Claim
*ClaimsApi* | [**generate_code**](docs/ClaimsApi.md#generate_code) | **GET** /codes | Get Code (Codes Plugin)
*ClaimsApi* | [**get_attempt_data_from_request_bin**](docs/ClaimsApi.md#get_attempt_data_from_request_bin) | **GET** /api/v0/requestBin/attemptData/{claimId}/{claimAttemptId} | Get Attempt Data (Request Bin)
*ClaimsApi* | [**get_claim**](docs/ClaimsApi.md#get_claim) | **GET** /claim/{claimId} | Get Claim
*ClaimsApi* | [**get_claim_attempt_status**](docs/ClaimsApi.md#get_claim_attempt_status) | **GET** /claims/status/{claimAttemptId} | Get Claim Attempt Status
*ClaimsApi* | [**get_claim_attempts**](docs/ClaimsApi.md#get_claim_attempts) | **GET** /claims/{claimId}/attempts | Get Claim Attempts
*ClaimsApi* | [**get_claims**](docs/ClaimsApi.md#get_claims) | **POST** /claims/fetch | Get Claims - Batch
*ClaimsApi* | [**get_gated_content_for_claim**](docs/ClaimsApi.md#get_gated_content_for_claim) | **GET** /claims/gatedContent/{claimId} | Get Gated Content for Claim
*ClaimsApi* | [**get_reserved_codes**](docs/ClaimsApi.md#get_reserved_codes) | **POST** /claims/reserved/{claimId}/{address} | Get Reserved Claim Codes
*ClaimsApi* | [**search_claims**](docs/ClaimsApi.md#search_claims) | **GET** /claims/search | Search Claims
*ClaimsApi* | [**simulate_claim**](docs/ClaimsApi.md#simulate_claim) | **POST** /claims/simulate/{claimId}/{address} | Simulate Claim
*ClaimsApi* | [**update_claim**](docs/ClaimsApi.md#update_claim) | **PUT** /claims | Update Claim
*DynamicStoresApi* | [**create_dynamic_data_store**](docs/DynamicStoresApi.md#create_dynamic_data_store) | **POST** /dynamicStores | Create Dynamic Data Store
*DynamicStoresApi* | [**delete_dynamic_data_store**](docs/DynamicStoresApi.md#delete_dynamic_data_store) | **DELETE** /dynamicStores | Delete Dynamic Data Store
*DynamicStoresApi* | [**get_dynamic_data_activity**](docs/DynamicStoresApi.md#get_dynamic_data_activity) | **GET** /dynamicStores/activity | Get Dynamic Data Activity
*DynamicStoresApi* | [**get_dynamic_data_store**](docs/DynamicStoresApi.md#get_dynamic_data_store) | **GET** /dynamicStore/{dynamicStoreId} | Get Dynamic Data Store
*DynamicStoresApi* | [**get_dynamic_data_store_value**](docs/DynamicStoresApi.md#get_dynamic_data_store_value) | **GET** /dynamicStore/{dynamicStoreId}/value | Get Dynamic Data Store Value
*DynamicStoresApi* | [**get_dynamic_data_store_values_paginated**](docs/DynamicStoresApi.md#get_dynamic_data_store_values_paginated) | **GET** /dynamicStore/{dynamicStoreId}/values | Get Dynamic Data Store Values Paginated
*DynamicStoresApi* | [**get_dynamic_data_stores**](docs/DynamicStoresApi.md#get_dynamic_data_stores) | **POST** /dynamicStores/fetch | Fetch Dynamic Data Stores - Batch
*DynamicStoresApi* | [**perform_store_action_batch_with_body_auth**](docs/DynamicStoresApi.md#perform_store_action_batch_with_body_auth) | **POST** /storeActions/batch | Perform Batch Store Actions (Body Auth)
*DynamicStoresApi* | [**perform_store_action_single_with_body_auth**](docs/DynamicStoresApi.md#perform_store_action_single_with_body_auth) | **POST** /storeActions/single | Perform Single Store Action (Body Auth)
*DynamicStoresApi* | [**search_dynamic_data_stores**](docs/DynamicStoresApi.md#search_dynamic_data_stores) | **GET** /dynamicStores/search | Search Dynamic Data Stores For User
*DynamicStoresApi* | [**update_dynamic_data_store**](docs/DynamicStoresApi.md#update_dynamic_data_store) | **PUT** /dynamicStores | Update Dynamic Data Store
*MapsAndProtocolsApi* | [**get_map**](docs/MapsAndProtocolsApi.md#get_map) | **GET** /maps/{mapId} | Get Map
*MapsAndProtocolsApi* | [**get_map_value**](docs/MapsAndProtocolsApi.md#get_map_value) | **GET** /mapValue/{mapId}/{key} | Get Map Value
*MapsAndProtocolsApi* | [**get_map_values**](docs/MapsAndProtocolsApi.md#get_map_values) | **POST** /mapValues | Get Map Values - Batch
*MapsAndProtocolsApi* | [**get_maps**](docs/MapsAndProtocolsApi.md#get_maps) | **POST** /maps | Get Maps - Batch
*MiscellanousApi* | [**get_status**](docs/MiscellanousApi.md#get_status) | **GET** /status | Get Status
*PluginsApi* | [**get_plugin**](docs/PluginsApi.md#get_plugin) | **GET** /plugin/{pluginId} | Get Plugin
*PluginsApi* | [**get_plugins**](docs/PluginsApi.md#get_plugins) | **POST** /plugins/fetch | Get Plugins - Batch
*PluginsApi* | [**search_plugins**](docs/PluginsApi.md#search_plugins) | **GET** /plugins/search | Search Plugins
*SignInWithBitBadgesApi* | [**check_sign_in_status**](docs/SignInWithBitBadgesApi.md#check_sign_in_status) | **POST** /auth/status | Check Sign In Status
*SignInWithBitBadgesApi* | [**create_developer_app**](docs/SignInWithBitBadgesApi.md#create_developer_app) | **POST** /developerApps | Create OAuth App
*SignInWithBitBadgesApi* | [**create_siwbb_request**](docs/SignInWithBitBadgesApi.md#create_siwbb_request) | **POST** /siwbbRequest | Create SIWBB Request
*SignInWithBitBadgesApi* | [**delete_developer_app**](docs/SignInWithBitBadgesApi.md#delete_developer_app) | **DELETE** /developerApps | Delete OAuth App
*SignInWithBitBadgesApi* | [**delete_siwbb_request**](docs/SignInWithBitBadgesApi.md#delete_siwbb_request) | **DELETE** /siwbbRequest | Delete SIWBB Request
*SignInWithBitBadgesApi* | [**exchange_siwbb_authorization_code**](docs/SignInWithBitBadgesApi.md#exchange_siwbb_authorization_code) | **POST** /siwbb/token | Exchange SIWBB Code
*SignInWithBitBadgesApi* | [**generate_apple_wallet_pass**](docs/SignInWithBitBadgesApi.md#generate_apple_wallet_pass) | **POST** /siwbbRequest/appleWalletPass | Generate Apple Wallet Pass
*SignInWithBitBadgesApi* | [**generate_google_wallet_pass**](docs/SignInWithBitBadgesApi.md#generate_google_wallet_pass) | **POST** /siwbbRequest/googleWalletPass | Generate Google Wallet Pass
*SignInWithBitBadgesApi* | [**get_developer_app**](docs/SignInWithBitBadgesApi.md#get_developer_app) | **GET** /developerApp/{clientId} | Get OAuth App
*SignInWithBitBadgesApi* | [**get_siwbb_requests_for_developer_app**](docs/SignInWithBitBadgesApi.md#get_siwbb_requests_for_developer_app) | **GET** /developerApps/siwbbRequests | Get SIWBB Requests For Developer App
*SignInWithBitBadgesApi* | [**revoke_oauth_authorization**](docs/SignInWithBitBadgesApi.md#revoke_oauth_authorization) | **POST** /siwbb/token/revoke | Revoke Authorization
*SignInWithBitBadgesApi* | [**rotate_siwbb_request**](docs/SignInWithBitBadgesApi.md#rotate_siwbb_request) | **POST** /siwbbRequest/rotate | Rotate SIWBB Request
*SignInWithBitBadgesApi* | [**update_developer_app**](docs/SignInWithBitBadgesApi.md#update_developer_app) | **PUT** /developerApps | Update OAuth App
*TransactionsApi* | [**broadcast_tx**](docs/TransactionsApi.md#broadcast_tx) | **POST** /broadcast | Broadcast Transaction
*TransactionsApi* | [**simulate_tx**](docs/TransactionsApi.md#simulate_tx) | **POST** /simulate | Simulate Transaction
*UtilityPagesApi* | [**create_utility_page**](docs/UtilityPagesApi.md#create_utility_page) | **POST** /utilityPages | Create Utility Page
*UtilityPagesApi* | [**delete_utility_page**](docs/UtilityPagesApi.md#delete_utility_page) | **DELETE** /utilityPages | Delete Utility Page
*UtilityPagesApi* | [**get_utility_page**](docs/UtilityPagesApi.md#get_utility_page) | **GET** /utilityPage/{utilityPageId} | Get Utility Page
*UtilityPagesApi* | [**get_utility_pages**](docs/UtilityPagesApi.md#get_utility_pages) | **POST** /utilityPages/fetch | Get Utility Pages - Batch
*UtilityPagesApi* | [**search_utility_pages**](docs/UtilityPagesApi.md#search_utility_pages) | **GET** /utilityPages/search | Search Utility Pages
*UtilityPagesApi* | [**update_utility_page**](docs/UtilityPagesApi.md#update_utility_page) | **PUT** /utilityPages | Update Utility Page


## Documentation For Models

 - [AccountFetchDetails](docs/AccountFetchDetails.md)
 - [AccountFetchDetailsViewsToFetchInner](docs/AccountFetchDetailsViewsToFetchInner.md)
 - [AccountResponse](docs/AccountResponse.md)
 - [AccountResponseAccount](docs/AccountResponseAccount.md)
 - [AccountResponseAccountBaseAccount](docs/AccountResponseAccountBaseAccount.md)
 - [AccountResponseAccountBaseAccountPubKey](docs/AccountResponseAccountBaseAccountPubKey.md)
 - [AccountViewKey](docs/AccountViewKey.md)
 - [AdditionalQueryParams](docs/AdditionalQueryParams.md)
 - [AddressListViewKey](docs/AddressListViewKey.md)
 - [AminoConverter](docs/AminoConverter.md)
 - [AminoMsg](docs/AminoMsg.md)
 - [AndGroup](docs/AndGroup.md)
 - [AssetConditionGroup](docs/AssetConditionGroup.md)
 - [AssetDetails](docs/AssetDetails.md)
 - [AssetDetailsAssetIdsInner](docs/AssetDetailsAssetIdsInner.md)
 - [Attribute](docs/Attribute.md)
 - [BroadcastPostBody](docs/BroadcastPostBody.md)
 - [BroadcastTxRequest](docs/BroadcastTxRequest.md)
 - [Chain](docs/Chain.md)
 - [ChallengeParams](docs/ChallengeParams.md)
 - [Channel](docs/Channel.md)
 - [ChannelsResponse](docs/ChannelsResponse.md)
 - [ChannelsResponseHeight](docs/ChannelsResponseHeight.md)
 - [ChannelsResponsePagination](docs/ChannelsResponsePagination.md)
 - [CodeGenQueryParams](docs/CodeGenQueryParams.md)
 - [CollectionViewKey](docs/CollectionViewKey.md)
 - [ConvertOptions](docs/ConvertOptions.md)
 - [CosmosAccountResponse](docs/CosmosAccountResponse.md)
 - [CosmosAccountResponsePubKey](docs/CosmosAccountResponsePubKey.md)
 - [CosmosEvent](docs/CosmosEvent.md)
 - [CounterParty](docs/CounterParty.md)
 - [CreateClaimRequest](docs/CreateClaimRequest.md)
 - [CreateClaimRequestMetadata](docs/CreateClaimRequestMetadata.md)
 - [DeliverTxResponse](docs/DeliverTxResponse.md)
 - [DeliverTxResponseMsgResponsesInner](docs/DeliverTxResponseMsgResponsesInner.md)
 - [Doc](docs/Doc.md)
 - [DynamicDataHandlerActionRequest](docs/DynamicDataHandlerActionRequest.md)
 - [DynamicDataHandlerType](docs/DynamicDataHandlerType.md)
 - [EIP712ToSign](docs/EIP712ToSign.md)
 - [EIP712ToSignDomain](docs/EIP712ToSignDomain.md)
 - [EncodeObject](docs/EncodeObject.md)
 - [ErrorDoc](docs/ErrorDoc.md)
 - [ErrorResponse](docs/ErrorResponse.md)
 - [Fee](docs/Fee.md)
 - [GenerateCode200Response](docs/GenerateCode200Response.md)
 - [GetAdditionalCollectionDetailsPayload](docs/GetAdditionalCollectionDetailsPayload.md)
 - [GetAdditionalCollectionDetailsPayloadViewsToFetchInner](docs/GetAdditionalCollectionDetailsPayloadViewsToFetchInner.md)
 - [GetCollectionRequestBody](docs/GetCollectionRequestBody.md)
 - [GetCollectionRequestBodyViewsToFetchInner](docs/GetCollectionRequestBodyViewsToFetchInner.md)
 - [GetMetadataForCollectionPayload](docs/GetMetadataForCollectionPayload.md)
 - [GetMetadataForCollectionPayloadBadgeFloorPricesToFetch](docs/GetMetadataForCollectionPayloadBadgeFloorPricesToFetch.md)
 - [GetUndelegationsResponse](docs/GetUndelegationsResponse.md)
 - [GetUndelegationsResponsePagination](docs/GetUndelegationsResponsePagination.md)
 - [GetValidatorsResponse](docs/GetValidatorsResponse.md)
 - [GetValidatorsResponsePagination](docs/GetValidatorsResponsePagination.md)
 - [IAccessTokenDoc](docs/IAccessTokenDoc.md)
 - [IAccountDoc](docs/IAccountDoc.md)
 - [IActionPermission](docs/IActionPermission.md)
 - [IActivityDoc](docs/IActivityDoc.md)
 - [IAddApprovalDetailsToOffChainStoragePayload](docs/IAddApprovalDetailsToOffChainStoragePayload.md)
 - [IAddApprovalDetailsToOffChainStoragePayloadApprovalDetailsInner](docs/IAddApprovalDetailsToOffChainStoragePayloadApprovalDetailsInner.md)
 - [IAddApprovalDetailsToOffChainStorageSuccessResponse](docs/IAddApprovalDetailsToOffChainStorageSuccessResponse.md)
 - [IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInner](docs/IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInner.md)
 - [IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInnerChallengeResultsInner](docs/IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInnerChallengeResultsInner.md)
 - [IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInnerMetadataResult](docs/IAddApprovalDetailsToOffChainStorageSuccessResponseApprovalResultsInnerMetadataResult.md)
 - [IAddBalancesToOffChainStoragePayload](docs/IAddBalancesToOffChainStoragePayload.md)
 - [IAddBalancesToOffChainStoragePayloadClaimsInner](docs/IAddBalancesToOffChainStoragePayloadClaimsInner.md)
 - [IAddBalancesToOffChainStorageSuccessResponse](docs/IAddBalancesToOffChainStorageSuccessResponse.md)
 - [IAddToIpfsPayload](docs/IAddToIpfsPayload.md)
 - [IAddToIpfsPayloadContentsInner](docs/IAddToIpfsPayloadContentsInner.md)
 - [IAddToIpfsSuccessResponse](docs/IAddToIpfsSuccessResponse.md)
 - [IAddToIpfsSuccessResponseResultsInner](docs/IAddToIpfsSuccessResponseResultsInner.md)
 - [IAddressList](docs/IAddressList.md)
 - [IAddressListCreateObject](docs/IAddressListCreateObject.md)
 - [IAddressListDoc](docs/IAddressListDoc.md)
 - [IAddressListDocNsfw](docs/IAddressListDocNsfw.md)
 - [IAddressListDocReported](docs/IAddressListDocReported.md)
 - [IAddressListEditKey](docs/IAddressListEditKey.md)
 - [IAirdropDoc](docs/IAirdropDoc.md)
 - [IAmountTrackerIdDetails](docs/IAmountTrackerIdDetails.md)
 - [IApiKeyDoc](docs/IApiKeyDoc.md)
 - [IApplicationDoc](docs/IApplicationDoc.md)
 - [IApplicationPage](docs/IApplicationPage.md)
 - [IApprovalAmounts](docs/IApprovalAmounts.md)
 - [IApprovalCriteria](docs/IApprovalCriteria.md)
 - [IApprovalIdentifierDetails](docs/IApprovalIdentifierDetails.md)
 - [IApprovalInfoDetails](docs/IApprovalInfoDetails.md)
 - [IApprovalItemDoc](docs/IApprovalItemDoc.md)
 - [IApprovalTrackerDoc](docs/IApprovalTrackerDoc.md)
 - [IAutoDeletionOptions](docs/IAutoDeletionOptions.md)
 - [IBadgeFloorPriceDoc](docs/IBadgeFloorPriceDoc.md)
 - [IBadgeIdsActionPermission](docs/IBadgeIdsActionPermission.md)
 - [IBadgeMetadata](docs/IBadgeMetadata.md)
 - [IBadgeMetadataDetails](docs/IBadgeMetadataDetails.md)
 - [IBadgeMetadataTimeline](docs/IBadgeMetadataTimeline.md)
 - [IBalance](docs/IBalance.md)
 - [IBalanceDoc](docs/IBalanceDoc.md)
 - [IBaseQueryParams](docs/IBaseQueryParams.md)
 - [IBaseStats](docs/IBaseStats.md)
 - [IBaseSuccessResponse](docs/IBaseSuccessResponse.md)
 - [IBatchBadgeDetails](docs/IBatchBadgeDetails.md)
 - [IBitBadgesCollection](docs/IBitBadgesCollection.md)
 - [IBitBadgesCollectionViewsValue](docs/IBitBadgesCollectionViewsValue.md)
 - [IBitBadgesUserInfo](docs/IBitBadgesUserInfo.md)
 - [IBitBadgesUserInfoAlias](docs/IBitBadgesUserInfoAlias.md)
 - [IBitBadgesUserInfoApprovedSignInMethods](docs/IBitBadgesUserInfoApprovedSignInMethods.md)
 - [IBitBadgesUserInfoApprovedSignInMethodsAddressesInner](docs/IBitBadgesUserInfoApprovedSignInMethodsAddressesInner.md)
 - [IBitBadgesUserInfoApprovedSignInMethodsDiscord](docs/IBitBadgesUserInfoApprovedSignInMethodsDiscord.md)
 - [IBitBadgesUserInfoApprovedSignInMethodsGithub](docs/IBitBadgesUserInfoApprovedSignInMethodsGithub.md)
 - [IBitBadgesUserInfoApprovedSignInMethodsGoogle](docs/IBitBadgesUserInfoApprovedSignInMethodsGoogle.md)
 - [IBitBadgesUserInfoApprovedSignInMethodsPasswordsInner](docs/IBitBadgesUserInfoApprovedSignInMethodsPasswordsInner.md)
 - [IBitBadgesUserInfoCustomPages](docs/IBitBadgesUserInfoCustomPages.md)
 - [IBitBadgesUserInfoNsfw](docs/IBitBadgesUserInfoNsfw.md)
 - [IBitBadgesUserInfoReported](docs/IBitBadgesUserInfoReported.md)
 - [IBitBadgesUserInfoViewsValue](docs/IBitBadgesUserInfoViewsValue.md)
 - [IBitBadgesUserInfoWatchlists](docs/IBitBadgesUserInfoWatchlists.md)
 - [IBroadcastTxSuccessResponse](docs/IBroadcastTxSuccessResponse.md)
 - [IBroadcastTxSuccessResponseTxResponse](docs/IBroadcastTxSuccessResponseTxResponse.md)
 - [IBroadcastTxSuccessResponseTxResponseEventsInner](docs/IBroadcastTxSuccessResponseTxResponseEventsInner.md)
 - [IBroadcastTxSuccessResponseTxResponseEventsInnerAttributesInner](docs/IBroadcastTxSuccessResponseTxResponseEventsInnerAttributesInner.md)
 - [IBroadcastTxSuccessResponseTxResponseLogsInner](docs/IBroadcastTxSuccessResponseTxResponseLogsInner.md)
 - [IBroadcastTxSuccessResponseTxResponseLogsInnerEventsInner](docs/IBroadcastTxSuccessResponseTxResponseLogsInnerEventsInner.md)
 - [IBroadcastTxSuccessResponseTxResponseLogsInnerEventsInnerAttributesInner](docs/IBroadcastTxSuccessResponseTxResponseLogsInnerEventsInnerAttributesInner.md)
 - [ICalculatePointsPayload](docs/ICalculatePointsPayload.md)
 - [ICalculatePointsSuccessResponse](docs/ICalculatePointsSuccessResponse.md)
 - [IChallengeDetails](docs/IChallengeDetails.md)
 - [IChallengeInfoDetails](docs/IChallengeInfoDetails.md)
 - [IChallengeInfoDetailsUpdate](docs/IChallengeInfoDetailsUpdate.md)
 - [IChallengeTrackerIdDetails](docs/IChallengeTrackerIdDetails.md)
 - [ICheckClaimSuccessSuccessResponse](docs/ICheckClaimSuccessSuccessResponse.md)
 - [ICheckSignInStatusSuccessResponse](docs/ICheckSignInStatusSuccessResponse.md)
 - [ICheckSignInStatusSuccessResponseBluesky](docs/ICheckSignInStatusSuccessResponseBluesky.md)
 - [ICheckSignInStatusSuccessResponseDiscord](docs/ICheckSignInStatusSuccessResponseDiscord.md)
 - [ICheckSignInStatusSuccessResponseFacebook](docs/ICheckSignInStatusSuccessResponseFacebook.md)
 - [ICheckSignInStatusSuccessResponseFarcaster](docs/ICheckSignInStatusSuccessResponseFarcaster.md)
 - [ICheckSignInStatusSuccessResponseGithub](docs/ICheckSignInStatusSuccessResponseGithub.md)
 - [ICheckSignInStatusSuccessResponseGoogle](docs/ICheckSignInStatusSuccessResponseGoogle.md)
 - [ICheckSignInStatusSuccessResponseGoogleCalendar](docs/ICheckSignInStatusSuccessResponseGoogleCalendar.md)
 - [ICheckSignInStatusSuccessResponseLinkedIn](docs/ICheckSignInStatusSuccessResponseLinkedIn.md)
 - [ICheckSignInStatusSuccessResponseMailchimp](docs/ICheckSignInStatusSuccessResponseMailchimp.md)
 - [ICheckSignInStatusSuccessResponseMeetup](docs/ICheckSignInStatusSuccessResponseMeetup.md)
 - [ICheckSignInStatusSuccessResponseReddit](docs/ICheckSignInStatusSuccessResponseReddit.md)
 - [ICheckSignInStatusSuccessResponseShopify](docs/ICheckSignInStatusSuccessResponseShopify.md)
 - [ICheckSignInStatusSuccessResponseSlack](docs/ICheckSignInStatusSuccessResponseSlack.md)
 - [ICheckSignInStatusSuccessResponseStrava](docs/ICheckSignInStatusSuccessResponseStrava.md)
 - [ICheckSignInStatusSuccessResponseTelegram](docs/ICheckSignInStatusSuccessResponseTelegram.md)
 - [ICheckSignInStatusSuccessResponseTwitch](docs/ICheckSignInStatusSuccessResponseTwitch.md)
 - [ICheckSignInStatusSuccessResponseTwitter](docs/ICheckSignInStatusSuccessResponseTwitter.md)
 - [ICheckSignInStatusSuccessResponseYoutube](docs/ICheckSignInStatusSuccessResponseYoutube.md)
 - [IClaimActivityDoc](docs/IClaimActivityDoc.md)
 - [IClaimAlertDoc](docs/IClaimAlertDoc.md)
 - [IClaimAttempt](docs/IClaimAttempt.md)
 - [IClaimBuilderDoc](docs/IClaimBuilderDoc.md)
 - [IClaimBuilderDocAction](docs/IClaimBuilderDocAction.md)
 - [IClaimCachePolicy](docs/IClaimCachePolicy.md)
 - [IClaimDetails](docs/IClaimDetails.md)
 - [IClaimDetailsTemplateInfo](docs/IClaimDetailsTemplateInfo.md)
 - [IClaimGatedContent](docs/IClaimGatedContent.md)
 - [IClaimReward](docs/IClaimReward.md)
 - [IClaimRewardCalculationMethod](docs/IClaimRewardCalculationMethod.md)
 - [IClaimRewardMetadata](docs/IClaimRewardMetadata.md)
 - [ICoinTransfer](docs/ICoinTransfer.md)
 - [ICoinTransferItem](docs/ICoinTransferItem.md)
 - [ICollectionApproval](docs/ICollectionApproval.md)
 - [ICollectionApprovalPermission](docs/ICollectionApprovalPermission.md)
 - [ICollectionDoc](docs/ICollectionDoc.md)
 - [ICollectionInvariants](docs/ICollectionInvariants.md)
 - [ICollectionMetadata](docs/ICollectionMetadata.md)
 - [ICollectionMetadataDetails](docs/ICollectionMetadataDetails.md)
 - [ICollectionMetadataTimeline](docs/ICollectionMetadataTimeline.md)
 - [ICollectionNSFW](docs/ICollectionNSFW.md)
 - [ICollectionPermissions](docs/ICollectionPermissions.md)
 - [ICollectionStatsDoc](docs/ICollectionStatsDoc.md)
 - [ICompleteClaimPayload](docs/ICompleteClaimPayload.md)
 - [ICompleteClaimSuccessResponse](docs/ICompleteClaimSuccessResponse.md)
 - [IComplianceDoc](docs/IComplianceDoc.md)
 - [IComplianceDocAccounts](docs/IComplianceDocAccounts.md)
 - [IComplianceDocAccountsNsfwInner](docs/IComplianceDocAccountsNsfwInner.md)
 - [IComplianceDocAddressLists](docs/IComplianceDocAddressLists.md)
 - [IComplianceDocAddressListsNsfwInner](docs/IComplianceDocAddressListsNsfwInner.md)
 - [IComplianceDocApplications](docs/IComplianceDocApplications.md)
 - [IComplianceDocApplicationsNsfwInner](docs/IComplianceDocApplicationsNsfwInner.md)
 - [IComplianceDocBadges](docs/IComplianceDocBadges.md)
 - [IComplianceDocClaims](docs/IComplianceDocClaims.md)
 - [IComplianceDocClaimsNsfwInner](docs/IComplianceDocClaimsNsfwInner.md)
 - [IComplianceDocMaps](docs/IComplianceDocMaps.md)
 - [IComplianceDocMapsNsfwInner](docs/IComplianceDocMapsNsfwInner.md)
 - [ICosmosCoin](docs/ICosmosCoin.md)
 - [ICosmosCoinWrapperPath](docs/ICosmosCoinWrapperPath.md)
 - [ICosmosCoinWrapperPathAddObject](docs/ICosmosCoinWrapperPathAddObject.md)
 - [ICreateAddressListsPayload](docs/ICreateAddressListsPayload.md)
 - [ICreateApiKeyPayload](docs/ICreateApiKeyPayload.md)
 - [ICreateApiKeySuccessResponse](docs/ICreateApiKeySuccessResponse.md)
 - [ICreateApplicationPayload](docs/ICreateApplicationPayload.md)
 - [ICreateApplicationSuccessResponse](docs/ICreateApplicationSuccessResponse.md)
 - [ICreateClaimPayload](docs/ICreateClaimPayload.md)
 - [ICreateDeveloperAppPayload](docs/ICreateDeveloperAppPayload.md)
 - [ICreateDeveloperAppSuccessResponse](docs/ICreateDeveloperAppSuccessResponse.md)
 - [ICreateDynamicDataStorePayload](docs/ICreateDynamicDataStorePayload.md)
 - [ICreateDynamicDataStoreSuccessResponse](docs/ICreateDynamicDataStoreSuccessResponse.md)
 - [ICreatePaymentIntentPayload](docs/ICreatePaymentIntentPayload.md)
 - [ICreatePaymentIntentSuccessResponse](docs/ICreatePaymentIntentSuccessResponse.md)
 - [ICreatePluginPayload](docs/ICreatePluginPayload.md)
 - [ICreatePluginPayloadMetadata](docs/ICreatePluginPayloadMetadata.md)
 - [ICreateSIWBBRequestPayload](docs/ICreateSIWBBRequestPayload.md)
 - [ICreateSIWBBRequestSuccessResponse](docs/ICreateSIWBBRequestSuccessResponse.md)
 - [ICreateUtilityPagePayload](docs/ICreateUtilityPagePayload.md)
 - [ICreateUtilityPageSuccessResponse](docs/ICreateUtilityPageSuccessResponse.md)
 - [ICreatorCreditsDoc](docs/ICreatorCreditsDoc.md)
 - [ICustomDataTimeline](docs/ICustomDataTimeline.md)
 - [ICustomLink](docs/ICustomLink.md)
 - [ICustomListPage](docs/ICustomListPage.md)
 - [ICustomPage](docs/ICustomPage.md)
 - [IDeleteAddressListsPayload](docs/IDeleteAddressListsPayload.md)
 - [IDeleteApiKeyPayload](docs/IDeleteApiKeyPayload.md)
 - [IDeleteApplicationPayload](docs/IDeleteApplicationPayload.md)
 - [IDeleteClaimPayload](docs/IDeleteClaimPayload.md)
 - [IDeleteConnectedAccountSuccessResponse](docs/IDeleteConnectedAccountSuccessResponse.md)
 - [IDeleteDeveloperAppPayload](docs/IDeleteDeveloperAppPayload.md)
 - [IDeleteDynamicDataStorePayload](docs/IDeleteDynamicDataStorePayload.md)
 - [IDeleteDynamicDataStoreSuccessResponse](docs/IDeleteDynamicDataStoreSuccessResponse.md)
 - [IDeletePluginPayload](docs/IDeletePluginPayload.md)
 - [IDeleteSIWBBRequestPayload](docs/IDeleteSIWBBRequestPayload.md)
 - [IDeleteUtilityPagePayload](docs/IDeleteUtilityPagePayload.md)
 - [IDenomUnit](docs/IDenomUnit.md)
 - [IDepositBalanceDoc](docs/IDepositBalanceDoc.md)
 - [IDeveloperAppDoc](docs/IDeveloperAppDoc.md)
 - [IDynamicDataDoc](docs/IDynamicDataDoc.md)
 - [IDynamicStoreChallenge](docs/IDynamicStoreChallenge.md)
 - [IETHSignatureChallenge](docs/IETHSignatureChallenge.md)
 - [IETHSignatureProof](docs/IETHSignatureProof.md)
 - [IEmailVerificationStatus](docs/IEmailVerificationStatus.md)
 - [IEstimatedCost](docs/IEstimatedCost.md)
 - [IEvent](docs/IEvent.md)
 - [IExchangeSIWBBAuthorizationCodePayload](docs/IExchangeSIWBBAuthorizationCodePayload.md)
 - [IExchangeSIWBBAuthorizationCodeSuccessResponse](docs/IExchangeSIWBBAuthorizationCodeSuccessResponse.md)
 - [IExchangeSIWBBAuthorizationCodeSuccessResponseVerificationResponse](docs/IExchangeSIWBBAuthorizationCodeSuccessResponseVerificationResponse.md)
 - [IFetchDoc](docs/IFetchDoc.md)
 - [IFetchDocContent](docs/IFetchDocContent.md)
 - [IFetchMetadataDirectlyPayload](docs/IFetchMetadataDirectlyPayload.md)
 - [IFetchMetadataDirectlySuccessResponse](docs/IFetchMetadataDirectlySuccessResponse.md)
 - [IFilterBadgesInCollectionPayload](docs/IFilterBadgesInCollectionPayload.md)
 - [IFilterBadgesInCollectionPayloadAttributesInner](docs/IFilterBadgesInCollectionPayloadAttributesInner.md)
 - [IFilterBadgesInCollectionSuccessResponse](docs/IFilterBadgesInCollectionSuccessResponse.md)
 - [IFilterSuggestionsSuccessResponse](docs/IFilterSuggestionsSuccessResponse.md)
 - [IFilterSuggestionsSuccessResponseAttributesInner](docs/IFilterSuggestionsSuccessResponseAttributesInner.md)
 - [IFloorPriceHistory](docs/IFloorPriceHistory.md)
 - [IGenerateAppleWalletPassPayload](docs/IGenerateAppleWalletPassPayload.md)
 - [IGenerateAppleWalletPassSuccessResponse](docs/IGenerateAppleWalletPassSuccessResponse.md)
 - [IGenerateGoogleWalletPayload](docs/IGenerateGoogleWalletPayload.md)
 - [IGenerateGoogleWalletSuccessResponse](docs/IGenerateGoogleWalletSuccessResponse.md)
 - [IGenericBlockinVerifyPayload](docs/IGenericBlockinVerifyPayload.md)
 - [IGenericVerifyAssetsPayload](docs/IGenericVerifyAssetsPayload.md)
 - [IGenericVerifyAssetsSuccessResponse](docs/IGenericVerifyAssetsSuccessResponse.md)
 - [IGetAccountPayload](docs/IGetAccountPayload.md)
 - [IGetAccountSuccessResponse](docs/IGetAccountSuccessResponse.md)
 - [IGetAccountsPayload](docs/IGetAccountsPayload.md)
 - [IGetAccountsSuccessResponse](docs/IGetAccountsSuccessResponse.md)
 - [IGetActiveAuthorizationsSuccessResponse](docs/IGetActiveAuthorizationsSuccessResponse.md)
 - [IGetAddressListActivityPayload](docs/IGetAddressListActivityPayload.md)
 - [IGetAddressListActivitySuccessResponse](docs/IGetAddressListActivitySuccessResponse.md)
 - [IGetAddressListClaimsSuccessResponse](docs/IGetAddressListClaimsSuccessResponse.md)
 - [IGetAddressListListingsPayload](docs/IGetAddressListListingsPayload.md)
 - [IGetAddressListListingsSuccessResponse](docs/IGetAddressListListingsSuccessResponse.md)
 - [IGetAddressListSuccessResponse](docs/IGetAddressListSuccessResponse.md)
 - [IGetAddressListsForUserPayload](docs/IGetAddressListsForUserPayload.md)
 - [IGetAddressListsForUserSuccessResponse](docs/IGetAddressListsForUserSuccessResponse.md)
 - [IGetAddressListsPayload](docs/IGetAddressListsPayload.md)
 - [IGetAddressListsPayloadListsToFetchInner](docs/IGetAddressListsPayloadListsToFetchInner.md)
 - [IGetAddressListsPayloadListsToFetchInnerViewsToFetchInner](docs/IGetAddressListsPayloadListsToFetchInnerViewsToFetchInner.md)
 - [IGetAddressListsSuccessResponse](docs/IGetAddressListsSuccessResponse.md)
 - [IGetApiKeysPayload](docs/IGetApiKeysPayload.md)
 - [IGetApiKeysSuccessResponse](docs/IGetApiKeysSuccessResponse.md)
 - [IGetApiKeysSuccessResponsePagination](docs/IGetApiKeysSuccessResponsePagination.md)
 - [IGetApplicationSuccessResponse](docs/IGetApplicationSuccessResponse.md)
 - [IGetApplicationsPayload](docs/IGetApplicationsPayload.md)
 - [IGetApplicationsSuccessResponse](docs/IGetApplicationsSuccessResponse.md)
 - [IGetAttemptDataFromRequestBinPayload](docs/IGetAttemptDataFromRequestBinPayload.md)
 - [IGetAttemptDataFromRequestBinSuccessResponse](docs/IGetAttemptDataFromRequestBinSuccessResponse.md)
 - [IGetBadgeActivityPayload](docs/IGetBadgeActivityPayload.md)
 - [IGetBadgeActivitySuccessResponse](docs/IGetBadgeActivitySuccessResponse.md)
 - [IGetBadgeBalanceByAddressPayload](docs/IGetBadgeBalanceByAddressPayload.md)
 - [IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse](docs/IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse.md)
 - [IGetBadgeBalanceByAddressSuccessResponse](docs/IGetBadgeBalanceByAddressSuccessResponse.md)
 - [IGetBadgeMetadataSuccessResponse](docs/IGetBadgeMetadataSuccessResponse.md)
 - [IGetBadgesViewForUserPayload](docs/IGetBadgesViewForUserPayload.md)
 - [IGetBadgesViewForUserSuccessResponse](docs/IGetBadgesViewForUserSuccessResponse.md)
 - [IGetBrowsePayload](docs/IGetBrowsePayload.md)
 - [IGetBrowseSuccessResponse](docs/IGetBrowseSuccessResponse.md)
 - [IGetClaimActivityForUserPayload](docs/IGetClaimActivityForUserPayload.md)
 - [IGetClaimActivityForUserSuccessResponse](docs/IGetClaimActivityForUserSuccessResponse.md)
 - [IGetClaimAlertsForUserPayload](docs/IGetClaimAlertsForUserPayload.md)
 - [IGetClaimAlertsForUserSuccessResponse](docs/IGetClaimAlertsForUserSuccessResponse.md)
 - [IGetClaimAttemptStatusSuccessResponse](docs/IGetClaimAttemptStatusSuccessResponse.md)
 - [IGetClaimAttemptsPayload](docs/IGetClaimAttemptsPayload.md)
 - [IGetClaimAttemptsSuccessResponse](docs/IGetClaimAttemptsSuccessResponse.md)
 - [IGetClaimAttemptsSuccessResponseDocsInner](docs/IGetClaimAttemptsSuccessResponseDocsInner.md)
 - [IGetClaimPayload](docs/IGetClaimPayload.md)
 - [IGetClaimSuccessResponse](docs/IGetClaimSuccessResponse.md)
 - [IGetClaimsPayload](docs/IGetClaimsPayload.md)
 - [IGetClaimsPayloadPrivateStatesToFetchInner](docs/IGetClaimsPayloadPrivateStatesToFetchInner.md)
 - [IGetClaimsPayloadV1](docs/IGetClaimsPayloadV1.md)
 - [IGetClaimsPayloadV1ClaimsToFetchInner](docs/IGetClaimsPayloadV1ClaimsToFetchInner.md)
 - [IGetClaimsSuccessResponse](docs/IGetClaimsSuccessResponse.md)
 - [IGetCollectionAmountTrackerByIdSuccessResponse](docs/IGetCollectionAmountTrackerByIdSuccessResponse.md)
 - [IGetCollectionAmountTrackersPayload](docs/IGetCollectionAmountTrackersPayload.md)
 - [IGetCollectionAmountTrackersSuccessResponse](docs/IGetCollectionAmountTrackersSuccessResponse.md)
 - [IGetCollectionChallengeTrackerByIdSuccessResponse](docs/IGetCollectionChallengeTrackerByIdSuccessResponse.md)
 - [IGetCollectionChallengeTrackersPayload](docs/IGetCollectionChallengeTrackersPayload.md)
 - [IGetCollectionChallengeTrackersSuccessResponse](docs/IGetCollectionChallengeTrackersSuccessResponse.md)
 - [IGetCollectionClaimsSuccessResponse](docs/IGetCollectionClaimsSuccessResponse.md)
 - [IGetCollectionListingsPayload](docs/IGetCollectionListingsPayload.md)
 - [IGetCollectionListingsSuccessResponse](docs/IGetCollectionListingsSuccessResponse.md)
 - [IGetCollectionOwnersPayload](docs/IGetCollectionOwnersPayload.md)
 - [IGetCollectionOwnersSuccessResponse](docs/IGetCollectionOwnersSuccessResponse.md)
 - [IGetCollectionSuccessResponse](docs/IGetCollectionSuccessResponse.md)
 - [IGetCollectionTransferActivityPayload](docs/IGetCollectionTransferActivityPayload.md)
 - [IGetCollectionTransferActivitySuccessResponse](docs/IGetCollectionTransferActivitySuccessResponse.md)
 - [IGetCollectionsPayload](docs/IGetCollectionsPayload.md)
 - [IGetCollectionsSuccessResponse](docs/IGetCollectionsSuccessResponse.md)
 - [IGetConnectedAccountsSuccessResponse](docs/IGetConnectedAccountsSuccessResponse.md)
 - [IGetConnectedAccountsSuccessResponseAccountsInner](docs/IGetConnectedAccountsSuccessResponseAccountsInner.md)
 - [IGetDeveloperAppSuccessResponse](docs/IGetDeveloperAppSuccessResponse.md)
 - [IGetDeveloperAppsPayload](docs/IGetDeveloperAppsPayload.md)
 - [IGetDeveloperAppsSuccessResponse](docs/IGetDeveloperAppsSuccessResponse.md)
 - [IGetDynamicDataActivityPayload](docs/IGetDynamicDataActivityPayload.md)
 - [IGetDynamicDataActivitySuccessResponse](docs/IGetDynamicDataActivitySuccessResponse.md)
 - [IGetDynamicDataActivitySuccessResponseHistory](docs/IGetDynamicDataActivitySuccessResponseHistory.md)
 - [IGetDynamicDataActivitySuccessResponseHistoryDocsInner](docs/IGetDynamicDataActivitySuccessResponseHistoryDocsInner.md)
 - [IGetDynamicDataActivitySuccessResponseHistoryPagination](docs/IGetDynamicDataActivitySuccessResponseHistoryPagination.md)
 - [IGetDynamicDataActivitySuccessResponsePendingInner](docs/IGetDynamicDataActivitySuccessResponsePendingInner.md)
 - [IGetDynamicDataStorePayload](docs/IGetDynamicDataStorePayload.md)
 - [IGetDynamicDataStoreSuccessResponse](docs/IGetDynamicDataStoreSuccessResponse.md)
 - [IGetDynamicDataStoreValuePayload](docs/IGetDynamicDataStoreValuePayload.md)
 - [IGetDynamicDataStoreValueSuccessResponse](docs/IGetDynamicDataStoreValueSuccessResponse.md)
 - [IGetDynamicDataStoreValuesPaginatedPayload](docs/IGetDynamicDataStoreValuesPaginatedPayload.md)
 - [IGetDynamicDataStoreValuesPaginatedSuccessResponse](docs/IGetDynamicDataStoreValuesPaginatedSuccessResponse.md)
 - [IGetDynamicDataStoreValuesPaginatedSuccessResponseLookupValuesInner](docs/IGetDynamicDataStoreValuesPaginatedSuccessResponseLookupValuesInner.md)
 - [IGetDynamicDataStoresPayload](docs/IGetDynamicDataStoresPayload.md)
 - [IGetDynamicDataStoresSuccessResponse](docs/IGetDynamicDataStoresSuccessResponse.md)
 - [IGetDynamicDataStoresSuccessResponsePagination](docs/IGetDynamicDataStoresSuccessResponsePagination.md)
 - [IGetGatedContentForClaimSuccessResponse](docs/IGetGatedContentForClaimSuccessResponse.md)
 - [IGetListActivityForUserPayload](docs/IGetListActivityForUserPayload.md)
 - [IGetListActivityForUserSuccessResponse](docs/IGetListActivityForUserSuccessResponse.md)
 - [IGetMapSuccessResponse](docs/IGetMapSuccessResponse.md)
 - [IGetMapValueSuccessResponse](docs/IGetMapValueSuccessResponse.md)
 - [IGetMapValuesPayload](docs/IGetMapValuesPayload.md)
 - [IGetMapValuesSuccessResponse](docs/IGetMapValuesSuccessResponse.md)
 - [IGetMapValuesSuccessResponseValuesInner](docs/IGetMapValuesSuccessResponseValuesInner.md)
 - [IGetMapsPayload](docs/IGetMapsPayload.md)
 - [IGetMapsSuccessResponse](docs/IGetMapsSuccessResponse.md)
 - [IGetOrCreateEmbeddedWalletSuccessResponse](docs/IGetOrCreateEmbeddedWalletSuccessResponse.md)
 - [IGetOwnersForBadgePayload](docs/IGetOwnersForBadgePayload.md)
 - [IGetOwnersForBadgeSuccessResponse](docs/IGetOwnersForBadgeSuccessResponse.md)
 - [IGetPluginErrorsPayload](docs/IGetPluginErrorsPayload.md)
 - [IGetPluginErrorsSuccessResponse](docs/IGetPluginErrorsSuccessResponse.md)
 - [IGetPluginSuccessResponse](docs/IGetPluginSuccessResponse.md)
 - [IGetPluginsPayload](docs/IGetPluginsPayload.md)
 - [IGetPluginsSuccessResponse](docs/IGetPluginsSuccessResponse.md)
 - [IGetPointsActivityForUserPayload](docs/IGetPointsActivityForUserPayload.md)
 - [IGetPointsActivityForUserSuccessResponse](docs/IGetPointsActivityForUserSuccessResponse.md)
 - [IGetPointsActivityPayload](docs/IGetPointsActivityPayload.md)
 - [IGetPointsActivitySuccessResponse](docs/IGetPointsActivitySuccessResponse.md)
 - [IGetPostActionStatusesSuccessResponse](docs/IGetPostActionStatusesSuccessResponse.md)
 - [IGetPostActionStatusesSuccessResponsePostActionStatusesInner](docs/IGetPostActionStatusesSuccessResponsePostActionStatusesInner.md)
 - [IGetReservedClaimCodesSuccessResponse](docs/IGetReservedClaimCodesSuccessResponse.md)
 - [IGetSIWBBRequestsForDeveloperAppPayload](docs/IGetSIWBBRequestsForDeveloperAppPayload.md)
 - [IGetSIWBBRequestsForDeveloperAppSuccessResponse](docs/IGetSIWBBRequestsForDeveloperAppSuccessResponse.md)
 - [IGetSearchPayload](docs/IGetSearchPayload.md)
 - [IGetSearchSuccessResponse](docs/IGetSearchSuccessResponse.md)
 - [IGetSearchSuccessResponseBadgesInner](docs/IGetSearchSuccessResponseBadgesInner.md)
 - [IGetSignInChallengePayload](docs/IGetSignInChallengePayload.md)
 - [IGetSignInChallengeSuccessResponse](docs/IGetSignInChallengeSuccessResponse.md)
 - [IGetSiwbbRequestsForUserPayload](docs/IGetSiwbbRequestsForUserPayload.md)
 - [IGetSiwbbRequestsForUserSuccessResponse](docs/IGetSiwbbRequestsForUserSuccessResponse.md)
 - [IGetStatusPayload](docs/IGetStatusPayload.md)
 - [IGetStatusSuccessResponse](docs/IGetStatusSuccessResponse.md)
 - [IGetTransferActivityForUserPayload](docs/IGetTransferActivityForUserPayload.md)
 - [IGetTransferActivityForUserSuccessResponse](docs/IGetTransferActivityForUserSuccessResponse.md)
 - [IGetUtilityPageSuccessResponse](docs/IGetUtilityPageSuccessResponse.md)
 - [IGetUtilityPagesPayload](docs/IGetUtilityPagesPayload.md)
 - [IGetUtilityPagesSuccessResponse](docs/IGetUtilityPagesSuccessResponse.md)
 - [IIPFSTotalsDoc](docs/IIPFSTotalsDoc.md)
 - [IIncomingApprovalCriteria](docs/IIncomingApprovalCriteria.md)
 - [IIncrementedBalances](docs/IIncrementedBalances.md)
 - [IIndexerStatus](docs/IIndexerStatus.md)
 - [IInheritMetadataFrom](docs/IInheritMetadataFrom.md)
 - [IIsArchivedTimeline](docs/IIsArchivedTimeline.md)
 - [ILatestBlockStatus](docs/ILatestBlockStatus.md)
 - [ILinkedTo](docs/ILinkedTo.md)
 - [IListActivityDoc](docs/IListActivityDoc.md)
 - [IListingViewsDoc](docs/IListingViewsDoc.md)
 - [IListingViewsDocViewsByPeriod](docs/IListingViewsDocViewsByPeriod.md)
 - [IManagerTimeline](docs/IManagerTimeline.md)
 - [IManualBalances](docs/IManualBalances.md)
 - [IMap](docs/IMap.md)
 - [IMapDoc](docs/IMapDoc.md)
 - [IMapMetadataTimeline](docs/IMapMetadataTimeline.md)
 - [IMapPermissions](docs/IMapPermissions.md)
 - [IMapUpdateCriteria](docs/IMapUpdateCriteria.md)
 - [IMapWithValues](docs/IMapWithValues.md)
 - [IMaxNumTransfers](docs/IMaxNumTransfers.md)
 - [IMerkleChallenge](docs/IMerkleChallenge.md)
 - [IMerkleChallengeTrackerDoc](docs/IMerkleChallengeTrackerDoc.md)
 - [IMerklePathItem](docs/IMerklePathItem.md)
 - [IMerkleProof](docs/IMerkleProof.md)
 - [IMetadata](docs/IMetadata.md)
 - [IMetadataAdditionalInfoInner](docs/IMetadataAdditionalInfoInner.md)
 - [IMetadataAttributesInner](docs/IMetadataAttributesInner.md)
 - [IMetadataAttributesInnerValue](docs/IMetadataAttributesInnerValue.md)
 - [IMetadataOffChainTransferabilityInfo](docs/IMetadataOffChainTransferabilityInfo.md)
 - [IMetadataWithoutInternals](docs/IMetadataWithoutInternals.md)
 - [IMsgCreateAddressLists](docs/IMsgCreateAddressLists.md)
 - [IMsgCreateCollection](docs/IMsgCreateCollection.md)
 - [IMsgCreateDynamicStore](docs/IMsgCreateDynamicStore.md)
 - [IMsgCreateMap](docs/IMsgCreateMap.md)
 - [IMsgDecrementStoreValue](docs/IMsgDecrementStoreValue.md)
 - [IMsgDeleteCollection](docs/IMsgDeleteCollection.md)
 - [IMsgDeleteDynamicStore](docs/IMsgDeleteDynamicStore.md)
 - [IMsgDeleteIncomingApproval](docs/IMsgDeleteIncomingApproval.md)
 - [IMsgDeleteMap](docs/IMsgDeleteMap.md)
 - [IMsgDeleteOutgoingApproval](docs/IMsgDeleteOutgoingApproval.md)
 - [IMsgExecuteContractCompat](docs/IMsgExecuteContractCompat.md)
 - [IMsgIncrementStoreValue](docs/IMsgIncrementStoreValue.md)
 - [IMsgInstantiateContractCompat](docs/IMsgInstantiateContractCompat.md)
 - [IMsgPurgeApprovals](docs/IMsgPurgeApprovals.md)
 - [IMsgSetBadgeMetadata](docs/IMsgSetBadgeMetadata.md)
 - [IMsgSetCollectionApprovals](docs/IMsgSetCollectionApprovals.md)
 - [IMsgSetCollectionMetadata](docs/IMsgSetCollectionMetadata.md)
 - [IMsgSetCustomData](docs/IMsgSetCustomData.md)
 - [IMsgSetDynamicStoreValue](docs/IMsgSetDynamicStoreValue.md)
 - [IMsgSetIncomingApproval](docs/IMsgSetIncomingApproval.md)
 - [IMsgSetIsArchived](docs/IMsgSetIsArchived.md)
 - [IMsgSetManager](docs/IMsgSetManager.md)
 - [IMsgSetOutgoingApproval](docs/IMsgSetOutgoingApproval.md)
 - [IMsgSetStandards](docs/IMsgSetStandards.md)
 - [IMsgSetValidBadgeIds](docs/IMsgSetValidBadgeIds.md)
 - [IMsgSetValue](docs/IMsgSetValue.md)
 - [IMsgStoreCodeCompat](docs/IMsgStoreCodeCompat.md)
 - [IMsgTransferBadges](docs/IMsgTransferBadges.md)
 - [IMsgUniversalUpdateCollection](docs/IMsgUniversalUpdateCollection.md)
 - [IMsgUpdateDynamicStore](docs/IMsgUpdateDynamicStore.md)
 - [IMsgUpdateMap](docs/IMsgUpdateMap.md)
 - [IMsgUpdateUserApprovals](docs/IMsgUpdateUserApprovals.md)
 - [IMustOwnBadge](docs/IMustOwnBadge.md)
 - [IMustOwnBadges](docs/IMustOwnBadges.md)
 - [INotificationPreferences](docs/INotificationPreferences.md)
 - [INotificationPreferencesDiscord](docs/INotificationPreferencesDiscord.md)
 - [INotificationPreferencesPreferences](docs/INotificationPreferencesPreferences.md)
 - [IOauthRevokePayload](docs/IOauthRevokePayload.md)
 - [IOffChainBalancesMetadata](docs/IOffChainBalancesMetadata.md)
 - [IOffChainBalancesMetadataTimeline](docs/IOffChainBalancesMetadataTimeline.md)
 - [IOutgoingApprovalCriteria](docs/IOutgoingApprovalCriteria.md)
 - [IPerformStoreActionBatchWithBodyAuthPayload](docs/IPerformStoreActionBatchWithBodyAuthPayload.md)
 - [IPerformStoreActionBatchWithBodyAuthPayloadActionsInner](docs/IPerformStoreActionBatchWithBodyAuthPayloadActionsInner.md)
 - [IPerformStoreActionSingleWithBodyAuthPayload](docs/IPerformStoreActionSingleWithBodyAuthPayload.md)
 - [IPluginDoc](docs/IPluginDoc.md)
 - [IPluginDocMetadata](docs/IPluginDocMetadata.md)
 - [IPluginVersionConfig](docs/IPluginVersionConfig.md)
 - [IPluginVersionConfigClaimCreatorRedirect](docs/IPluginVersionConfigClaimCreatorRedirect.md)
 - [IPluginVersionConfigUserInputRedirect](docs/IPluginVersionConfigUserInputRedirect.md)
 - [IPluginVersionConfigVerificationCall](docs/IPluginVersionConfigVerificationCall.md)
 - [IPointsActivityDoc](docs/IPointsActivityDoc.md)
 - [IPointsDoc](docs/IPointsDoc.md)
 - [IPointsValue](docs/IPointsValue.md)
 - [IPrecalculationOptions](docs/IPrecalculationOptions.md)
 - [IPredeterminedBalances](docs/IPredeterminedBalances.md)
 - [IPredeterminedOrderCalculationMethod](docs/IPredeterminedOrderCalculationMethod.md)
 - [IProfileDoc](docs/IProfileDoc.md)
 - [IProfileDocApprovedSignInMethods](docs/IProfileDocApprovedSignInMethods.md)
 - [IProfileDocApprovedSignInMethodsAddressesInner](docs/IProfileDocApprovedSignInMethodsAddressesInner.md)
 - [IProfileDocApprovedSignInMethodsDiscord](docs/IProfileDocApprovedSignInMethodsDiscord.md)
 - [IProfileDocApprovedSignInMethodsGithub](docs/IProfileDocApprovedSignInMethodsGithub.md)
 - [IProfileDocApprovedSignInMethodsPasswordsInner](docs/IProfileDocApprovedSignInMethodsPasswordsInner.md)
 - [IProfileDocCustomPages](docs/IProfileDocCustomPages.md)
 - [IProfileDocWatchlists](docs/IProfileDocWatchlists.md)
 - [IQueueDoc](docs/IQueueDoc.md)
 - [IQueueDocClaimInfo](docs/IQueueDocClaimInfo.md)
 - [IQueueDocFaucetInfo](docs/IQueueDocFaucetInfo.md)
 - [IRecurringOwnershipTimes](docs/IRecurringOwnershipTimes.md)
 - [IRefreshDoc](docs/IRefreshDoc.md)
 - [IRefreshStatusSuccessResponse](docs/IRefreshStatusSuccessResponse.md)
 - [IResetTimeIntervals](docs/IResetTimeIntervals.md)
 - [IReviewDoc](docs/IReviewDoc.md)
 - [IRotateApiKeyPayload](docs/IRotateApiKeyPayload.md)
 - [IRotateApiKeySuccessResponse](docs/IRotateApiKeySuccessResponse.md)
 - [IRotateSIWBBRequestPayload](docs/IRotateSIWBBRequestPayload.md)
 - [IRotateSIWBBRequestSuccessResponse](docs/IRotateSIWBBRequestSuccessResponse.md)
 - [ISIWBBRequestDoc](docs/ISIWBBRequestDoc.md)
 - [ISatisfyMethod](docs/ISatisfyMethod.md)
 - [ISatisfyMethodConditionsInner](docs/ISatisfyMethodConditionsInner.md)
 - [ISatisfyMethodOptions](docs/ISatisfyMethodOptions.md)
 - [IScheduleTokenRefreshPayload](docs/IScheduleTokenRefreshPayload.md)
 - [IScheduleTokenRefreshSuccessResponse](docs/IScheduleTokenRefreshSuccessResponse.md)
 - [ISearchApplicationsPayload](docs/ISearchApplicationsPayload.md)
 - [ISearchApplicationsSuccessResponse](docs/ISearchApplicationsSuccessResponse.md)
 - [ISearchClaimsPayload](docs/ISearchClaimsPayload.md)
 - [ISearchClaimsSuccessResponse](docs/ISearchClaimsSuccessResponse.md)
 - [ISearchDeveloperAppsPayload](docs/ISearchDeveloperAppsPayload.md)
 - [ISearchDeveloperAppsSuccessResponse](docs/ISearchDeveloperAppsSuccessResponse.md)
 - [ISearchDynamicDataStoresPayload](docs/ISearchDynamicDataStoresPayload.md)
 - [ISearchDynamicDataStoresSuccessResponse](docs/ISearchDynamicDataStoresSuccessResponse.md)
 - [ISearchDynamicDataStoresSuccessResponsePagination](docs/ISearchDynamicDataStoresSuccessResponsePagination.md)
 - [ISearchPluginsPayload](docs/ISearchPluginsPayload.md)
 - [ISearchPluginsSuccessResponse](docs/ISearchPluginsSuccessResponse.md)
 - [ISearchUtilityPagesPayload](docs/ISearchUtilityPagesPayload.md)
 - [ISearchUtilityPagesSuccessResponse](docs/ISearchUtilityPagesSuccessResponse.md)
 - [ISendClaimAlertsPayload](docs/ISendClaimAlertsPayload.md)
 - [ISendClaimAlertsPayloadClaimAlertsInner](docs/ISendClaimAlertsPayloadClaimAlertsInner.md)
 - [ISetOptions](docs/ISetOptions.md)
 - [ISignOutPayload](docs/ISignOutPayload.md)
 - [ISignWithEmbeddedWalletPayload](docs/ISignWithEmbeddedWalletPayload.md)
 - [ISignWithEmbeddedWalletSuccessResponse](docs/ISignWithEmbeddedWalletSuccessResponse.md)
 - [ISimulateClaimPayload](docs/ISimulateClaimPayload.md)
 - [ISimulateClaimSuccessResponse](docs/ISimulateClaimSuccessResponse.md)
 - [ISimulateTxSuccessResponse](docs/ISimulateTxSuccessResponse.md)
 - [ISimulateTxSuccessResponseGasInfo](docs/ISimulateTxSuccessResponseGasInfo.md)
 - [ISimulateTxSuccessResponseResult](docs/ISimulateTxSuccessResponseResult.md)
 - [ISiwbbChallenge](docs/ISiwbbChallenge.md)
 - [ISiwbbChallengeVerificationResponse](docs/ISiwbbChallengeVerificationResponse.md)
 - [ISocialConnections](docs/ISocialConnections.md)
 - [ISocialConnectionsDiscord](docs/ISocialConnectionsDiscord.md)
 - [ISocialConnectionsTwitter](docs/ISocialConnectionsTwitter.md)
 - [IStandardsTimeline](docs/IStandardsTimeline.md)
 - [IStatusDoc](docs/IStatusDoc.md)
 - [ITierWithOptionalWeight](docs/ITierWithOptionalWeight.md)
 - [ITimedUpdatePermission](docs/ITimedUpdatePermission.md)
 - [ITimedUpdateWithBadgeIdsPermission](docs/ITimedUpdateWithBadgeIdsPermission.md)
 - [ITimelineItem](docs/ITimelineItem.md)
 - [ITransactionEntry](docs/ITransactionEntry.md)
 - [ITransfer](docs/ITransfer.md)
 - [ITransferActivityDoc](docs/ITransferActivityDoc.md)
 - [ITransferWithIncrements](docs/ITransferWithIncrements.md)
 - [IUintRange](docs/IUintRange.md)
 - [IUpdateAccountInfoPayload](docs/IUpdateAccountInfoPayload.md)
 - [IUpdateAccountInfoPayloadApprovedSignInMethods](docs/IUpdateAccountInfoPayloadApprovedSignInMethods.md)
 - [IUpdateAccountInfoPayloadApprovedSignInMethodsPasswordsInner](docs/IUpdateAccountInfoPayloadApprovedSignInMethodsPasswordsInner.md)
 - [IUpdateAccountInfoPayloadCustomPages](docs/IUpdateAccountInfoPayloadCustomPages.md)
 - [IUpdateAccountInfoPayloadNotifications](docs/IUpdateAccountInfoPayloadNotifications.md)
 - [IUpdateAccountInfoPayloadNotificationsDiscord](docs/IUpdateAccountInfoPayloadNotificationsDiscord.md)
 - [IUpdateAccountInfoPayloadNotificationsPreferences](docs/IUpdateAccountInfoPayloadNotificationsPreferences.md)
 - [IUpdateAccountInfoPayloadPublicSocialConnectionsToSetInner](docs/IUpdateAccountInfoPayloadPublicSocialConnectionsToSetInner.md)
 - [IUpdateAccountInfoPayloadWatchlists](docs/IUpdateAccountInfoPayloadWatchlists.md)
 - [IUpdateAccountInfoSuccessResponse](docs/IUpdateAccountInfoSuccessResponse.md)
 - [IUpdateAddressListAddressesPayload](docs/IUpdateAddressListAddressesPayload.md)
 - [IUpdateAddressListCoreDetailsPayload](docs/IUpdateAddressListCoreDetailsPayload.md)
 - [IUpdateAddressListsPayload](docs/IUpdateAddressListsPayload.md)
 - [IUpdateApplicationPayload](docs/IUpdateApplicationPayload.md)
 - [IUpdateApplicationSuccessResponse](docs/IUpdateApplicationSuccessResponse.md)
 - [IUpdateClaimPayload](docs/IUpdateClaimPayload.md)
 - [IUpdateDeveloperAppPayload](docs/IUpdateDeveloperAppPayload.md)
 - [IUpdateDeveloperAppSuccessResponse](docs/IUpdateDeveloperAppSuccessResponse.md)
 - [IUpdateDynamicDataStorePayload](docs/IUpdateDynamicDataStorePayload.md)
 - [IUpdateDynamicDataStoreSuccessResponse](docs/IUpdateDynamicDataStoreSuccessResponse.md)
 - [IUpdateHistory](docs/IUpdateHistory.md)
 - [IUpdatePluginPayload](docs/IUpdatePluginPayload.md)
 - [IUpdatePluginPayloadMetadata](docs/IUpdatePluginPayloadMetadata.md)
 - [IUpdatePluginPayloadVersionUpdatesInner](docs/IUpdatePluginPayloadVersionUpdatesInner.md)
 - [IUpdatePluginPayloadVersionUpdatesInnerConfig](docs/IUpdatePluginPayloadVersionUpdatesInnerConfig.md)
 - [IUpdatePluginPayloadVersionUpdatesInnerConfigClaimCreatorRedirect](docs/IUpdatePluginPayloadVersionUpdatesInnerConfigClaimCreatorRedirect.md)
 - [IUpdatePluginPayloadVersionUpdatesInnerConfigUserInputRedirect](docs/IUpdatePluginPayloadVersionUpdatesInnerConfigUserInputRedirect.md)
 - [IUpdatePluginPayloadVersionUpdatesInnerConfigVerificationCall](docs/IUpdatePluginPayloadVersionUpdatesInnerConfigVerificationCall.md)
 - [IUpdateUtilityPagePayload](docs/IUpdateUtilityPagePayload.md)
 - [IUpdateUtilityPageSuccessResponse](docs/IUpdateUtilityPageSuccessResponse.md)
 - [IUploadBalancesPayload](docs/IUploadBalancesPayload.md)
 - [IUsedLeafStatus](docs/IUsedLeafStatus.md)
 - [IUserBalanceStore](docs/IUserBalanceStore.md)
 - [IUserIncomingApproval](docs/IUserIncomingApproval.md)
 - [IUserIncomingApprovalPermission](docs/IUserIncomingApprovalPermission.md)
 - [IUserOutgoingApproval](docs/IUserOutgoingApproval.md)
 - [IUserOutgoingApprovalPermission](docs/IUserOutgoingApprovalPermission.md)
 - [IUserPermissions](docs/IUserPermissions.md)
 - [IUserRoyalties](docs/IUserRoyalties.md)
 - [IUtilityPageContent](docs/IUtilityPageContent.md)
 - [IUtilityPageDoc](docs/IUtilityPageDoc.md)
 - [IUtilityPageDocApprovalStatus](docs/IUtilityPageDocApprovalStatus.md)
 - [IUtilityPageDocHomePageView](docs/IUtilityPageDocHomePageView.md)
 - [IUtilityPageDocViewsByPeriod](docs/IUtilityPageDocViewsByPeriod.md)
 - [IUtilityPageLink](docs/IUtilityPageLink.md)
 - [IValueOptions](docs/IValueOptions.md)
 - [IValueStore](docs/IValueStore.md)
 - [IVerifySignInPayload](docs/IVerifySignInPayload.md)
 - [IntegrationPluginDetails](docs/IntegrationPluginDetails.md)
 - [IntegrationPluginDetailsMetadata](docs/IntegrationPluginDetailsMetadata.md)
 - [IntegrationPluginDetailsUpdate](docs/IntegrationPluginDetailsUpdate.md)
 - [IntegrationPluginParams](docs/IntegrationPluginParams.md)
 - [IntegrationPluginParamsMetadata](docs/IntegrationPluginParamsMetadata.md)
 - [JsonBodyInputSchema](docs/JsonBodyInputSchema.md)
 - [JsonBodyInputSchemaHyperlink](docs/JsonBodyInputSchemaHyperlink.md)
 - [JsonBodyInputSchemaOptionsInner](docs/JsonBodyInputSchemaOptionsInner.md)
 - [JsonBodyInputWithValue](docs/JsonBodyInputWithValue.md)
 - [JsonBodyInputWithValueValue](docs/JsonBodyInputWithValueValue.md)
 - [MetadataFetchOptions](docs/MetadataFetchOptions.md)
 - [MetadataFetchOptionsBadgeIds](docs/MetadataFetchOptionsBadgeIds.md)
 - [NumberType](docs/NumberType.md)
 - [OAuthScopeDetails](docs/OAuthScopeDetails.md)
 - [OAuthScopeDetailsWithId](docs/OAuthScopeDetailsWithId.md)
 - [OauthAppName](docs/OauthAppName.md)
 - [OrGroup](docs/OrGroup.md)
 - [OwnershipRequirements](docs/OwnershipRequirements.md)
 - [OwnershipRequirementsOptions](docs/OwnershipRequirementsOptions.md)
 - [PaginationInfo](docs/PaginationInfo.md)
 - [ParsedQsValue](docs/ParsedQsValue.md)
 - [PermissionNameString](docs/PermissionNameString.md)
 - [PluginErrorDoc](docs/PluginErrorDoc.md)
 - [PluginVersionConfigPayload](docs/PluginVersionConfigPayload.md)
 - [PluginVersionConfigPayloadVerificationCall](docs/PluginVersionConfigPayloadVerificationCall.md)
 - [Sender](docs/Sender.md)
 - [SimulateTxRequest](docs/SimulateTxRequest.md)
 - [StdFee](docs/StdFee.md)
 - [StdSignDoc](docs/StdSignDoc.md)
 - [SupportedChain](docs/SupportedChain.md)
 - [SupportedChainType](docs/SupportedChainType.md)
 - [TallyResponse](docs/TallyResponse.md)
 - [TallyResponseTally](docs/TallyResponseTally.md)
 - [TxContext](docs/TxContext.md)
 - [TxContextSender](docs/TxContextSender.md)
 - [UndelegationResponse](docs/UndelegationResponse.md)
 - [UpdateClaimRequest](docs/UpdateClaimRequest.md)
 - [Validator](docs/Validator.md)
 - [ValidatorCommission](docs/ValidatorCommission.md)
 - [ValidatorCommissionCommissionRates](docs/ValidatorCommissionCommissionRates.md)
 - [ValidatorConsensusPubkey](docs/ValidatorConsensusPubkey.md)
 - [ValidatorDescription](docs/ValidatorDescription.md)
 - [VerifyChallengeOptions](docs/VerifyChallengeOptions.md)
 - [VerifyChallengeOptionsExpectedChallengeParams](docs/VerifyChallengeOptionsExpectedChallengeParams.md)
 - [VerifySIWBBOptions](docs/VerifySIWBBOptions.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="apiKey"></a>
### apiKey

- **Type**: API key
- **API key parameter name**: x-api-key
- **Location**: HTTP header

<a id="frontendOnly"></a>
### frontendOnly

- **Type**: API key
- **API key parameter name**: Origin
- **Location**: HTTP header

<a id="userSignedIn"></a>
### userSignedIn


<a id="userMaybeSignedIn"></a>
### userMaybeSignedIn


<a id="userIsManager"></a>
### userIsManager


<a id="userIsOwner"></a>
### userIsOwner



## Author




