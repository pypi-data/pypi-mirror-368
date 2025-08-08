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

from pydantic import Field, StrictInt, StrictStr
from typing import Any, Dict, Optional
from typing_extensions import Annotated
from bitbadgespy_sdk.models.i_amount_tracker_id_details import IAmountTrackerIdDetails
from bitbadgespy_sdk.models.i_challenge_tracker_id_details import IChallengeTrackerIdDetails
from bitbadgespy_sdk.models.i_get_badge_activity_payload import IGetBadgeActivityPayload
from bitbadgespy_sdk.models.i_get_badge_activity_success_response import IGetBadgeActivitySuccessResponse
from bitbadgespy_sdk.models.i_get_badge_balance_by_address_payload import IGetBadgeBalanceByAddressPayload
from bitbadgespy_sdk.models.i_get_badge_balance_by_address_specific_badge_success_response import IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse
from bitbadgespy_sdk.models.i_get_badge_balance_by_address_success_response import IGetBadgeBalanceByAddressSuccessResponse
from bitbadgespy_sdk.models.i_get_badge_metadata_success_response import IGetBadgeMetadataSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_amount_tracker_by_id_success_response import IGetCollectionAmountTrackerByIdSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_amount_trackers_payload import IGetCollectionAmountTrackersPayload
from bitbadgespy_sdk.models.i_get_collection_amount_trackers_success_response import IGetCollectionAmountTrackersSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_challenge_tracker_by_id_success_response import IGetCollectionChallengeTrackerByIdSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_challenge_trackers_payload import IGetCollectionChallengeTrackersPayload
from bitbadgespy_sdk.models.i_get_collection_challenge_trackers_success_response import IGetCollectionChallengeTrackersSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_claims_success_response import IGetCollectionClaimsSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_listings_payload import IGetCollectionListingsPayload
from bitbadgespy_sdk.models.i_get_collection_listings_success_response import IGetCollectionListingsSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_owners_payload import IGetCollectionOwnersPayload
from bitbadgespy_sdk.models.i_get_collection_owners_success_response import IGetCollectionOwnersSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_success_response import IGetCollectionSuccessResponse
from bitbadgespy_sdk.models.i_get_collection_transfer_activity_payload import IGetCollectionTransferActivityPayload
from bitbadgespy_sdk.models.i_get_collection_transfer_activity_success_response import IGetCollectionTransferActivitySuccessResponse
from bitbadgespy_sdk.models.i_get_collections_payload import IGetCollectionsPayload
from bitbadgespy_sdk.models.i_get_collections_success_response import IGetCollectionsSuccessResponse
from bitbadgespy_sdk.models.i_get_owners_for_badge_payload import IGetOwnersForBadgePayload
from bitbadgespy_sdk.models.i_get_owners_for_badge_success_response import IGetOwnersForBadgeSuccessResponse
from bitbadgespy_sdk.models.i_refresh_status_success_response import IRefreshStatusSuccessResponse
from bitbadgespy_sdk.models.i_upload_balances_payload import IUploadBalancesPayload

from bitbadgespy_sdk.api_client import ApiClient, RequestSerialized
from bitbadgespy_sdk.api_response import ApiResponse
from bitbadgespy_sdk.rest import RESTResponseType


class BadgesApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def get_badge_activity(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which activity is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetBadgeActivitySuccessResponse:
        """Get Badge Activity

        Retrieves the activity in a paginated format for a specific badge in a collection.  ```tsx const res = await BitBadgesApi.getBadgeActivity(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeactivity)** 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param badge_id: The ID of the badge for which activity is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeActivityPayload
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

        _param = self._get_badge_activity_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeActivitySuccessResponse",
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
    def get_badge_activity_with_http_info(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which activity is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetBadgeActivitySuccessResponse]:
        """Get Badge Activity

        Retrieves the activity in a paginated format for a specific badge in a collection.  ```tsx const res = await BitBadgesApi.getBadgeActivity(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeactivity)** 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param badge_id: The ID of the badge for which activity is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeActivityPayload
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

        _param = self._get_badge_activity_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeActivitySuccessResponse",
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
    def get_badge_activity_without_preload_content(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which activity is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Badge Activity

        Retrieves the activity in a paginated format for a specific badge in a collection.  ```tsx const res = await BitBadgesApi.getBadgeActivity(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeactivity)** 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param badge_id: The ID of the badge for which activity is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeActivityPayload
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

        _param = self._get_badge_activity_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeActivitySuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_badge_activity_serialize(
        self,
        collection_id,
        badge_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        if badge_id is not None:
            _path_params['badgeId'] = badge_id
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
            resource_path='/collection/{collectionId}/{badgeId}/activity',
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
    def get_badge_balance_by_address(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeBalanceByAddressPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetBadgeBalanceByAddressSuccessResponse:
        """Get Badge Balances By Address

        Retrieves the balances of a specific address for a collection.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddress(collectionId, address, { ...options }); console.log(res); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddress)**  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (user-level approvals)  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeBalanceByAddressPayload
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

        _param = self._get_badge_balance_by_address_serialize(
            collection_id=collection_id,
            address=address,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSuccessResponse",
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
    def get_badge_balance_by_address_with_http_info(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeBalanceByAddressPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetBadgeBalanceByAddressSuccessResponse]:
        """Get Badge Balances By Address

        Retrieves the balances of a specific address for a collection.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddress(collectionId, address, { ...options }); console.log(res); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddress)**  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (user-level approvals)  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeBalanceByAddressPayload
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

        _param = self._get_badge_balance_by_address_serialize(
            collection_id=collection_id,
            address=address,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSuccessResponse",
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
    def get_badge_balance_by_address_without_preload_content(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetBadgeBalanceByAddressPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Badge Balances By Address

        Retrieves the balances of a specific address for a collection.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddress(collectionId, address, { ...options }); console.log(res); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddress)**  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (user-level approvals)  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetBadgeBalanceByAddressPayload
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

        _param = self._get_badge_balance_by_address_serialize(
            collection_id=collection_id,
            address=address,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_badge_balance_by_address_serialize(
        self,
        collection_id,
        address,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/balance/{address}',
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
    def get_badge_balance_by_address_specific_badge(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which the balance is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
    ) -> IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse:
        """Get Badge Balance By Address - Specific Badge

        Retrieves the balance of a specific badge for a specific address at the current time.  For more advanced queries returning the whole balance document, please use the POST `/collection/{collectionId}/balance/{address}` endpoint.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddressSpecificBadge(collectionId, address, badgeId); console.log(res); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddressspecificbadge)**  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param badge_id: The ID of the badge for which the balance is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_badge_balance_by_address_specific_badge_serialize(
            collection_id=collection_id,
            address=address,
            badge_id=badge_id,
            x_api_key=x_api_key,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse",
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
    def get_badge_balance_by_address_specific_badge_with_http_info(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which the balance is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
    ) -> ApiResponse[IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse]:
        """Get Badge Balance By Address - Specific Badge

        Retrieves the balance of a specific badge for a specific address at the current time.  For more advanced queries returning the whole balance document, please use the POST `/collection/{collectionId}/balance/{address}` endpoint.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddressSpecificBadge(collectionId, address, badgeId); console.log(res); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddressspecificbadge)**  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param badge_id: The ID of the badge for which the balance is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_badge_balance_by_address_specific_badge_serialize(
            collection_id=collection_id,
            address=address,
            badge_id=badge_id,
            x_api_key=x_api_key,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse",
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
    def get_badge_balance_by_address_specific_badge_without_preload_content(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection containing the badge.")],
        address: Annotated[StrictStr, Field(description="The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply.")],
        badge_id: Annotated[StrictInt, Field(description="The ID of the badge for which the balance is to be retrieved.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
        """Get Badge Balance By Address - Specific Badge

        Retrieves the balance of a specific badge for a specific address at the current time.  For more advanced queries returning the whole balance document, please use the POST `/collection/{collectionId}/balance/{address}` endpoint.  ```tsx const res = await BitBadgesApi.getBadgeBalanceByAddressSpecificBadge(collectionId, address, badgeId); console.log(res); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeBalanceByAddressSpecificBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgebalancebyaddressspecificbadge)**  Alternative Flow: Note that you can also set up a claim that checks badge ownership and check the success per user of that claim as well 

        :param collection_id: The ID of the collection containing the badge. (required)
        :type collection_id: int
        :param address: The address for which the badge balance is to be retrieved. Can be \"Total\" for the circulating supply. (required)
        :type address: str
        :param badge_id: The ID of the badge for which the balance is to be retrieved. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_badge_balance_by_address_specific_badge_serialize(
            collection_id=collection_id,
            address=address,
            badge_id=badge_id,
            x_api_key=x_api_key,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeBalanceByAddressSpecificBadgeSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_badge_balance_by_address_specific_badge_serialize(
        self,
        collection_id,
        address,
        badge_id,
        x_api_key,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        if address is not None:
            _path_params['address'] = address
        if badge_id is not None:
            _path_params['badgeId'] = badge_id
        # process the query parameters
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
            resource_path='/collection/{collectionId}/balance/{address}/{badgeId}',
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
    def get_badge_metadata(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        badge_id: Annotated[StrictStr, Field(description="Badge ID")],
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
    ) -> IGetBadgeMetadataSuccessResponse:
        """Get Badge Metadata

        Gets current metadata for a specific badge in a collection.  ```tsx await BitBadgesApi.getBadgeMetadata(\"123\", \"1\"); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeMetadataSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeMetadata)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param badge_id: Badge ID (required)
        :type badge_id: str
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

        _param = self._get_badge_metadata_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            badge_id=badge_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeMetadataSuccessResponse",
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
    def get_badge_metadata_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        badge_id: Annotated[StrictStr, Field(description="Badge ID")],
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
    ) -> ApiResponse[IGetBadgeMetadataSuccessResponse]:
        """Get Badge Metadata

        Gets current metadata for a specific badge in a collection.  ```tsx await BitBadgesApi.getBadgeMetadata(\"123\", \"1\"); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeMetadataSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeMetadata)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param badge_id: Badge ID (required)
        :type badge_id: str
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

        _param = self._get_badge_metadata_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            badge_id=badge_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeMetadataSuccessResponse",
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
    def get_badge_metadata_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        badge_id: Annotated[StrictStr, Field(description="Badge ID")],
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
        """Get Badge Metadata

        Gets current metadata for a specific badge in a collection.  ```tsx await BitBadgesApi.getBadgeMetadata(\"123\", \"1\"); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetBadgeMetadataSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getbadgeMetadata)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param badge_id: Badge ID (required)
        :type badge_id: str
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

        _param = self._get_badge_metadata_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            badge_id=badge_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetBadgeMetadataSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_badge_metadata_serialize(
        self,
        x_api_key,
        collection_id,
        badge_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        if badge_id is not None:
            _path_params['badgeId'] = badge_id
        # process the query parameters
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
            resource_path='/collection/{collectionId}/{badgeId}/metadata',
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
    def get_collection(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
    ) -> IGetCollectionSuccessResponse:
        """Get Collection

        Gets a specific collection.  ```tsx await BitBadgesApi.getCollection(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollection)**  Note: The `views` and corresponding fields like `owners`, `approvalTrackers`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionSuccessResponse",
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
    def get_collection_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
    ) -> ApiResponse[IGetCollectionSuccessResponse]:
        """Get Collection

        Gets a specific collection.  ```tsx await BitBadgesApi.getCollection(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollection)**  Note: The `views` and corresponding fields like `owners`, `approvalTrackers`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionSuccessResponse",
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
    def get_collection_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
        """Get Collection

        Gets a specific collection.  ```tsx await BitBadgesApi.getCollection(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollection)**  Note: The `views` and corresponding fields like `owners`, `approvalTrackers`, etc will be blank with this simple GET but are provided in the response for compatibility with the SDK. To actually fetch these views, use the POST batch route or the individual view routes.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        # process the query parameters
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
            resource_path='/collection/{collectionId}',
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
    def get_collection_amount_tracker_by_id(
        self,
        payload: Annotated[Optional[IAmountTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionAmountTrackerByIdSuccessResponse:
        """Get Collection Amount Tracker By ID

        Gets an amount tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iAmountTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IAmountTrackerIdDetails
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

        _param = self._get_collection_amount_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackerByIdSuccessResponse",
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
    def get_collection_amount_tracker_by_id_with_http_info(
        self,
        payload: Annotated[Optional[IAmountTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionAmountTrackerByIdSuccessResponse]:
        """Get Collection Amount Tracker By ID

        Gets an amount tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iAmountTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IAmountTrackerIdDetails
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

        _param = self._get_collection_amount_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackerByIdSuccessResponse",
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
    def get_collection_amount_tracker_by_id_without_preload_content(
        self,
        payload: Annotated[Optional[IAmountTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Amount Tracker By ID

        Gets an amount tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iAmountTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IAmountTrackerIdDetails
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

        _param = self._get_collection_amount_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackerByIdSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_amount_tracker_by_id_serialize(
        self,
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
            resource_path='/api/v0/collection/amountTracker',
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
    def get_collection_amount_trackers(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionAmountTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionAmountTrackersSuccessResponse:
        """Get Collection Amount Trackers

        Gets amount trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionAmountTrackersPayload
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

        _param = self._get_collection_amount_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackersSuccessResponse",
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
    def get_collection_amount_trackers_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionAmountTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionAmountTrackersSuccessResponse]:
        """Get Collection Amount Trackers

        Gets amount trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionAmountTrackersPayload
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

        _param = self._get_collection_amount_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackersSuccessResponse",
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
    def get_collection_amount_trackers_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionAmountTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Amount Trackers

        Gets amount trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionAmountTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionAmountTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionamounttrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionAmountTrackersPayload
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

        _param = self._get_collection_amount_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionAmountTrackersSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_amount_trackers_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/amountTrackers',
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
    def get_collection_challenge_tracker_by_id(
        self,
        payload: Annotated[Optional[IChallengeTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionChallengeTrackerByIdSuccessResponse:
        """Get Collection Challenge Tracker By ID

        Gets a challenge tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iChallengeTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IChallengeTrackerIdDetails
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

        _param = self._get_collection_challenge_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackerByIdSuccessResponse",
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
    def get_collection_challenge_tracker_by_id_with_http_info(
        self,
        payload: Annotated[Optional[IChallengeTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionChallengeTrackerByIdSuccessResponse]:
        """Get Collection Challenge Tracker By ID

        Gets a challenge tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iChallengeTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IChallengeTrackerIdDetails
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

        _param = self._get_collection_challenge_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackerByIdSuccessResponse",
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
    def get_collection_challenge_tracker_by_id_without_preload_content(
        self,
        payload: Annotated[Optional[IChallengeTrackerIdDetails], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Challenge Tracker By ID

        Gets a challenge tracker by ID for a collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackerById({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iChallengeTrackerIdDetails)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackerByIdSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackerbyid)**

        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IChallengeTrackerIdDetails
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

        _param = self._get_collection_challenge_tracker_by_id_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackerByIdSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_challenge_tracker_by_id_serialize(
        self,
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
            resource_path='/api/v0/collection/challengeTracker',
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
    def get_collection_challenge_trackers(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionChallengeTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionChallengeTrackersSuccessResponse:
        """Get Collection Challenge Trackers

        Gets challenge trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionChallengeTrackersPayload
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

        _param = self._get_collection_challenge_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackersSuccessResponse",
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
    def get_collection_challenge_trackers_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionChallengeTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionChallengeTrackersSuccessResponse]:
        """Get Collection Challenge Trackers

        Gets challenge trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionChallengeTrackersPayload
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

        _param = self._get_collection_challenge_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackersSuccessResponse",
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
    def get_collection_challenge_trackers_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionChallengeTrackersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Challenge Trackers

        Gets challenge trackers for a specific collection.  ```tsx await BitBadgesApi.getCollectionChallengeTrackers(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionChallengeTrackersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionchallengetrackers)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionChallengeTrackersPayload
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

        _param = self._get_collection_challenge_trackers_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionChallengeTrackersSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_challenge_trackers_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/challengeTrackers',
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
    def get_collection_claims(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
    ) -> IGetCollectionClaimsSuccessResponse:
        """Get Collection Claims

        Gets claims for a specific collection.  ```tsx await BitBadgesApi.getCollectionClaims(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of collection)  Note: For fetching more advanced information like private claim data, you can do so with the get claim routes. Use the IDs from these responses.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_claims_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionClaimsSuccessResponse",
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
    def get_collection_claims_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
    ) -> ApiResponse[IGetCollectionClaimsSuccessResponse]:
        """Get Collection Claims

        Gets claims for a specific collection.  ```tsx await BitBadgesApi.getCollectionClaims(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of collection)  Note: For fetching more advanced information like private claim data, you can do so with the get claim routes. Use the IDs from these responses.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_claims_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionClaimsSuccessResponse",
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
    def get_collection_claims_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
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
        """Get Collection Claims

        Gets claims for a specific collection.  ```tsx await BitBadgesApi.getCollectionClaims(\"123\", { ... }); ```  SDK Links: - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of collection)  Note: For fetching more advanced information like private claim data, you can do so with the get claim routes. Use the IDs from these responses.

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
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

        _param = self._get_collection_claims_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionClaimsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_claims_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        # process the query parameters
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
            resource_path='/collection/{collectionId}/claims',
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
    def get_collection_listings(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionListingsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionListingsSuccessResponse:
        """Get Collection Listings

        Gets listings for a specific collection.  ```tsx await BitBadgesApi.getCollectionListings(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionlistings)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionListingsPayload
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

        _param = self._get_collection_listings_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionListingsSuccessResponse",
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
    def get_collection_listings_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionListingsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionListingsSuccessResponse]:
        """Get Collection Listings

        Gets listings for a specific collection.  ```tsx await BitBadgesApi.getCollectionListings(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionlistings)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionListingsPayload
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

        _param = self._get_collection_listings_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionListingsSuccessResponse",
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
    def get_collection_listings_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionListingsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Listings

        Gets listings for a specific collection.  ```tsx await BitBadgesApi.getCollectionListings(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionListingsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionlistings)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionListingsPayload
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

        _param = self._get_collection_listings_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionListingsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_listings_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/listings',
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
    def get_collection_owners(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionOwnersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionOwnersSuccessResponse:
        """Get Collection Owners

        Gets owners for a specific collection.  ```tsx await BitBadgesApi.getCollectionOwners(\"123\"); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionowners)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionOwnersPayload
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

        _param = self._get_collection_owners_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionOwnersSuccessResponse",
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
    def get_collection_owners_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionOwnersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionOwnersSuccessResponse]:
        """Get Collection Owners

        Gets owners for a specific collection.  ```tsx await BitBadgesApi.getCollectionOwners(\"123\"); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionowners)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionOwnersPayload
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

        _param = self._get_collection_owners_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionOwnersSuccessResponse",
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
    def get_collection_owners_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionOwnersPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Owners

        Gets owners for a specific collection.  ```tsx await BitBadgesApi.getCollectionOwners(\"123\"); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionOwnersSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectionowners)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionOwnersPayload
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

        _param = self._get_collection_owners_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionOwnersSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_owners_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/owners',
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
    def get_collection_transfer_activity(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionTransferActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetCollectionTransferActivitySuccessResponse:
        """Get Collection Transfer Activity

        Gets transfer activity for a specific collection.  ```tsx await BitBadgesApi.getCollectionTransferActivity(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectiontransferactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionTransferActivityPayload
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

        _param = self._get_collection_transfer_activity_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionTransferActivitySuccessResponse",
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
    def get_collection_transfer_activity_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionTransferActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetCollectionTransferActivitySuccessResponse]:
        """Get Collection Transfer Activity

        Gets transfer activity for a specific collection.  ```tsx await BitBadgesApi.getCollectionTransferActivity(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectiontransferactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionTransferActivityPayload
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

        _param = self._get_collection_transfer_activity_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionTransferActivitySuccessResponse",
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
    def get_collection_transfer_activity_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        collection_id: Annotated[StrictStr, Field(description="Collection ID")],
        payload: Annotated[Optional[IGetCollectionTransferActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Collection Transfer Activity

        Gets transfer activity for a specific collection.  ```tsx await BitBadgesApi.getCollectionTransferActivity(\"123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionTransferActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollectiontransferactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param collection_id: Collection ID (required)
        :type collection_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetCollectionTransferActivityPayload
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

        _param = self._get_collection_transfer_activity_serialize(
            x_api_key=x_api_key,
            collection_id=collection_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionTransferActivitySuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collection_transfer_activity_serialize(
        self,
        x_api_key,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
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
            resource_path='/collection/{collectionId}/activity',
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
    def get_collections_batch(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_collections_payload: IGetCollectionsPayload,
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
    ) -> IGetCollectionsSuccessResponse:
        """Get Collections - Batch

        Retrieves badge collections and associated details. This route is all-inclusive and uses a view-based approach to fetch specific data about collections, including metadata, balances, owners, and more.  ```tsx const res = await BitBadgesApi.getCollections({   collectionsToFetch: [     {       collectionId: 1n,       metadataToFetch: {         badgeIds: [{ start: 1n, end: 10n }],       },       fetchTotalAndMintBalances: true,       viewsToFetch: [         {           viewType: 'owners',           viewId: 'owners',           bookmark: '',         },       ],     },   ], })  const collection = res.collections[0] ```  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (must also be the manager)  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollections)**  Note: This route has lots of legacy features that are planned to be deprecated. For any views, we recommend using the other GET routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_collections_payload: (required)
        :type i_get_collections_payload: IGetCollectionsPayload
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

        _param = self._get_collections_batch_serialize(
            x_api_key=x_api_key,
            i_get_collections_payload=i_get_collections_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionsSuccessResponse",
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
    def get_collections_batch_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_collections_payload: IGetCollectionsPayload,
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
    ) -> ApiResponse[IGetCollectionsSuccessResponse]:
        """Get Collections - Batch

        Retrieves badge collections and associated details. This route is all-inclusive and uses a view-based approach to fetch specific data about collections, including metadata, balances, owners, and more.  ```tsx const res = await BitBadgesApi.getCollections({   collectionsToFetch: [     {       collectionId: 1n,       metadataToFetch: {         badgeIds: [{ start: 1n, end: 10n }],       },       fetchTotalAndMintBalances: true,       viewsToFetch: [         {           viewType: 'owners',           viewId: 'owners',           bookmark: '',         },       ],     },   ], })  const collection = res.collections[0] ```  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (must also be the manager)  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollections)**  Note: This route has lots of legacy features that are planned to be deprecated. For any views, we recommend using the other GET routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_collections_payload: (required)
        :type i_get_collections_payload: IGetCollectionsPayload
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

        _param = self._get_collections_batch_serialize(
            x_api_key=x_api_key,
            i_get_collections_payload=i_get_collections_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionsSuccessResponse",
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
    def get_collections_batch_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_collections_payload: IGetCollectionsPayload,
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
        """Get Collections - Batch

        Retrieves badge collections and associated details. This route is all-inclusive and uses a view-based approach to fetch specific data about collections, including metadata, balances, owners, and more.  ```tsx const res = await BitBadgesApi.getCollections({   collectionsToFetch: [     {       collectionId: 1n,       metadataToFetch: {         badgeIds: [{ start: 1n, end: 10n }],       },       fetchTotalAndMintBalances: true,       viewsToFetch: [         {           viewType: 'owners',           viewId: 'owners',           bookmark: '',         },       ],     },   ], })  const collection = res.collections[0] ```  Scopes: - `readPrivateClaimData` - Required if fetching private claim data (must also be the manager)  Documentation References / Tutorials: - **[Managing Views](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-views)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetCollectionsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getcollections)**  Note: This route has lots of legacy features that are planned to be deprecated. For any views, we recommend using the other GET routes. 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_collections_payload: (required)
        :type i_get_collections_payload: IGetCollectionsPayload
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

        _param = self._get_collections_batch_serialize(
            x_api_key=x_api_key,
            i_get_collections_payload=i_get_collections_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetCollectionsSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_collections_batch_serialize(
        self,
        x_api_key,
        i_get_collections_payload,
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
        if i_get_collections_payload is not None:
            _body_params = i_get_collections_payload


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
            resource_path='/collections',
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
    def get_owners_for_badge(
        self,
        collection_id: Annotated[StrictInt, Field(description="The numeric collection ID.")],
        badge_id: Annotated[StrictInt, Field(description="The numeric badge ID to retrieve owners for.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetOwnersForBadgePayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetOwnersForBadgeSuccessResponse:
        """Get Badge Owners

        Retrieves the owners in a paginated format for a specific badge in a collection. Returns a list of addresses and their corresponding balances for the specified badge ID.  ```tsx const res = await BitBadgesApi.getOwnersForBadge(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getownersforbadge)** 

        :param collection_id: The numeric collection ID. (required)
        :type collection_id: int
        :param badge_id: The numeric badge ID to retrieve owners for. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetOwnersForBadgePayload
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

        _param = self._get_owners_for_badge_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetOwnersForBadgeSuccessResponse",
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
    def get_owners_for_badge_with_http_info(
        self,
        collection_id: Annotated[StrictInt, Field(description="The numeric collection ID.")],
        badge_id: Annotated[StrictInt, Field(description="The numeric badge ID to retrieve owners for.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetOwnersForBadgePayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetOwnersForBadgeSuccessResponse]:
        """Get Badge Owners

        Retrieves the owners in a paginated format for a specific badge in a collection. Returns a list of addresses and their corresponding balances for the specified badge ID.  ```tsx const res = await BitBadgesApi.getOwnersForBadge(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getownersforbadge)** 

        :param collection_id: The numeric collection ID. (required)
        :type collection_id: int
        :param badge_id: The numeric badge ID to retrieve owners for. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetOwnersForBadgePayload
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

        _param = self._get_owners_for_badge_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetOwnersForBadgeSuccessResponse",
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
    def get_owners_for_badge_without_preload_content(
        self,
        collection_id: Annotated[StrictInt, Field(description="The numeric collection ID.")],
        badge_id: Annotated[StrictInt, Field(description="The numeric badge ID to retrieve owners for.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetOwnersForBadgePayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Badge Owners

        Retrieves the owners in a paginated format for a specific badge in a collection. Returns a list of addresses and their corresponding balances for the specified badge ID.  ```tsx const res = await BitBadgesApi.getOwnersForBadge(   collectionId,   badgeId,   {     bookmark: '...'   } ); ```   SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetOwnersForBadgeSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getownersforbadge)** 

        :param collection_id: The numeric collection ID. (required)
        :type collection_id: int
        :param badge_id: The numeric badge ID to retrieve owners for. (required)
        :type badge_id: int
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetOwnersForBadgePayload
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

        _param = self._get_owners_for_badge_serialize(
            collection_id=collection_id,
            badge_id=badge_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetOwnersForBadgeSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_owners_for_badge_serialize(
        self,
        collection_id,
        badge_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        if badge_id is not None:
            _path_params['badgeId'] = badge_id
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
            resource_path='/collection/{collectionId}/{badgeId}/owners',
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
    def get_refresh_status(
        self,
        collection_id: Annotated[StrictStr, Field(description="The collection ID")],
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
    ) -> IRefreshStatusSuccessResponse:
        """Get Refresh Status

        Gets the refresh status for a collection. Used to track if any errors occur during a refresh, or if it is in the queue or not.  ```tsx const res = await BitBadgesApi.getRefreshStatus(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getrefreshstatus)**

        :param collection_id: The collection ID (required)
        :type collection_id: str
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

        _param = self._get_refresh_status_serialize(
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IRefreshStatusSuccessResponse",
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
    def get_refresh_status_with_http_info(
        self,
        collection_id: Annotated[StrictStr, Field(description="The collection ID")],
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
    ) -> ApiResponse[IRefreshStatusSuccessResponse]:
        """Get Refresh Status

        Gets the refresh status for a collection. Used to track if any errors occur during a refresh, or if it is in the queue or not.  ```tsx const res = await BitBadgesApi.getRefreshStatus(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getrefreshstatus)**

        :param collection_id: The collection ID (required)
        :type collection_id: str
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

        _param = self._get_refresh_status_serialize(
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IRefreshStatusSuccessResponse",
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
    def get_refresh_status_without_preload_content(
        self,
        collection_id: Annotated[StrictStr, Field(description="The collection ID")],
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
        """Get Refresh Status

        Gets the refresh status for a collection. Used to track if any errors occur during a refresh, or if it is in the queue or not.  ```tsx const res = await BitBadgesApi.getRefreshStatus(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetRefreshStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getrefreshstatus)**

        :param collection_id: The collection ID (required)
        :type collection_id: str
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

        _param = self._get_refresh_status_serialize(
            collection_id=collection_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IRefreshStatusSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_refresh_status_serialize(
        self,
        collection_id,
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
        if collection_id is not None:
            _path_params['collectionId'] = collection_id
        # process the query parameters
        # process the header parameters
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
            'userIsManager', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/collection/{collectionId}/refreshStatus',
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
    def upload_balances(
        self,
        i_upload_balances_payload: IUploadBalancesPayload,
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
    ) -> object:
        """Upload Balances

        Uploads balances for off-chain indexed balances managed by BitBadges. Note: This only applies to collections with off-chain balances, and the badges must not be frozen / immutable yet.  This uses a queue-system, so it may take a few minutes to process and display in-site.  ```tsx await BitBadgesApi.uploadBalances({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#uploadbalances)**  Scopes:   - `manageOffChainBalances` - Required and also must be current manager

        :param i_upload_balances_payload: (required)
        :type i_upload_balances_payload: IUploadBalancesPayload
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

        _param = self._upload_balances_serialize(
            i_upload_balances_payload=i_upload_balances_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def upload_balances_with_http_info(
        self,
        i_upload_balances_payload: IUploadBalancesPayload,
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
    ) -> ApiResponse[object]:
        """Upload Balances

        Uploads balances for off-chain indexed balances managed by BitBadges. Note: This only applies to collections with off-chain balances, and the badges must not be frozen / immutable yet.  This uses a queue-system, so it may take a few minutes to process and display in-site.  ```tsx await BitBadgesApi.uploadBalances({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#uploadbalances)**  Scopes:   - `manageOffChainBalances` - Required and also must be current manager

        :param i_upload_balances_payload: (required)
        :type i_upload_balances_payload: IUploadBalancesPayload
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

        _param = self._upload_balances_serialize(
            i_upload_balances_payload=i_upload_balances_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def upload_balances_without_preload_content(
        self,
        i_upload_balances_payload: IUploadBalancesPayload,
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
        """Upload Balances

        Uploads balances for off-chain indexed balances managed by BitBadges. Note: This only applies to collections with off-chain balances, and the badges must not be frozen / immutable yet.  This uses a queue-system, so it may take a few minutes to process and display in-site.  ```tsx await BitBadgesApi.uploadBalances({ ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUploadBalancesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#uploadbalances)**  Scopes:   - `manageOffChainBalances` - Required and also must be current manager

        :param i_upload_balances_payload: (required)
        :type i_upload_balances_payload: IUploadBalancesPayload
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

        _param = self._upload_balances_serialize(
            i_upload_balances_payload=i_upload_balances_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _upload_balances_serialize(
        self,
        i_upload_balances_payload,
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
        # process the form parameters
        # process the body parameter
        if i_upload_balances_payload is not None:
            _body_params = i_upload_balances_payload


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
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v0/uploadBalances',
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


