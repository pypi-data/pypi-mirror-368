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
from bitbadgespy_sdk.models.i_calculate_points_payload import ICalculatePointsPayload
from bitbadgespy_sdk.models.i_calculate_points_success_response import ICalculatePointsSuccessResponse
from bitbadgespy_sdk.models.i_create_application_payload import ICreateApplicationPayload
from bitbadgespy_sdk.models.i_create_application_success_response import ICreateApplicationSuccessResponse
from bitbadgespy_sdk.models.i_delete_application_payload import IDeleteApplicationPayload
from bitbadgespy_sdk.models.i_get_application_success_response import IGetApplicationSuccessResponse
from bitbadgespy_sdk.models.i_get_applications_payload import IGetApplicationsPayload
from bitbadgespy_sdk.models.i_get_applications_success_response import IGetApplicationsSuccessResponse
from bitbadgespy_sdk.models.i_get_points_activity_payload import IGetPointsActivityPayload
from bitbadgespy_sdk.models.i_get_points_activity_success_response import IGetPointsActivitySuccessResponse
from bitbadgespy_sdk.models.i_search_applications_payload import ISearchApplicationsPayload
from bitbadgespy_sdk.models.i_search_applications_success_response import ISearchApplicationsSuccessResponse
from bitbadgespy_sdk.models.i_update_application_payload import IUpdateApplicationPayload
from bitbadgespy_sdk.models.i_update_application_success_response import IUpdateApplicationSuccessResponse

from bitbadgespy_sdk.api_client import ApiClient, RequestSerialized
from bitbadgespy_sdk.api_response import ApiResponse
from bitbadgespy_sdk.rest import RESTResponseType


class ApplicationsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def calculate_points(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_calculate_points_payload: ICalculatePointsPayload,
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
    ) -> ICalculatePointsSuccessResponse:
        """Calculate Points

        Calculates points for an application, page, and user.  Note: We use a heavy caching system, so you may not see the results immediately and may be rejected if recently calculated.  ```tsx await BitBadgesApi.calculatePoints(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#calculatepoints)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_calculate_points_payload: (required)
        :type i_calculate_points_payload: ICalculatePointsPayload
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

        _param = self._calculate_points_serialize(
            x_api_key=x_api_key,
            i_calculate_points_payload=i_calculate_points_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICalculatePointsSuccessResponse",
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
    def calculate_points_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_calculate_points_payload: ICalculatePointsPayload,
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
    ) -> ApiResponse[ICalculatePointsSuccessResponse]:
        """Calculate Points

        Calculates points for an application, page, and user.  Note: We use a heavy caching system, so you may not see the results immediately and may be rejected if recently calculated.  ```tsx await BitBadgesApi.calculatePoints(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#calculatepoints)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_calculate_points_payload: (required)
        :type i_calculate_points_payload: ICalculatePointsPayload
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

        _param = self._calculate_points_serialize(
            x_api_key=x_api_key,
            i_calculate_points_payload=i_calculate_points_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICalculatePointsSuccessResponse",
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
    def calculate_points_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_calculate_points_payload: ICalculatePointsPayload,
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
        """Calculate Points

        Calculates points for an application, page, and user.  Note: We use a heavy caching system, so you may not see the results immediately and may be rejected if recently calculated.  ```tsx await BitBadgesApi.calculatePoints(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCalculatePointsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#calculatepoints)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_calculate_points_payload: (required)
        :type i_calculate_points_payload: ICalculatePointsPayload
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

        _param = self._calculate_points_serialize(
            x_api_key=x_api_key,
            i_calculate_points_payload=i_calculate_points_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICalculatePointsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _calculate_points_serialize(
        self,
        x_api_key,
        i_calculate_points_payload,
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
        if i_calculate_points_payload is not None:
            _body_params = i_calculate_points_payload


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
            resource_path='/applications/points',
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
    def create_application(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_application_payload: ICreateApplicationPayload,
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
    ) -> ICreateApplicationSuccessResponse:
        """Create Application

        Creates an application.  ```tsx await BitBadgesApi.createApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_application_payload: (required)
        :type i_create_application_payload: ICreateApplicationPayload
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

        _param = self._create_application_serialize(
            x_api_key=x_api_key,
            i_create_application_payload=i_create_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateApplicationSuccessResponse",
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
    def create_application_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_application_payload: ICreateApplicationPayload,
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
    ) -> ApiResponse[ICreateApplicationSuccessResponse]:
        """Create Application

        Creates an application.  ```tsx await BitBadgesApi.createApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_application_payload: (required)
        :type i_create_application_payload: ICreateApplicationPayload
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

        _param = self._create_application_serialize(
            x_api_key=x_api_key,
            i_create_application_payload=i_create_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateApplicationSuccessResponse",
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
    def create_application_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_application_payload: ICreateApplicationPayload,
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
        """Create Application

        Creates an application.  ```tsx await BitBadgesApi.createApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_application_payload: (required)
        :type i_create_application_payload: ICreateApplicationPayload
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

        _param = self._create_application_serialize(
            x_api_key=x_api_key,
            i_create_application_payload=i_create_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICreateApplicationSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _create_application_serialize(
        self,
        x_api_key,
        i_create_application_payload,
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
        if i_create_application_payload is not None:
            _body_params = i_create_application_payload


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
            'userIsOwner', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/applications',
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
    def delete_application(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_application_payload: IDeleteApplicationPayload,
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
        """Delete Application

        Deletes an application.  ```tsx await BitBadgesApi.deleteApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_application_payload: (required)
        :type i_delete_application_payload: IDeleteApplicationPayload
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

        _param = self._delete_application_serialize(
            x_api_key=x_api_key,
            i_delete_application_payload=i_delete_application_payload,
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
    def delete_application_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_application_payload: IDeleteApplicationPayload,
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
        """Delete Application

        Deletes an application.  ```tsx await BitBadgesApi.deleteApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_application_payload: (required)
        :type i_delete_application_payload: IDeleteApplicationPayload
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

        _param = self._delete_application_serialize(
            x_api_key=x_api_key,
            i_delete_application_payload=i_delete_application_payload,
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
    def delete_application_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_application_payload: IDeleteApplicationPayload,
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
        """Delete Application

        Deletes an application.  ```tsx await BitBadgesApi.deleteApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_application_payload: (required)
        :type i_delete_application_payload: IDeleteApplicationPayload
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

        _param = self._delete_application_serialize(
            x_api_key=x_api_key,
            i_delete_application_payload=i_delete_application_payload,
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


    def _delete_application_serialize(
        self,
        x_api_key,
        i_delete_application_payload,
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
        if i_delete_application_payload is not None:
            _body_params = i_delete_application_payload


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
            'userIsOwner', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/applications',
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
    def get_application(
        self,
        application_id: Annotated[StrictStr, Field(description="Application ID")],
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
    ) -> IGetApplicationSuccessResponse:
        """Get Application

        Gets an application by specific ID.  ```tsx await BitBadgesApi.getApplication(\"application123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplication)**

        :param application_id: Application ID (required)
        :type application_id: str
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

        _param = self._get_application_serialize(
            application_id=application_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationSuccessResponse",
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
    def get_application_with_http_info(
        self,
        application_id: Annotated[StrictStr, Field(description="Application ID")],
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
    ) -> ApiResponse[IGetApplicationSuccessResponse]:
        """Get Application

        Gets an application by specific ID.  ```tsx await BitBadgesApi.getApplication(\"application123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplication)**

        :param application_id: Application ID (required)
        :type application_id: str
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

        _param = self._get_application_serialize(
            application_id=application_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationSuccessResponse",
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
    def get_application_without_preload_content(
        self,
        application_id: Annotated[StrictStr, Field(description="Application ID")],
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
        """Get Application

        Gets an application by specific ID.  ```tsx await BitBadgesApi.getApplication(\"application123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplication)**

        :param application_id: Application ID (required)
        :type application_id: str
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

        _param = self._get_application_serialize(
            application_id=application_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_application_serialize(
        self,
        application_id,
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
        if application_id is not None:
            _path_params['applicationId'] = application_id
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
            resource_path='/application/{applicationId}',
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
    def get_applications(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_applications_payload: IGetApplicationsPayload,
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
    ) -> IGetApplicationsSuccessResponse:
        """Get Applications - Batch

        Fetches applications based on the provided criteria.  ```tsx await BitBadgesApi.getApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplications)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_applications_payload: (required)
        :type i_get_applications_payload: IGetApplicationsPayload
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

        _param = self._get_applications_serialize(
            x_api_key=x_api_key,
            i_get_applications_payload=i_get_applications_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationsSuccessResponse",
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
    def get_applications_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_applications_payload: IGetApplicationsPayload,
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
    ) -> ApiResponse[IGetApplicationsSuccessResponse]:
        """Get Applications - Batch

        Fetches applications based on the provided criteria.  ```tsx await BitBadgesApi.getApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplications)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_applications_payload: (required)
        :type i_get_applications_payload: IGetApplicationsPayload
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

        _param = self._get_applications_serialize(
            x_api_key=x_api_key,
            i_get_applications_payload=i_get_applications_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationsSuccessResponse",
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
    def get_applications_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_get_applications_payload: IGetApplicationsPayload,
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
        """Get Applications - Batch

        Fetches applications based on the provided criteria.  ```tsx await BitBadgesApi.getApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getapplications)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_get_applications_payload: (required)
        :type i_get_applications_payload: IGetApplicationsPayload
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

        _param = self._get_applications_serialize(
            x_api_key=x_api_key,
            i_get_applications_payload=i_get_applications_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetApplicationsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_applications_serialize(
        self,
        x_api_key,
        i_get_applications_payload,
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
        if i_get_applications_payload is not None:
            _body_params = i_get_applications_payload


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
            resource_path='/applications/fetch',
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
    def get_points_activity(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetPointsActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetPointsActivitySuccessResponse:
        """Get Points Activity

        Fetches points activity for an application.  ```tsx await BitBadgesApi.getPointsActivity(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityPayload
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

        _param = self._get_points_activity_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivitySuccessResponse",
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
    def get_points_activity_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetPointsActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetPointsActivitySuccessResponse]:
        """Get Points Activity

        Fetches points activity for an application.  ```tsx await BitBadgesApi.getPointsActivity(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityPayload
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

        _param = self._get_points_activity_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivitySuccessResponse",
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
    def get_points_activity_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[IGetPointsActivityPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Points Activity

        Fetches points activity for an application.  ```tsx await BitBadgesApi.getPointsActivity(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivityPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetPointsActivitySuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getpointsactivity)**

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetPointsActivityPayload
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

        _param = self._get_points_activity_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetPointsActivitySuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_points_activity_serialize(
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
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/applications/points/activity',
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
    def search_applications(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchApplicationsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ISearchApplicationsSuccessResponse:
        """Search Applications

        Searches for applications based on the provided criteria. Currently, this only gets the signed in user's applications.  ```tsx await BitBadgesApi.searchApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchapplications)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchApplicationsPayload
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

        _param = self._search_applications_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchApplicationsSuccessResponse",
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
    def search_applications_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchApplicationsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[ISearchApplicationsSuccessResponse]:
        """Search Applications

        Searches for applications based on the provided criteria. Currently, this only gets the signed in user's applications.  ```tsx await BitBadgesApi.searchApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchapplications)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchApplicationsPayload
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

        _param = self._search_applications_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchApplicationsSuccessResponse",
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
    def search_applications_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: Annotated[Optional[ISearchApplicationsPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Search Applications

        Searches for applications based on the provided criteria. Currently, this only gets the signed in user's applications.  ```tsx await BitBadgesApi.searchApplications(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchApplicationsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchapplications)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: ISearchApplicationsPayload
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

        _param = self._search_applications_serialize(
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchApplicationsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _search_applications_serialize(
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
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/applications/search',
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
    def update_application(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_application_payload: IUpdateApplicationPayload,
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
    ) -> IUpdateApplicationSuccessResponse:
        """Update Application

        Updates an application.  ```tsx await BitBadgesApi.updateApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_application_payload: (required)
        :type i_update_application_payload: IUpdateApplicationPayload
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

        _param = self._update_application_serialize(
            x_api_key=x_api_key,
            i_update_application_payload=i_update_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateApplicationSuccessResponse",
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
    def update_application_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_application_payload: IUpdateApplicationPayload,
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
    ) -> ApiResponse[IUpdateApplicationSuccessResponse]:
        """Update Application

        Updates an application.  ```tsx await BitBadgesApi.updateApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_application_payload: (required)
        :type i_update_application_payload: IUpdateApplicationPayload
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

        _param = self._update_application_serialize(
            x_api_key=x_api_key,
            i_update_application_payload=i_update_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateApplicationSuccessResponse",
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
    def update_application_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_application_payload: IUpdateApplicationPayload,
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
        """Update Application

        Updates an application.  ```tsx await BitBadgesApi.updateApplication(...); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateApplicationSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateapplication)**  Scopes: - `manageApplications` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_application_payload: (required)
        :type i_update_application_payload: IUpdateApplicationPayload
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

        _param = self._update_application_serialize(
            x_api_key=x_api_key,
            i_update_application_payload=i_update_application_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IUpdateApplicationSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_application_serialize(
        self,
        x_api_key,
        i_update_application_payload,
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
        if i_update_application_payload is not None:
            _body_params = i_update_application_payload


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
            'userIsOwner', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/applications',
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


