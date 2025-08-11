import boto3
from gooder_ai.auth.types import AuthenticateParams, AuthenticateReturn

Cognito_Client = boto3.client(
    "cognito-idp", region_name="us-east-1"
)  # Initialize a boto3 client for Cognito Identity Provider to manage authentication flows
Cognito_Identity_Client = boto3.client(
    "cognito-identity", region_name="us-east-1"
)  # Initialize a boto3 client for Cognito Identity to manage access key and secret access key


def authenticate(input: AuthenticateParams) -> AuthenticateReturn:
    email = input["email"]
    password = input["password"]
    app_client_id = input["app_client_id"]
    identity_pool_id = input["identity_pool_id"]
    user_pool_id = input["user_pool_id"]

    # Initiate authentication Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/initiate_auth.html#initiate-auth
    # cognito_client_response consists of access_token, id_token, refresh_token.
    cognito_client_response = Cognito_Client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        ClientId=app_client_id,
        AuthParameters={"USERNAME": email, "PASSWORD": password},
    )

    # Using id_token to get the client_id. Ref: https://stackoverflow.com/a/62789387
    cognito_identity_response = Cognito_Identity_Client.get_id(
        IdentityPoolId=identity_pool_id
    )
    # Using cognito identity id to get access_key, secret_access_key which will be used to upload files to s3. Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-identity/client/get_credentials_for_identity.html#get-credentials-for-identity
    cognito_credentials_response = Cognito_Identity_Client.get_credentials_for_identity(
        IdentityId=cognito_identity_response["IdentityId"],
        Logins={
            f"cognito-idp.us-east-1.amazonaws.com/{user_pool_id}": cognito_client_response[
                "AuthenticationResult"
            ][
                "IdToken"
            ]
        },
    )

    credentials: AuthenticateReturn = {
        "cognito_client_response": cognito_client_response,
        "cognito_identity_response": cognito_identity_response,
        "cognito_credentials": cognito_credentials_response,
    }

    return credentials
