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
from bitbadgespy_sdk.models.generate_code200_response import GenerateCode200Response
from bitbadgespy_sdk.models.i_check_claim_success_success_response import ICheckClaimSuccessSuccessResponse
from bitbadgespy_sdk.models.i_complete_claim_payload import ICompleteClaimPayload
from bitbadgespy_sdk.models.i_complete_claim_success_response import ICompleteClaimSuccessResponse
from bitbadgespy_sdk.models.i_create_claim_payload import ICreateClaimPayload
from bitbadgespy_sdk.models.i_delete_claim_payload import IDeleteClaimPayload
from bitbadgespy_sdk.models.i_get_attempt_data_from_request_bin_payload import IGetAttemptDataFromRequestBinPayload
from bitbadgespy_sdk.models.i_get_attempt_data_from_request_bin_success_response import IGetAttemptDataFromRequestBinSuccessResponse
from bitbadgespy_sdk.models.i_get_claim_attempt_status_success_response import IGetClaimAttemptStatusSuccessResponse
from bitbadgespy_sdk.models.i_get_claim_attempts_payload import IGetClaimAttemptsPayload
from bitbadgespy_sdk.models.i_get_claim_attempts_success_response import IGetClaimAttemptsSuccessResponse
from bitbadgespy_sdk.models.i_get_claim_payload import IGetClaimPayload
from bitbadgespy_sdk.models.i_get_claim_success_response import IGetClaimSuccessResponse
from bitbadgespy_sdk.models.i_get_claims_payload_v1 import IGetClaimsPayloadV1
from bitbadgespy_sdk.models.i_get_claims_success_response import IGetClaimsSuccessResponse
from bitbadgespy_sdk.models.i_get_gated_content_for_claim_success_response import IGetGatedContentForClaimSuccessResponse
from bitbadgespy_sdk.models.i_get_reserved_claim_codes_success_response import IGetReservedClaimCodesSuccessResponse
from bitbadgespy_sdk.models.i_search_claims_payload import ISearchClaimsPayload
from bitbadgespy_sdk.models.i_search_claims_success_response import ISearchClaimsSuccessResponse
from bitbadgespy_sdk.models.i_simulate_claim_payload import ISimulateClaimPayload
from bitbadgespy_sdk.models.i_simulate_claim_success_response import ISimulateClaimSuccessResponse
from bitbadgespy_sdk.models.i_update_claim_payload import IUpdateClaimPayload

from bitbadgespy_sdk.api_client import ApiClient, RequestSerialized
from bitbadgespy_sdk.api_response import ApiResponse
from bitbadgespy_sdk.rest import RESTResponseType


class ClaimsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def check_claim_success(
        self,
        claim_id: StrictStr,
        address: StrictStr,
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
    ) -> ICheckClaimSuccessSuccessResponse:
        """Check Claim Successes By User

        Checks if a claim has been successfully completed.  This returns a success count based on how many times the user has completed the claim.  For on-demand claims, this will return 1 if the user has completed the claim. For indexed claims, this will return the number of times the user has completed the claim.  Note that this will not work if the claim hides its state.  ```tsx const res = await BitBadgesApi.checkClaimSuccess(claimId, address); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#checkclaimsuccess)** 

        :param claim_id: (required)
        :type claim_id: str
        :param address: (required)
        :type address: str
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

        _param = self._check_claim_success_serialize(
            claim_id=claim_id,
            address=address,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICheckClaimSuccessSuccessResponse",
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
    def check_claim_success_with_http_info(
        self,
        claim_id: StrictStr,
        address: StrictStr,
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
    ) -> ApiResponse[ICheckClaimSuccessSuccessResponse]:
        """Check Claim Successes By User

        Checks if a claim has been successfully completed.  This returns a success count based on how many times the user has completed the claim.  For on-demand claims, this will return 1 if the user has completed the claim. For indexed claims, this will return the number of times the user has completed the claim.  Note that this will not work if the claim hides its state.  ```tsx const res = await BitBadgesApi.checkClaimSuccess(claimId, address); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#checkclaimsuccess)** 

        :param claim_id: (required)
        :type claim_id: str
        :param address: (required)
        :type address: str
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

        _param = self._check_claim_success_serialize(
            claim_id=claim_id,
            address=address,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICheckClaimSuccessSuccessResponse",
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
    def check_claim_success_without_preload_content(
        self,
        claim_id: StrictStr,
        address: StrictStr,
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
        """Check Claim Successes By User

        Checks if a claim has been successfully completed.  This returns a success count based on how many times the user has completed the claim.  For on-demand claims, this will return 1 if the user has completed the claim. For indexed claims, this will return the number of times the user has completed the claim.  Note that this will not work if the claim hides its state.  ```tsx const res = await BitBadgesApi.checkClaimSuccess(claimId, address); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCheckClaimSuccessSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#checkclaimsuccess)** 

        :param claim_id: (required)
        :type claim_id: str
        :param address: (required)
        :type address: str
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

        _param = self._check_claim_success_serialize(
            claim_id=claim_id,
            address=address,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICheckClaimSuccessSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _check_claim_success_serialize(
        self,
        claim_id,
        address,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
        if address is not None:
            _path_params['address'] = address
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
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/claims/success/{claimId}/{address}',
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
    def complete_claim(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_complete_claim_payload: ICompleteClaimPayload,
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
    ) -> ICompleteClaimSuccessResponse:
        """Complete Claim

        Completes a claim for a specific address. This triggers a complete claim request to be sent to the queue. Note, this route returning a success code does not mean the claim has been completed. You will need to fetch its status via the attempt ID.  If you want to simulate the claim first, you can use the simulate claim endpoint.  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  ```tsx const res = await BitBadgesApi.completeClaim(claimId, address, { _expectedVersion: 1, ...body }); console.log(res.claimAttemptId);  //Sleep 2 seconds  const res = await BitBadgesApi.getClaimAttemptStatus(res.claimAttemptId); console.log(res) // { success: true } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#completeclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in 

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_complete_claim_payload: (required)
        :type i_complete_claim_payload: ICompleteClaimPayload
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

        _param = self._complete_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_complete_claim_payload=i_complete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICompleteClaimSuccessResponse",
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
    def complete_claim_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_complete_claim_payload: ICompleteClaimPayload,
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
    ) -> ApiResponse[ICompleteClaimSuccessResponse]:
        """Complete Claim

        Completes a claim for a specific address. This triggers a complete claim request to be sent to the queue. Note, this route returning a success code does not mean the claim has been completed. You will need to fetch its status via the attempt ID.  If you want to simulate the claim first, you can use the simulate claim endpoint.  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  ```tsx const res = await BitBadgesApi.completeClaim(claimId, address, { _expectedVersion: 1, ...body }); console.log(res.claimAttemptId);  //Sleep 2 seconds  const res = await BitBadgesApi.getClaimAttemptStatus(res.claimAttemptId); console.log(res) // { success: true } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#completeclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in 

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_complete_claim_payload: (required)
        :type i_complete_claim_payload: ICompleteClaimPayload
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

        _param = self._complete_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_complete_claim_payload=i_complete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICompleteClaimSuccessResponse",
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
    def complete_claim_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_complete_claim_payload: ICompleteClaimPayload,
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
        """Complete Claim

        Completes a claim for a specific address. This triggers a complete claim request to be sent to the queue. Note, this route returning a success code does not mean the claim has been completed. You will need to fetch its status via the attempt ID.  If you want to simulate the claim first, you can use the simulate claim endpoint.  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  ```tsx const res = await BitBadgesApi.completeClaim(claimId, address, { _expectedVersion: 1, ...body }); console.log(res.claimAttemptId);  //Sleep 2 seconds  const res = await BitBadgesApi.getClaimAttemptStatus(res.claimAttemptId); console.log(res) // { success: true } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCompleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#completeclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in 

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_complete_claim_payload: (required)
        :type i_complete_claim_payload: ICompleteClaimPayload
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

        _param = self._complete_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_complete_claim_payload=i_complete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ICompleteClaimSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _complete_claim_serialize(
        self,
        claim_id,
        address,
        x_api_key,
        i_complete_claim_payload,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter
        if i_complete_claim_payload is not None:
            _body_params = i_complete_claim_payload


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
            resource_path='/claims/complete/{claimId}/{address}',
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
    def create_claim(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_claim_payload: ICreateClaimPayload,
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
        """Create Claim

        Creates a new claim.  Note: Creating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first. You may also opt to leave the creation in-site but update claims via the API instead.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated. - Linked to on-chain approvals (user or collection level) - This is advanced. If you need this, please reach out to us. Updates are fine, but creation uses an advanced processs that is undocumented currently.  ```tsx const res = await BitBadgesApi.createClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_claim_payload: (required)
        :type i_create_claim_payload: ICreateClaimPayload
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

        _param = self._create_claim_serialize(
            x_api_key=x_api_key,
            i_create_claim_payload=i_create_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def create_claim_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_claim_payload: ICreateClaimPayload,
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
        """Create Claim

        Creates a new claim.  Note: Creating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first. You may also opt to leave the creation in-site but update claims via the API instead.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated. - Linked to on-chain approvals (user or collection level) - This is advanced. If you need this, please reach out to us. Updates are fine, but creation uses an advanced processs that is undocumented currently.  ```tsx const res = await BitBadgesApi.createClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_claim_payload: (required)
        :type i_create_claim_payload: ICreateClaimPayload
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

        _param = self._create_claim_serialize(
            x_api_key=x_api_key,
            i_create_claim_payload=i_create_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def create_claim_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_create_claim_payload: ICreateClaimPayload,
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
        """Create Claim

        Creates a new claim.  Note: Creating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first. You may also opt to leave the creation in-site but update claims via the API instead.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated. - Linked to on-chain approvals (user or collection level) - This is advanced. If you need this, please reach out to us. Updates are fine, but creation uses an advanced processs that is undocumented currently.  ```tsx const res = await BitBadgesApi.createClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iCreateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#createclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_create_claim_payload: (required)
        :type i_create_claim_payload: ICreateClaimPayload
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

        _param = self._create_claim_serialize(
            x_api_key=x_api_key,
            i_create_claim_payload=i_create_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _create_claim_serialize(
        self,
        x_api_key,
        i_create_claim_payload,
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
        if i_create_claim_payload is not None:
            _body_params = i_create_claim_payload


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
            resource_path='/claims',
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
    def delete_claim(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_claim_payload: IDeleteClaimPayload,
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
        """Delete Claim

        Deletes a claim. Creating and maintaining claims are typically recommended to be done through the site, not the API, because they require special configuration.  ```tsx const res = await BitBadgesApi.deleteClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteclaims)**  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_claim_payload: (required)
        :type i_delete_claim_payload: IDeleteClaimPayload
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

        _param = self._delete_claim_serialize(
            x_api_key=x_api_key,
            i_delete_claim_payload=i_delete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def delete_claim_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_claim_payload: IDeleteClaimPayload,
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
        """Delete Claim

        Deletes a claim. Creating and maintaining claims are typically recommended to be done through the site, not the API, because they require special configuration.  ```tsx const res = await BitBadgesApi.deleteClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteclaims)**  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_claim_payload: (required)
        :type i_delete_claim_payload: IDeleteClaimPayload
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

        _param = self._delete_claim_serialize(
            x_api_key=x_api_key,
            i_delete_claim_payload=i_delete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def delete_claim_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_delete_claim_payload: IDeleteClaimPayload,
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
        """Delete Claim

        Deletes a claim. Creating and maintaining claims are typically recommended to be done through the site, not the API, because they require special configuration.  ```tsx const res = await BitBadgesApi.deleteClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iDeleteClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#deleteclaims)**  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for linked address list claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_delete_claim_payload: (required)
        :type i_delete_claim_payload: IDeleteClaimPayload
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

        _param = self._delete_claim_serialize(
            x_api_key=x_api_key,
            i_delete_claim_payload=i_delete_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _delete_claim_serialize(
        self,
        x_api_key,
        i_delete_claim_payload,
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
        if i_delete_claim_payload is not None:
            _body_params = i_delete_claim_payload


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
            resource_path='/claims',
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
    def generate_code(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        seed_code: Annotated[StrictStr, Field(description="The seed used to generate the code")],
        idx: Annotated[int, Field(strict=True, ge=0, description="The index of the code to generate")],
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
    ) -> GenerateCode200Response:
        """Get Code (Codes Plugin)

        Generates a unique code based on a seed and a zero-based index. This is used for the Codes plugin with claims.  Documentation References / Tutorials: - **[Codes Plugin](https://docs.bitbadges.io/for-developers/claim-builder/universal-approach-claim-codes)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param seed_code: The seed used to generate the code (required)
        :type seed_code: str
        :param idx: The index of the code to generate (required)
        :type idx: int
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

        _param = self._generate_code_serialize(
            x_api_key=x_api_key,
            seed_code=seed_code,
            idx=idx,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GenerateCode200Response",
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
    def generate_code_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        seed_code: Annotated[StrictStr, Field(description="The seed used to generate the code")],
        idx: Annotated[int, Field(strict=True, ge=0, description="The index of the code to generate")],
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
    ) -> ApiResponse[GenerateCode200Response]:
        """Get Code (Codes Plugin)

        Generates a unique code based on a seed and a zero-based index. This is used for the Codes plugin with claims.  Documentation References / Tutorials: - **[Codes Plugin](https://docs.bitbadges.io/for-developers/claim-builder/universal-approach-claim-codes)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param seed_code: The seed used to generate the code (required)
        :type seed_code: str
        :param idx: The index of the code to generate (required)
        :type idx: int
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

        _param = self._generate_code_serialize(
            x_api_key=x_api_key,
            seed_code=seed_code,
            idx=idx,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GenerateCode200Response",
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
    def generate_code_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        seed_code: Annotated[StrictStr, Field(description="The seed used to generate the code")],
        idx: Annotated[int, Field(strict=True, ge=0, description="The index of the code to generate")],
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
        """Get Code (Codes Plugin)

        Generates a unique code based on a seed and a zero-based index. This is used for the Codes plugin with claims.  Documentation References / Tutorials: - **[Codes Plugin](https://docs.bitbadges.io/for-developers/claim-builder/universal-approach-claim-codes)** 

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param seed_code: The seed used to generate the code (required)
        :type seed_code: str
        :param idx: The index of the code to generate (required)
        :type idx: int
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

        _param = self._generate_code_serialize(
            x_api_key=x_api_key,
            seed_code=seed_code,
            idx=idx,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "GenerateCode200Response",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _generate_code_serialize(
        self,
        x_api_key,
        seed_code,
        idx,
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
        if seed_code is not None:
            
            _query_params.append(('seedCode', seed_code))
            
        if idx is not None:
            
            _query_params.append(('idx', idx))
            
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
            resource_path='/codes',
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
    def get_attempt_data_from_request_bin(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        claim_attempt_id: Annotated[StrictStr, Field(description="Claim attempt ID")],
        payload: Annotated[Optional[IGetAttemptDataFromRequestBinPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetAttemptDataFromRequestBinSuccessResponse:
        """Get Attempt Data (Request Bin)

        Gets the attempt data for a specific claim attempt from the requestBin plugin.  Pre-Req: Your claim must be setup with a \"requestBin\" plugin. On the site, it will be titled \"Collect User Inputs\". If there is none, this will fail.  ```tsx await BitBadgesApi.getAttemptDataFromRequestBin(\"claim123\", \"attempt123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getattemptdatafromrequestbin)**  Scopes:   - `readPrivateClaimData` - Required and must be the manager

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param claim_attempt_id: Claim attempt ID (required)
        :type claim_attempt_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAttemptDataFromRequestBinPayload
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

        _param = self._get_attempt_data_from_request_bin_serialize(
            claim_id=claim_id,
            claim_attempt_id=claim_attempt_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAttemptDataFromRequestBinSuccessResponse",
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
    def get_attempt_data_from_request_bin_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        claim_attempt_id: Annotated[StrictStr, Field(description="Claim attempt ID")],
        payload: Annotated[Optional[IGetAttemptDataFromRequestBinPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetAttemptDataFromRequestBinSuccessResponse]:
        """Get Attempt Data (Request Bin)

        Gets the attempt data for a specific claim attempt from the requestBin plugin.  Pre-Req: Your claim must be setup with a \"requestBin\" plugin. On the site, it will be titled \"Collect User Inputs\". If there is none, this will fail.  ```tsx await BitBadgesApi.getAttemptDataFromRequestBin(\"claim123\", \"attempt123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getattemptdatafromrequestbin)**  Scopes:   - `readPrivateClaimData` - Required and must be the manager

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param claim_attempt_id: Claim attempt ID (required)
        :type claim_attempt_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAttemptDataFromRequestBinPayload
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

        _param = self._get_attempt_data_from_request_bin_serialize(
            claim_id=claim_id,
            claim_attempt_id=claim_attempt_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAttemptDataFromRequestBinSuccessResponse",
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
    def get_attempt_data_from_request_bin_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        claim_attempt_id: Annotated[StrictStr, Field(description="Claim attempt ID")],
        payload: Annotated[Optional[IGetAttemptDataFromRequestBinPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Attempt Data (Request Bin)

        Gets the attempt data for a specific claim attempt from the requestBin plugin.  Pre-Req: Your claim must be setup with a \"requestBin\" plugin. On the site, it will be titled \"Collect User Inputs\". If there is none, this will fail.  ```tsx await BitBadgesApi.getAttemptDataFromRequestBin(\"claim123\", \"attempt123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetAttemptDataFromRequestBinSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getattemptdatafromrequestbin)**  Scopes:   - `readPrivateClaimData` - Required and must be the manager

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param claim_attempt_id: Claim attempt ID (required)
        :type claim_attempt_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetAttemptDataFromRequestBinPayload
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

        _param = self._get_attempt_data_from_request_bin_serialize(
            claim_id=claim_id,
            claim_attempt_id=claim_attempt_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetAttemptDataFromRequestBinSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_attempt_data_from_request_bin_serialize(
        self,
        claim_id,
        claim_attempt_id,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
        if claim_attempt_id is not None:
            _path_params['claimAttemptId'] = claim_attempt_id
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
            resource_path='/api/v0/requestBin/attemptData/{claimId}/{claimAttemptId}',
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
    def get_claim(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        payload: Annotated[Optional[IGetClaimPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> IGetClaimSuccessResponse:
        """Get Claim

        Gets a claim by specific ID.  ```tsx await BitBadgesApi.getClaim(\"claim123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaim)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of claim)

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimPayload
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

        _param = self._get_claim_serialize(
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimSuccessResponse",
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
    def get_claim_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        payload: Annotated[Optional[IGetClaimPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
    ) -> ApiResponse[IGetClaimSuccessResponse]:
        """Get Claim

        Gets a claim by specific ID.  ```tsx await BitBadgesApi.getClaim(\"claim123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaim)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of claim)

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimPayload
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

        _param = self._get_claim_serialize(
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimSuccessResponse",
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
    def get_claim_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="Claim ID")],
        payload: Annotated[Optional[IGetClaimPayload], Field(description="The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)")] = None,
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
        """Get Claim

        Gets a claim by specific ID.  ```tsx await BitBadgesApi.getClaim(\"claim123\", { ... }); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaim)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data (also must be manager of claim)

        :param claim_id: Claim ID (required)
        :type claim_id: str
        :param payload: The payload for the request. Anything here should be specified as query parameters (e.g. ?key1=value1&key2=)
        :type payload: IGetClaimPayload
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

        _param = self._get_claim_serialize(
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claim_serialize(
        self,
        claim_id,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
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
            resource_path='/claim/{claimId}',
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
    def get_claim_attempt_status(
        self,
        claim_attempt_id: Annotated[StrictStr, Field(description="The transaction ID of the claim attempt.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
    ) -> IGetClaimAttemptStatusSuccessResponse:
        """Get Claim Attempt Status

        Retrieves the status of a claim attempt by the ID received when submitting.  ```tsx const res = await BitBadgesApi.getClaimAttemptStatus(claimAttemptId); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattemptstatus)**

        :param claim_attempt_id: The transaction ID of the claim attempt. (required)
        :type claim_attempt_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_claim_attempt_status_serialize(
            claim_attempt_id=claim_attempt_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptStatusSuccessResponse",
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
    def get_claim_attempt_status_with_http_info(
        self,
        claim_attempt_id: Annotated[StrictStr, Field(description="The transaction ID of the claim attempt.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
    ) -> ApiResponse[IGetClaimAttemptStatusSuccessResponse]:
        """Get Claim Attempt Status

        Retrieves the status of a claim attempt by the ID received when submitting.  ```tsx const res = await BitBadgesApi.getClaimAttemptStatus(claimAttemptId); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattemptstatus)**

        :param claim_attempt_id: The transaction ID of the claim attempt. (required)
        :type claim_attempt_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_claim_attempt_status_serialize(
            claim_attempt_id=claim_attempt_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptStatusSuccessResponse",
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
    def get_claim_attempt_status_without_preload_content(
        self,
        claim_attempt_id: Annotated[StrictStr, Field(description="The transaction ID of the claim attempt.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
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
        """Get Claim Attempt Status

        Retrieves the status of a claim attempt by the ID received when submitting.  ```tsx const res = await BitBadgesApi.getClaimAttemptStatus(claimAttemptId); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptStatusSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattemptstatus)**

        :param claim_attempt_id: The transaction ID of the claim attempt. (required)
        :type claim_attempt_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
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

        _param = self._get_claim_attempt_status_serialize(
            claim_attempt_id=claim_attempt_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptStatusSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claim_attempt_status_serialize(
        self,
        claim_attempt_id,
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
        if claim_attempt_id is not None:
            _path_params['claimAttemptId'] = claim_attempt_id
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
            resource_path='/claims/status/{claimAttemptId}',
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
    def get_claim_attempts(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: IGetClaimAttemptsPayload,
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
    ) -> IGetClaimAttemptsSuccessResponse:
        """Get Claim Attempts

        Retrieves the attempts for a claim in a paginated format. If you are the manager and authenticated, you can also request failed attempts and view the errors.  ```tsx const res = await BitBadgesApi.getClaimAttempts(claimId, {   address: \"\",   bookmark: \"\",   includeErrors: true }); ```  Documentation References / Tutorials: - **[Getting Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/getting-claims)** - **[Managing Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-claims)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattempts)**  Scopes:   - `readPrivateClaimData` - Required if fetching errors

        :param claim_id: The ID of the claim (required)
        :type claim_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: (required)
        :type payload: IGetClaimAttemptsPayload
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

        _param = self._get_claim_attempts_serialize(
            claim_id=claim_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptsSuccessResponse",
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
    def get_claim_attempts_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: IGetClaimAttemptsPayload,
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
    ) -> ApiResponse[IGetClaimAttemptsSuccessResponse]:
        """Get Claim Attempts

        Retrieves the attempts for a claim in a paginated format. If you are the manager and authenticated, you can also request failed attempts and view the errors.  ```tsx const res = await BitBadgesApi.getClaimAttempts(claimId, {   address: \"\",   bookmark: \"\",   includeErrors: true }); ```  Documentation References / Tutorials: - **[Getting Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/getting-claims)** - **[Managing Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-claims)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattempts)**  Scopes:   - `readPrivateClaimData` - Required if fetching errors

        :param claim_id: The ID of the claim (required)
        :type claim_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: (required)
        :type payload: IGetClaimAttemptsPayload
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

        _param = self._get_claim_attempts_serialize(
            claim_id=claim_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptsSuccessResponse",
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
    def get_claim_attempts_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        payload: IGetClaimAttemptsPayload,
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
        """Get Claim Attempts

        Retrieves the attempts for a claim in a paginated format. If you are the manager and authenticated, you can also request failed attempts and view the errors.  ```tsx const res = await BitBadgesApi.getClaimAttempts(claimId, {   address: \"\",   bookmark: \"\",   includeErrors: true }); ```  Documentation References / Tutorials: - **[Getting Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/getting-claims)** - **[Managing Claims](https://docs.bitbadges.io/for-developers/bitbadges-api/tutorials/managing-claims)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimAttemptsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaimattempts)**  Scopes:   - `readPrivateClaimData` - Required if fetching errors

        :param claim_id: The ID of the claim (required)
        :type claim_id: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param payload: (required)
        :type payload: IGetClaimAttemptsPayload
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

        _param = self._get_claim_attempts_serialize(
            claim_id=claim_id,
            x_api_key=x_api_key,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimAttemptsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claim_attempts_serialize(
        self,
        claim_id,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
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
            resource_path='/claims/{claimId}/attempts',
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
    def get_claims(
        self,
        i_get_claims_payload_v1: IGetClaimsPayloadV1,
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
    ) -> IGetClaimsSuccessResponse:
        """Get Claims - Batch

        Retrieve claims by ID(s). Certain state is not made available by default for scalability reasons and must be requested explicitly.  To fetch private parameters and state, you must be the manager of the claim, signed in, and request it.  ```tsx const res = await BitBadgesApi.getClaims({   claimsToFetch: [     {       claimId: '123',       fetchPrivateParams: true,       privateStatesToFetch: [instanceId1, instanceId2],     },   ], }); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsPayloadV1)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data

        :param i_get_claims_payload_v1: (required)
        :type i_get_claims_payload_v1: IGetClaimsPayloadV1
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

        _param = self._get_claims_serialize(
            i_get_claims_payload_v1=i_get_claims_payload_v1,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimsSuccessResponse",
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
    def get_claims_with_http_info(
        self,
        i_get_claims_payload_v1: IGetClaimsPayloadV1,
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
    ) -> ApiResponse[IGetClaimsSuccessResponse]:
        """Get Claims - Batch

        Retrieve claims by ID(s). Certain state is not made available by default for scalability reasons and must be requested explicitly.  To fetch private parameters and state, you must be the manager of the claim, signed in, and request it.  ```tsx const res = await BitBadgesApi.getClaims({   claimsToFetch: [     {       claimId: '123',       fetchPrivateParams: true,       privateStatesToFetch: [instanceId1, instanceId2],     },   ], }); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsPayloadV1)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data

        :param i_get_claims_payload_v1: (required)
        :type i_get_claims_payload_v1: IGetClaimsPayloadV1
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

        _param = self._get_claims_serialize(
            i_get_claims_payload_v1=i_get_claims_payload_v1,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimsSuccessResponse",
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
    def get_claims_without_preload_content(
        self,
        i_get_claims_payload_v1: IGetClaimsPayloadV1,
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
        """Get Claims - Batch

        Retrieve claims by ID(s). Certain state is not made available by default for scalability reasons and must be requested explicitly.  To fetch private parameters and state, you must be the manager of the claim, signed in, and request it.  ```tsx const res = await BitBadgesApi.getClaims({   claimsToFetch: [     {       claimId: '123',       fetchPrivateParams: true,       privateStatesToFetch: [instanceId1, instanceId2],     },   ], }); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsPayloadV1)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getclaims)**  Scopes:   - `readPrivateClaimData` - Required if fetching private claim data

        :param i_get_claims_payload_v1: (required)
        :type i_get_claims_payload_v1: IGetClaimsPayloadV1
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

        _param = self._get_claims_serialize(
            i_get_claims_payload_v1=i_get_claims_payload_v1,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetClaimsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_claims_serialize(
        self,
        i_get_claims_payload_v1,
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
        if i_get_claims_payload_v1 is not None:
            _body_params = i_get_claims_payload_v1


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
            resource_path='/claims/fetch',
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
    def get_gated_content_for_claim(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
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
    ) -> IGetGatedContentForClaimSuccessResponse:
        """Get Gated Content for Claim

        If claims implement the rewards tab with in-site delivery, there may be gated URLs or content that is only accessible to users who have completed the claim. This endpoint allows you to retrieve the gated content for a claim if you are authenticated and meet the claim's gated content requirements.  ```typescript const res = await BitBadgesApi.getGatedContentForClaim(claimId); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getgatedcontentforclaim)**  Scopes:   - `completeClaims` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param claim_id: The ID of the claim (required)
        :type claim_id: str
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

        _param = self._get_gated_content_for_claim_serialize(
            x_api_key=x_api_key,
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetGatedContentForClaimSuccessResponse",
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
    def get_gated_content_for_claim_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
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
    ) -> ApiResponse[IGetGatedContentForClaimSuccessResponse]:
        """Get Gated Content for Claim

        If claims implement the rewards tab with in-site delivery, there may be gated URLs or content that is only accessible to users who have completed the claim. This endpoint allows you to retrieve the gated content for a claim if you are authenticated and meet the claim's gated content requirements.  ```typescript const res = await BitBadgesApi.getGatedContentForClaim(claimId); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getgatedcontentforclaim)**  Scopes:   - `completeClaims` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param claim_id: The ID of the claim (required)
        :type claim_id: str
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

        _param = self._get_gated_content_for_claim_serialize(
            x_api_key=x_api_key,
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetGatedContentForClaimSuccessResponse",
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
    def get_gated_content_for_claim_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim")],
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
        """Get Gated Content for Claim

        If claims implement the rewards tab with in-site delivery, there may be gated URLs or content that is only accessible to users who have completed the claim. This endpoint allows you to retrieve the gated content for a claim if you are authenticated and meet the claim's gated content requirements.  ```typescript const res = await BitBadgesApi.getGatedContentForClaim(claimId); ```  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetGatedContentForClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getgatedcontentforclaim)**  Scopes:   - `completeClaims` - Required

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param claim_id: The ID of the claim (required)
        :type claim_id: str
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

        _param = self._get_gated_content_for_claim_serialize(
            x_api_key=x_api_key,
            claim_id=claim_id,
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetGatedContentForClaimSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_gated_content_for_claim_serialize(
        self,
        x_api_key,
        claim_id,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
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
            resource_path='/claims/gatedContent/{claimId}',
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
    def get_reserved_codes(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        body: Dict[str, Any],
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
    ) -> IGetReservedClaimCodesSuccessResponse:
        """Get Reserved Claim Codes

        Retrieves the reserved codes for a claim.  For on-chain claims / approvals, we use a code reservation system where the claim code is to be used in the eventual blockchain transaction. This is used to bridge the gap between the off-chain claim and on-chain approval / transfer.  ```tsx const res = await BitBadgesApi.getReservedCodes(claimId, address); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getReservedCodes)**  Scopes:   - `completeClaims` - Required

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param body: (required)
        :type body: object
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

        _param = self._get_reserved_codes_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetReservedClaimCodesSuccessResponse",
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
    def get_reserved_codes_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        body: Dict[str, Any],
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
    ) -> ApiResponse[IGetReservedClaimCodesSuccessResponse]:
        """Get Reserved Claim Codes

        Retrieves the reserved codes for a claim.  For on-chain claims / approvals, we use a code reservation system where the claim code is to be used in the eventual blockchain transaction. This is used to bridge the gap between the off-chain claim and on-chain approval / transfer.  ```tsx const res = await BitBadgesApi.getReservedCodes(claimId, address); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getReservedCodes)**  Scopes:   - `completeClaims` - Required

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param body: (required)
        :type body: object
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

        _param = self._get_reserved_codes_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetReservedClaimCodesSuccessResponse",
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
    def get_reserved_codes_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        body: Dict[str, Any],
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
        """Get Reserved Claim Codes

        Retrieves the reserved codes for a claim.  For on-chain claims / approvals, we use a code reservation system where the claim code is to be used in the eventual blockchain transaction. This is used to bridge the gap between the off-chain claim and on-chain approval / transfer.  ```tsx const res = await BitBadgesApi.getReservedCodes(claimId, address); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iGetReservedClaimCodesSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#getReservedCodes)**  Scopes:   - `completeClaims` - Required

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param body: (required)
        :type body: object
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

        _param = self._get_reserved_codes_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "IGetReservedClaimCodesSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_reserved_codes_serialize(
        self,
        claim_id,
        address,
        x_api_key,
        body,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter
        if body is not None:
            _body_params = body


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
            resource_path='/claims/reserved/{claimId}/{address}',
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
    def search_claims(
        self,
        payload: ISearchClaimsPayload,
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
    ) -> ISearchClaimsSuccessResponse:
        """Search Claims

        Search through the signed in user's claims they have created / are managing.  ```tsx const res = await BitBadgesApi.searchClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchclaims)**  Scopes:   - `readPrivateClaimData` - Required for fetching private claim data

        :param payload: (required)
        :type payload: ISearchClaimsPayload
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

        _param = self._search_claims_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchClaimsSuccessResponse",
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
    def search_claims_with_http_info(
        self,
        payload: ISearchClaimsPayload,
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
    ) -> ApiResponse[ISearchClaimsSuccessResponse]:
        """Search Claims

        Search through the signed in user's claims they have created / are managing.  ```tsx const res = await BitBadgesApi.searchClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchclaims)**  Scopes:   - `readPrivateClaimData` - Required for fetching private claim data

        :param payload: (required)
        :type payload: ISearchClaimsPayload
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

        _param = self._search_claims_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchClaimsSuccessResponse",
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
    def search_claims_without_preload_content(
        self,
        payload: ISearchClaimsPayload,
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
        """Search Claims

        Search through the signed in user's claims they have created / are managing.  ```tsx const res = await BitBadgesApi.searchClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSearchClaimsSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#searchclaims)**  Scopes:   - `readPrivateClaimData` - Required for fetching private claim data

        :param payload: (required)
        :type payload: ISearchClaimsPayload
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

        _param = self._search_claims_serialize(
            payload=payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISearchClaimsSuccessResponse",
            '400': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _search_claims_serialize(
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
            'userMaybeSignedIn', 
            'apiKey'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/claims/search',
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
    def simulate_claim(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_simulate_claim_payload: ISimulateClaimPayload,
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
    ) -> ISimulateClaimSuccessResponse:
        """Simulate Claim

        Simulates a claim for a user. This will check if the claim is valid and that all criteria is satisfied. This returns a fake ID for compatibility with certain integrations. A successful response means simulation passed. This is instant and does not use the queue.  Note: There may be cases where the simulation passes but the claim fails. This may happen if state changes between the simulation and the claim. It is always best practice to simulate first, but do not rely on the simulation response for the final result.  ```tsx const res = await BitBadgesApi.simulateClaim(claimId, address, { ...body }); ```  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   _specificInstanceIds: [pluginInstanceId1, pluginInstanceId2], //Optional: simulate only specific instances   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#simulateclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_simulate_claim_payload: (required)
        :type i_simulate_claim_payload: ISimulateClaimPayload
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

        _param = self._simulate_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_simulate_claim_payload=i_simulate_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISimulateClaimSuccessResponse",
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
    def simulate_claim_with_http_info(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_simulate_claim_payload: ISimulateClaimPayload,
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
    ) -> ApiResponse[ISimulateClaimSuccessResponse]:
        """Simulate Claim

        Simulates a claim for a user. This will check if the claim is valid and that all criteria is satisfied. This returns a fake ID for compatibility with certain integrations. A successful response means simulation passed. This is instant and does not use the queue.  Note: There may be cases where the simulation passes but the claim fails. This may happen if state changes between the simulation and the claim. It is always best practice to simulate first, but do not rely on the simulation response for the final result.  ```tsx const res = await BitBadgesApi.simulateClaim(claimId, address, { ...body }); ```  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   _specificInstanceIds: [pluginInstanceId1, pluginInstanceId2], //Optional: simulate only specific instances   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#simulateclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_simulate_claim_payload: (required)
        :type i_simulate_claim_payload: ISimulateClaimPayload
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

        _param = self._simulate_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_simulate_claim_payload=i_simulate_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISimulateClaimSuccessResponse",
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
    def simulate_claim_without_preload_content(
        self,
        claim_id: Annotated[StrictStr, Field(description="The ID of the claim.")],
        address: Annotated[StrictStr, Field(description="The address of the user making the claim.")],
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_simulate_claim_payload: ISimulateClaimPayload,
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
        """Simulate Claim

        Simulates a claim for a user. This will check if the claim is valid and that all criteria is satisfied. This returns a fake ID for compatibility with certain integrations. A successful response means simulation passed. This is instant and does not use the queue.  Note: There may be cases where the simulation passes but the claim fails. This may happen if state changes between the simulation and the claim. It is always best practice to simulate first, but do not rely on the simulation response for the final result.  ```tsx const res = await BitBadgesApi.simulateClaim(claimId, address, { ...body }); ```  _expectedVersion is required and must match the version of the claim. If you want to override this check, specify -1.  The rest of the body should look like: ```typescript {   _expectedVersion: 1,   _specificInstanceIds: [pluginInstanceId1, pluginInstanceId2], //Optional: simulate only specific instances   [pluginInstanceId1]: { ..bodyForPluginInstanceId1 },   [pluginInstanceId2]: { ..bodyForPluginInstanceId2 }, } ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iSimulateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#simulateclaim)**  Scopes:   - `completeClaims` - Required if completing claims on behalf of a user and requires sign-in

        :param claim_id: The ID of the claim. (required)
        :type claim_id: str
        :param address: The address of the user making the claim. (required)
        :type address: str
        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_simulate_claim_payload: (required)
        :type i_simulate_claim_payload: ISimulateClaimPayload
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

        _param = self._simulate_claim_serialize(
            claim_id=claim_id,
            address=address,
            x_api_key=x_api_key,
            i_simulate_claim_payload=i_simulate_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ISimulateClaimSuccessResponse",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _simulate_claim_serialize(
        self,
        claim_id,
        address,
        x_api_key,
        i_simulate_claim_payload,
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
        if claim_id is not None:
            _path_params['claimId'] = claim_id
        if address is not None:
            _path_params['address'] = address
        # process the query parameters
        # process the header parameters
        if x_api_key is not None:
            _header_params['x-api-key'] = x_api_key
        # process the form parameters
        # process the body parameter
        if i_simulate_claim_payload is not None:
            _body_params = i_simulate_claim_payload


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
            resource_path='/claims/simulate/{claimId}/{address}',
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
    def update_claim(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_claim_payload: IUpdateClaimPayload,
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
        """Update Claim

        Updates an existing claim.  Note: Updating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated per claim. - Linked to on-chain approvals (user or collection level) - Specify the valid collectionId. Note: This is advanced. Please reach out if you need this.  ```tsx const res = await BitBadgesApi.updateClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for updating link listed claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_claim_payload: (required)
        :type i_update_claim_payload: IUpdateClaimPayload
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

        _param = self._update_claim_serialize(
            x_api_key=x_api_key,
            i_update_claim_payload=i_update_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def update_claim_with_http_info(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_claim_payload: IUpdateClaimPayload,
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
        """Update Claim

        Updates an existing claim.  Note: Updating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated per claim. - Linked to on-chain approvals (user or collection level) - Specify the valid collectionId. Note: This is advanced. Please reach out if you need this.  ```tsx const res = await BitBadgesApi.updateClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for updating link listed claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_claim_payload: (required)
        :type i_update_claim_payload: IUpdateClaimPayload
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

        _param = self._update_claim_serialize(
            x_api_key=x_api_key,
            i_update_claim_payload=i_update_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
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
    def update_claim_without_preload_content(
        self,
        x_api_key: Annotated[StrictStr, Field(description="BitBadges API Key for authentication")],
        i_update_claim_payload: IUpdateClaimPayload,
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
        """Update Claim

        Updates an existing claim.  Note: Updating claims via the API is often overkill. Consider doing this in-site, using a plugin approach or another method first.  There are a few categories of claims: - Standalone (default) - Not attached to anything - Test claims - Used for frontend claim tester - Linked to address lists - Specify the valid `listId` within the request. Must be list creator. - Linked to off-chain balances - Specify the valid `collectionId` + `balancesToSet` within the request. `balancesToSet` determine what badges are allocated per claim. - Linked to on-chain approvals (user or collection level) - Specify the valid collectionId. Note: This is advanced. Please reach out if you need this.  ```tsx const res = await BitBadgesApi.updateClaims(...); ```  Documentation References / Tutorials: - **[Completing Claims](https://docs.bitbadges.io/for-developers/claim-builder/auto-complete-claims-w-bitbadges-api)** - **[All About BitBadges Claims](https://docs.bitbadges.io/for-developers/claim-builder)**  SDK Links: - **[Request Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimPayload)** - **[Response Type](https://bitbadges.github.io/bitbadgesjs/interfaces/iUpdateClaimSuccessResponse)** - **[SDK API Function](https://bitbadges.github.io/bitbadgesjs/classes/BitBadgesAPI.html#updateclaims)**  Tip: You can see the claim JSONs in-site. Click the info circle button > JSON tab. Use the claim tester, build your claim, and see how it works behind the scenes.  Scopes:   - `manageClaims` - Required   - `manageAddressLists` - Required for updating link listed claims

        :param x_api_key: BitBadges API Key for authentication (required)
        :type x_api_key: str
        :param i_update_claim_payload: (required)
        :type i_update_claim_payload: IUpdateClaimPayload
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

        _param = self._update_claim_serialize(
            x_api_key=x_api_key,
            i_update_claim_payload=i_update_claim_payload,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '400': "ErrorResponse",
            '401': "ErrorResponse",
            '500': "ErrorResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_claim_serialize(
        self,
        x_api_key,
        i_update_claim_payload,
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
        if i_update_claim_payload is not None:
            _body_params = i_update_claim_payload


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
            resource_path='/claims',
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


