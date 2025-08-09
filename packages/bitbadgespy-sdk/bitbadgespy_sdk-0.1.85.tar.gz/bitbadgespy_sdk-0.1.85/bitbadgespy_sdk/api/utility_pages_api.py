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
from typing import Any, Dict, Optional
from typing_extensions import Annotated
from bitbadgespy_sdk.models.i_create_utility_page_payload import ICreateUtilityPagePayload
from bitbadgespy_sdk.models.i_create_utility_page_success_response import ICreateUtilityPageSuccessResponse
from bitbadgespy_sdk.models.i_delete_utility_page_payload import IDeleteUtilityPagePayload
from bitbadgespy_sdk.models.i_get_utility_page_success_response import IGetUtilityPageSuccessResponse
from bitbadgespy_sdk.models.i_get_utility_pages_payload import IGetUtilityPagesPayload
from bitbadgespy_sdk.models.i_get_utility_pages_success_response import IGetUtilityPagesSuccessResponse
from bitbadgespy_sdk.models.i_search_utility_pages_payload import ISearchUtilityPagesPayload
from bitbadgespy_sdk.models.i_search_utility_pages_success_response import ISearchUtilityPagesSuccessResponse
from bitbadgespy_sdk.models.i_update_utility_page_payload import IUpdateUtilityPagePayload
from bitbadgespy_sdk.models.i_update_utility_page_success_response import IUpdateUtilityPageSuccessResponse

from bitbadgespy_sdk.api_client import ApiClient, RequestSerialized
from bitbadgespy_sdk.api_response import ApiResponse
from bitbadgespy_sdk.rest import RESTResponseType


class UtilityPagesApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def create_utility_page(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_utility_page_payload: ICreateUtilityPagePayload,
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
    ) -> ICreateUtilityPageSuccessResponse:
        """Create Utility Page

        Creates a new utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.createUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_utility_page_payload: (required)
        :type i_create_utility_page_payload: ICreateUtilityPagePayload
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

        _param = self._create_utility_page_serialize(
            x_api_key=x_api_key,
            i_create_utility_page_payload=i_create_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateUtilityPageSuccessResponse",
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
    def create_utility_page_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_utility_page_payload: ICreateUtilityPagePayload,
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
    ) -> ApiResponse[ICreateUtilityPageSuccessResponse]:
        """Create Utility Page

        Creates a new utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.createUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_utility_page_payload: (required)
        :type i_create_utility_page_payload: ICreateUtilityPagePayload
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

        _param = self._create_utility_page_serialize(
            x_api_key=x_api_key,
            i_create_utility_page_payload=i_create_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateUtilityPageSuccessResponse",
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
    def create_utility_page_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_utility_page_payload: ICreateUtilityPagePayload,
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
        """Create Utility Page

        Creates a new utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.createUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_utility_page_payload: (required)
        :type i_create_utility_page_payload: ICreateUtilityPagePayload
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

        _param = self._create_utility_page_serialize(
            x_api_key=x_api_key,
            i_create_utility_page_payload=i_create_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateUtilityPageSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _create_utility_page_serialize(
        self,
        x_api_key,
        i_create_utility_page_payload,
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
        if i_create_utility_page_payload is not None:
            _body_params = i_create_utility_page_payload


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
            'apiKey', 
            'userSignedIn'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/utilityPages',
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
    def delete_utility_page(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_utility_page_payload: IDeleteUtilityPagePayload,
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
        """Delete Utility Page

        Deletes a utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.deleteUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_utility_page_payload: (required)
        :type i_delete_utility_page_payload: IDeleteUtilityPagePayload
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

        _param = self._delete_utility_page_serialize(
            x_api_key=x_api_key,
            i_delete_utility_page_payload=i_delete_utility_page_payload,
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
    def delete_utility_page_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_utility_page_payload: IDeleteUtilityPagePayload,
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
        """Delete Utility Page

        Deletes a utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.deleteUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_utility_page_payload: (required)
        :type i_delete_utility_page_payload: IDeleteUtilityPagePayload
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

        _param = self._delete_utility_page_serialize(
            x_api_key=x_api_key,
            i_delete_utility_page_payload=i_delete_utility_page_payload,
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
    def delete_utility_page_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_utility_page_payload: IDeleteUtilityPagePayload,
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
        """Delete Utility Page

        Deletes a utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.deleteUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_utility_page_payload: (required)
        :type i_delete_utility_page_payload: IDeleteUtilityPagePayload
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

        _param = self._delete_utility_page_serialize(
            x_api_key=x_api_key,
            i_delete_utility_page_payload=i_delete_utility_page_payload,
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


    def _delete_utility_page_serialize(
        self,
        x_api_key,
        i_delete_utility_page_payload,
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
        if i_delete_utility_page_payload is not None:
            _body_params = i_delete_utility_page_payload


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
            'apiKey', 
            'userSignedIn'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/utilityPages',
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
    def get_utility_page(
        self,
        utility_page_id: Annotated[StrictStr, Field(description="Utility listing ID")],
        payload: Annotated[Optional[Dict[str, Any]], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetUtilityPageSuccessResponse:
        """Get Utility Page

        Gets a utility page by specific ID.  ```tsx await BitBadgesApi.getUtilityPage(\"utilityPage123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylisting)**  Scopes:   - `manageUtilityPages` - Required and must have view permissions for private listings

        :param utility_page_id: Utility listing ID (required)
        :type utility_page_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: object
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

        _param = self._get_utility_page_serialize(
            utility_page_id=utility_page_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPageSuccessResponse",
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
    def get_utility_page_with_http_info(
        self,
        utility_page_id: Annotated[StrictStr, Field(description="Utility listing ID")],
        payload: Annotated[Optional[Dict[str, Any]], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetUtilityPageSuccessResponse]:
        """Get Utility Page

        Gets a utility page by specific ID.  ```tsx await BitBadgesApi.getUtilityPage(\"utilityPage123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylisting)**  Scopes:   - `manageUtilityPages` - Required and must have view permissions for private listings

        :param utility_page_id: Utility listing ID (required)
        :type utility_page_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: object
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

        _param = self._get_utility_page_serialize(
            utility_page_id=utility_page_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPageSuccessResponse",
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
    def get_utility_page_without_preload_content(
        self,
        utility_page_id: Annotated[StrictStr, Field(description="Utility listing ID")],
        payload: Annotated[Optional[Dict[str, Any]], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Utility Page

        Gets a utility page by specific ID.  ```tsx await BitBadgesApi.getUtilityPage(\"utilityPage123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylisting)**  Scopes:   - `manageUtilityPages` - Required and must have view permissions for private listings

        :param utility_page_id: Utility listing ID (required)
        :type utility_page_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: object
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

        _param = self._get_utility_page_serialize(
            utility_page_id=utility_page_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPageSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_utility_page_serialize(
        self,
        utility_page_id,
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
        if utility_page_id is not None:
            _path_params['utilityPageId'] = utility_page_id
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
            resource_path='/utilityPage/{utilityPageId}',
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
    def get_utility_pages(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_utility_pages_payload: IGetUtilityPagesPayload,
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
    ) -> IGetUtilityPagesSuccessResponse:
        """Get Utility Pages - Batch

        Fetches utility pages based on the provided criteria.  Requires authentication for private listings.  ```tsx await BitBadgesApi.getUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylistings)**  Scopes: - `manageUtilityPages` - Required for private listings

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_utility_pages_payload: (required)
        :type i_get_utility_pages_payload: IGetUtilityPagesPayload
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

        _param = self._get_utility_pages_serialize(
            x_api_key=x_api_key,
            i_get_utility_pages_payload=i_get_utility_pages_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPagesSuccessResponse",
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
    def get_utility_pages_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_utility_pages_payload: IGetUtilityPagesPayload,
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
    ) -> ApiResponse[IGetUtilityPagesSuccessResponse]:
        """Get Utility Pages - Batch

        Fetches utility pages based on the provided criteria.  Requires authentication for private listings.  ```tsx await BitBadgesApi.getUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylistings)**  Scopes: - `manageUtilityPages` - Required for private listings

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_utility_pages_payload: (required)
        :type i_get_utility_pages_payload: IGetUtilityPagesPayload
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

        _param = self._get_utility_pages_serialize(
            x_api_key=x_api_key,
            i_get_utility_pages_payload=i_get_utility_pages_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPagesSuccessResponse",
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
    def get_utility_pages_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_utility_pages_payload: IGetUtilityPagesPayload,
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
        """Get Utility Pages - Batch

        Fetches utility pages based on the provided criteria.  Requires authentication for private listings.  ```tsx await BitBadgesApi.getUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getutilitylistings)**  Scopes: - `manageUtilityPages` - Required for private listings

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_utility_pages_payload: (required)
        :type i_get_utility_pages_payload: IGetUtilityPagesPayload
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

        _param = self._get_utility_pages_serialize(
            x_api_key=x_api_key,
            i_get_utility_pages_payload=i_get_utility_pages_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetUtilityPagesSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_utility_pages_serialize(
        self,
        x_api_key,
        i_get_utility_pages_payload,
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
        if i_get_utility_pages_payload is not None:
            _body_params = i_get_utility_pages_payload


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
            resource_path='/utilityPages/fetch',
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
    def search_utility_pages(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchUtilityPagesPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ISearchUtilityPagesSuccessResponse:
        """Search Utility Pages

        Searches for utility pages based on the provided criteria. Currently, this only gets the signed in user's utility pages.  ```tsx   await BitBadgesApi.searchUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchutilitylistings)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchUtilityPagesPayload
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

        _param = self._search_utility_pages_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchUtilityPagesSuccessResponse",
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
    def search_utility_pages_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchUtilityPagesPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[ISearchUtilityPagesSuccessResponse]:
        """Search Utility Pages

        Searches for utility pages based on the provided criteria. Currently, this only gets the signed in user's utility pages.  ```tsx   await BitBadgesApi.searchUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchutilitylistings)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchUtilityPagesPayload
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

        _param = self._search_utility_pages_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchUtilityPagesSuccessResponse",
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
    def search_utility_pages_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchUtilityPagesPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Search Utility Pages

        Searches for utility pages based on the provided criteria. Currently, this only gets the signed in user's utility pages.  ```tsx   await BitBadgesApi.searchUtilityPages(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchUtilityPagesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchutilitylistings)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchUtilityPagesPayload
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

        _param = self._search_utility_pages_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchUtilityPagesSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _search_utility_pages_serialize(
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
            'apiKey', 
            'userSignedIn'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/utilityPages/search',
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
    def update_utility_page(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_utility_page_payload: IUpdateUtilityPagePayload,
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
    ) -> IUpdateUtilityPageSuccessResponse:
        """Update Utility Page

        Updates an existing utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.updateUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_utility_page_payload: (required)
        :type i_update_utility_page_payload: IUpdateUtilityPagePayload
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

        _param = self._update_utility_page_serialize(
            x_api_key=x_api_key,
            i_update_utility_page_payload=i_update_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateUtilityPageSuccessResponse",
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
    def update_utility_page_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_utility_page_payload: IUpdateUtilityPagePayload,
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
    ) -> ApiResponse[IUpdateUtilityPageSuccessResponse]:
        """Update Utility Page

        Updates an existing utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.updateUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_utility_page_payload: (required)
        :type i_update_utility_page_payload: IUpdateUtilityPagePayload
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

        _param = self._update_utility_page_serialize(
            x_api_key=x_api_key,
            i_update_utility_page_payload=i_update_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateUtilityPageSuccessResponse",
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
    def update_utility_page_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_utility_page_payload: IUpdateUtilityPagePayload,
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
        """Update Utility Page

        Updates an existing utility page. This is also available in the developer portal.  ```tsx await BitBadgesApi.updateUtilityPage(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPagePayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateUtilityPageSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateutilitylisting)**  Scopes: - `manageUtilityPages` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_utility_page_payload: (required)
        :type i_update_utility_page_payload: IUpdateUtilityPagePayload
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

        _param = self._update_utility_page_serialize(
            x_api_key=x_api_key,
            i_update_utility_page_payload=i_update_utility_page_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateUtilityPageSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_utility_page_serialize(
        self,
        x_api_key,
        i_update_utility_page_payload,
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
        if i_update_utility_page_payload is not None:
            _body_params = i_update_utility_page_payload


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
            'apiKey', 
            'userSignedIn'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/utilityPages',
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


