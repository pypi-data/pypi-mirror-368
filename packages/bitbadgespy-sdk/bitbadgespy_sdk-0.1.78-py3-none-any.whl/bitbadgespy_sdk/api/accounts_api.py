# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Pages** (`manageUtilityPages`)   Create, update, and delete utility pages on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from bitbadgespy_sdk.models.i_get_account_payload import IGetAccountPayload
from bitbadgespy_sdk.models.i_get_account_success_response import IGetAccountSuccessResponse
from bitbadgespy_sdk.models.i_get_accounts_payload import IGetAccountsPayload
from bitbadgespy_sdk.models.i_get_accounts_success_response import IGetAccountsSuccessResponse
from bitbadgespy_sdk.models.i_get_address_lists_for_user_payload import IGetAddressListsForUserPayload
from bitbadgespy_sdk.models.i_get_address_lists_for_user_success_response import IGetAddressListsForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_badges_view_for_user_payload import IGetBadgesViewForUserPayload
from bitbadgespy_sdk.models.i_get_badges_view_for_user_success_response import IGetBadgesViewForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_claim_activity_for_user_payload import IGetClaimActivityForUserPayload
from bitbadgespy_sdk.models.i_get_claim_activity_for_user_success_response import IGetClaimActivityForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_claim_alerts_for_user_payload import IGetClaimAlertsForUserPayload
from bitbadgespy_sdk.models.i_get_claim_alerts_for_user_success_response import IGetClaimAlertsForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_list_activity_for_user_payload import IGetListActivityForUserPayload
from bitbadgespy_sdk.models.i_get_list_activity_for_user_success_response import IGetListActivityForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_points_activity_for_user_payload import IGetPointsActivityForUserPayload
from bitbadgespy_sdk.models.i_get_points_activity_for_user_success_response import IGetPointsActivityForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_siwbb_requests_for_user_payload import IGetSiwbbRequestsForUserPayload
from bitbadgespy_sdk.models.i_get_siwbb_requests_for_user_success_response import IGetSiwbbRequestsForUserSuccessResponse
from bitbadgespy_sdk.models.i_get_transfer_activity_for_user_payload import IGetTransferActivityForUserPayload
from bitbadgespy_sdk.models.i_get_transfer_activity_for_user_success_response import IGetTransferActivityForUserSuccessResponse

from bitbadgespy_sdk.api_client import ApiClient, RequestSerialized
from bitbadgespy_sdk.api_response import ApiResponse
from bitbadgespy_sdk.rest import RESTResponseType


class AccountsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def get_account(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetAccountPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetAccountSuccessResponse:
        """Get Account

        Retrieves an account by address or username.  ```tsx const res = await BitBadgesApi.getAccount({ address: '...', username: '...' }); console.log(res); ```  For more specific views, you can use the other routes.  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccount)**  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Stored Social connections   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc.  Couple Notes: - **[Native Chain Algorithm](https://docs.bitbadges.io/for-developers/bitbadges-api/concepts/native-chain-algorithm)**  Note: The `views` and corresponding fields like `badgesCollected`, `claimAlerts`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAccountPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_account_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_account_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetAccountPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetAccountSuccessResponse]:
        """Get Account

        Retrieves an account by address or username.  ```tsx const res = await BitBadgesApi.getAccount({ address: '...', username: '...' }); console.log(res); ```  For more specific views, you can use the other routes.  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccount)**  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Stored Social connections   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc.  Couple Notes: - **[Native Chain Algorithm](https://docs.bitbadges.io/for-developers/bitbadges-api/concepts/native-chain-algorithm)**  Note: The `views` and corresponding fields like `badgesCollected`, `claimAlerts`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAccountPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_account_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_account_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetAccountPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Account

        Retrieves an account by address or username.  ```tsx const res = await BitBadgesApi.getAccount({ address: '...', username: '...' }); console.log(res); ```  For more specific views, you can use the other routes.  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccount)**  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Stored Social connections   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc.  Couple Notes: - **[Native Chain Algorithm](https://docs.bitbadges.io/for-developers/bitbadges-api/concepts/native-chain-algorithm)**  Note: The `views` and corresponding fields like `badgesCollected`, `claimAlerts`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAccountPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_account_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_account_serialize(
        self,
        x_api_key,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'userMaybeSignedIn', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/user',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_accounts(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_accounts_payload: IGetAccountsPayload,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetAccountsSuccessResponse:
        """Get Accounts - Batch

        Retrieves accounts and accompanying details. This route is all-inclusive and uses a view-based approach to fetch specific data about the account. See more in the tutorial below.  ```tsx const accountsRes = await BitBadgesApi.getAccounts({   accountsToFetch: [     {       //example       address: 'bb1...',       viewsToFetch: [         {           viewType: 'badgesCollected',           viewId: 'badgesCollected',           bookmark: '',         },       ],     },   ], }) const account = accountsRes.accounts[0] ```  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Public badge balances   - Public activity   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Private Attestations   - Private activity, etc   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc. - `readClaimAlerts` - Required if fetching private claim alerts - `readAuthenticationCodes` - Required if fetching private authentication codes  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccounts)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_accounts_payload: (required)
        :type i_get_accounts_payload: IGetAccountsPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_accounts_serialize(
            x_api_key=x_api_key,
            i_get_accounts_payload=i_get_accounts_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountsSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_accounts_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_accounts_payload: IGetAccountsPayload,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetAccountsSuccessResponse]:
        """Get Accounts - Batch

        Retrieves accounts and accompanying details. This route is all-inclusive and uses a view-based approach to fetch specific data about the account. See more in the tutorial below.  ```tsx const accountsRes = await BitBadgesApi.getAccounts({   accountsToFetch: [     {       //example       address: 'bb1...',       viewsToFetch: [         {           viewType: 'badgesCollected',           viewId: 'badgesCollected',           bookmark: '',         },       ],     },   ], }) const account = accountsRes.accounts[0] ```  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Public badge balances   - Public activity   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Private Attestations   - Private activity, etc   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc. - `readClaimAlerts` - Required if fetching private claim alerts - `readAuthenticationCodes` - Required if fetching private authentication codes  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccounts)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_accounts_payload: (required)
        :type i_get_accounts_payload: IGetAccountsPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_accounts_serialize(
            x_api_key=x_api_key,
            i_get_accounts_payload=i_get_accounts_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountsSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_accounts_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_accounts_payload: IGetAccountsPayload,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Accounts - Batch

        Retrieves accounts and accompanying details. This route is all-inclusive and uses a view-based approach to fetch specific data about the account. See more in the tutorial below.  ```tsx const accountsRes = await BitBadgesApi.getAccounts({   accountsToFetch: [     {       //example       address: 'bb1...',       viewsToFetch: [         {           viewType: 'badgesCollected',           viewId: 'badgesCollected',           bookmark: '',         },       ],     },   ], }) const account = accountsRes.accounts[0] ```  ## Authentication Details - **Public Data**: Available with API key only   - Basic profile information   - Public badge balances   - Public activity   - Etc  - **Private Data** (requires user authentication):   - Notification preferences   - Private Attestations   - Private activity, etc   - Etc  Scopes - `readProfile` - Required for private profile information like notification preferences, social connections, etc. - `readClaimAlerts` - Required if fetching private claim alerts - `readAuthenticationCodes` - Required if fetching private authentication codes  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAccountsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaccounts)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_accounts_payload: (required)
        :type i_get_accounts_payload: IGetAccountsPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_accounts_serialize(
            x_api_key=x_api_key,
            i_get_accounts_payload=i_get_accounts_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAccountsSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_accounts_serialize(
        self,
        x_api_key,
        i_get_accounts_payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter
        if i_get_accounts_payload is not None:
            _body_params = i_get_accounts_payload


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'userMaybeSignedIn', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/users',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_address_lists_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetAddressListsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetAddressListsForUserSuccessResponse:
        """Get Address Lists For User

        Gets address lists for a specific account. Specify the viewType to determine what address lists to retrieve.  ```tsx await BitBadgesApi.getAddressListsForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaddresslistsforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAddressListsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_address_lists_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAddressListsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_address_lists_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetAddressListsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetAddressListsForUserSuccessResponse]:
        """Get Address Lists For User

        Gets address lists for a specific account. Specify the viewType to determine what address lists to retrieve.  ```tsx await BitBadgesApi.getAddressListsForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaddresslistsforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAddressListsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_address_lists_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAddressListsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_address_lists_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetAddressListsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Address Lists For User

        Gets address lists for a specific account. Specify the viewType to determine what address lists to retrieve.  ```tsx await BitBadgesApi.getAddressListsForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAddressListsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getaddresslistsforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAddressListsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_address_lists_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAddressListsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_address_lists_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/lists',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_badges_view_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetBadgesViewForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetBadgesViewForUserSuccessResponse:
        """Get Badges For User

        Gets badges for a specific user. Specify the viewType to determine what badges to retrieve. Default is 'collected'.  ```tsx await BitBadgesApi.getBadgesViewForUser(address, { viewType: \"collected\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgesviewforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgesViewForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_badges_view_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgesViewForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_badges_view_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetBadgesViewForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetBadgesViewForUserSuccessResponse]:
        """Get Badges For User

        Gets badges for a specific user. Specify the viewType to determine what badges to retrieve. Default is 'collected'.  ```tsx await BitBadgesApi.getBadgesViewForUser(address, { viewType: \"collected\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgesviewforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgesViewForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_badges_view_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgesViewForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_badges_view_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetBadgesViewForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Badges For User

        Gets badges for a specific user. Specify the viewType to determine what badges to retrieve. Default is 'collected'.  ```tsx await BitBadgesApi.getBadgesViewForUser(address, { viewType: \"collected\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgesViewForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgesviewforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgesViewForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_badges_view_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgesViewForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_badges_view_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/badges/',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_claim_activity_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetClaimActivityForUserSuccessResponse:
        """Get Claim Activity For User

        Gets claim activity for a specific user. Specify the viewType to determine what claim activity to retrieve.  Most claim activity will be public, but if the state is hidden, then only the manager of the claim and you should be able to see the activity.  ```tsx await BitBadgesApi.getClaimActivityForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimactivityforuser)**  Scopes:   - `completeClaims` - Required if fetching all claim activity.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_claim_activity_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetClaimActivityForUserSuccessResponse]:
        """Get Claim Activity For User

        Gets claim activity for a specific user. Specify the viewType to determine what claim activity to retrieve.  Most claim activity will be public, but if the state is hidden, then only the manager of the claim and you should be able to see the activity.  ```tsx await BitBadgesApi.getClaimActivityForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimactivityforuser)**  Scopes:   - `completeClaims` - Required if fetching all claim activity.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_claim_activity_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Claim Activity For User

        Gets claim activity for a specific user. Specify the viewType to determine what claim activity to retrieve.  Most claim activity will be public, but if the state is hidden, then only the manager of the claim and you should be able to see the activity.  ```tsx await BitBadgesApi.getClaimActivityForUser(address, { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimactivityforuser)**  Scopes:   - `completeClaims` - Required if fetching all claim activity.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claim_activity_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/activity/claims',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_claim_alerts_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimAlertsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetClaimAlertsForUserSuccessResponse:
        """Get Claim Alerts For User

        Gets claim alerts for a specific user. Specify the viewType 'received' or 'sent' to determine what claim alerts to retrieve.  ```tsx await BitBadgesApi.getClaimAlertsForUser(address, { viewType: 'received' }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimalertsforuser)**  Scopes:   - `readClaimAlerts` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimAlertsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_alerts_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAlertsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_claim_alerts_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimAlertsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetClaimAlertsForUserSuccessResponse]:
        """Get Claim Alerts For User

        Gets claim alerts for a specific user. Specify the viewType 'received' or 'sent' to determine what claim alerts to retrieve.  ```tsx await BitBadgesApi.getClaimAlertsForUser(address, { viewType: 'received' }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimalertsforuser)**  Scopes:   - `readClaimAlerts` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimAlertsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_alerts_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAlertsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_claim_alerts_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetClaimAlertsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Claim Alerts For User

        Gets claim alerts for a specific user. Specify the viewType 'received' or 'sent' to determine what claim alerts to retrieve.  ```tsx await BitBadgesApi.getClaimAlertsForUser(address, { viewType: 'received' }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAlertsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimalertsforuser)**  Scopes:   - `readClaimAlerts` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimAlertsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_claim_alerts_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAlertsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claim_alerts_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/claimAlerts',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_list_activity_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetListActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetListActivityForUserSuccessResponse:
        """Get Lists Activity For User

        Gets lists activity for a specific user.  ```tsx await BitBadgesApi.getListActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getlistActivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetListActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_list_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetListActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_list_activity_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetListActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetListActivityForUserSuccessResponse]:
        """Get Lists Activity For User

        Gets lists activity for a specific user.  ```tsx await BitBadgesApi.getListActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getlistActivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetListActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_list_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetListActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_list_activity_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetListActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Lists Activity For User

        Gets lists activity for a specific user.  ```tsx await BitBadgesApi.getListActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetListActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getlistActivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetListActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_list_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetListActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_list_activity_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/activity/lists',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_points_activity_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetPointsActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetPointsActivityForUserSuccessResponse:
        """Get Points Activity For User

        Gets points activity for a specific user.  ```tsx await BitBadgesApi.getPointsActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_points_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_points_activity_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetPointsActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetPointsActivityForUserSuccessResponse]:
        """Get Points Activity For User

        Gets points activity for a specific user.  ```tsx await BitBadgesApi.getPointsActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_points_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_points_activity_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetPointsActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Points Activity For User

        Gets points activity for a specific user.  ```tsx await BitBadgesApi.getPointsActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_points_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_points_activity_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/activity/points',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_siwbb_requests_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetSiwbbRequestsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetSiwbbRequestsForUserSuccessResponse:
        """Get SIWBB Requests For User

        Gets Sign-In with BitBadges (SIWBB) requests for a user.  ```tsx await BitBadgesApi.getSiwbbRequestsForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getsiwbbrequestsforuser)**  Scopes:   - `readAuthenticationCodes` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetSiwbbRequestsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_siwbb_requests_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetSiwbbRequestsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_siwbb_requests_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetSiwbbRequestsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetSiwbbRequestsForUserSuccessResponse]:
        """Get SIWBB Requests For User

        Gets Sign-In with BitBadges (SIWBB) requests for a user.  ```tsx await BitBadgesApi.getSiwbbRequestsForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getsiwbbrequestsforuser)**  Scopes:   - `readAuthenticationCodes` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetSiwbbRequestsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_siwbb_requests_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetSiwbbRequestsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_siwbb_requests_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetSiwbbRequestsForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get SIWBB Requests For User

        Gets Sign-In with BitBadges (SIWBB) requests for a user.  ```tsx await BitBadgesApi.getSiwbbRequestsForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetSiwbbRequestsForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getsiwbbrequestsforuser)**  Scopes:   - `readAuthenticationCodes` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetSiwbbRequestsForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_siwbb_requests_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetSiwbbRequestsForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_siwbb_requests_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/requests/siwbb',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_transfer_activity_for_user(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetTransferActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> IGetTransferActivityForUserSuccessResponse:
        """Get Transfer Activity For User

        Gets transfer activity for a specific user.  ```tsx await BitBadgesApi.getTransferActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#gettransferactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetTransferActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_transfer_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetTransferActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_transfer_activity_for_user_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetTransferActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[IGetTransferActivityForUserSuccessResponse]:
        """Get Transfer Activity For User

        Gets transfer activity for a specific user.  ```tsx await BitBadgesApi.getTransferActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#gettransferactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetTransferActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_transfer_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetTransferActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_transfer_activity_for_user_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        address: Annotated[StrictStr, Field(description="Account address")],
        payload: Annotated[Optional[IGetTransferActivityForUserPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get Transfer Activity For User

        Gets transfer activity for a specific user.  ```tsx await BitBadgesApi.getTransferActivityForUser({ address: \"bb1...\" }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetTransferActivityForUserSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#gettransferactivityforuser)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param address: Account address (required)
        :type address: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetTransferActivityForUserPayload
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_transfer_activity_for_user_serialize(
            x_api_key=x_api_key,
            address=address,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetTransferActivityForUserSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_transfer_activity_for_user_serialize(
        self,
        x_api_key,
        address,
        payload,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        if payload is not None:
            
            _query_params.append(('payload', payload))
            
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/account/{address}/activity/badges',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


