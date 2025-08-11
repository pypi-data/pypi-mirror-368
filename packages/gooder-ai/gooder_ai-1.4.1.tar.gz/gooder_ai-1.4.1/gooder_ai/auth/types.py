from typing import TypedDict


class AuthenticateParams(TypedDict):
    email: str
    password: str
    app_client_id: str
    identity_pool_id: str
    user_pool_id: str


class AuthenticationResult(TypedDict):
    AccessToken: str
    IdToken: str
    RefreshToken: str
    ExpiresIn: int
    TokenType: str


class CognitoClientResponse(TypedDict):
    AuthenticationResult: AuthenticationResult


class CognitoIdentityResponse(TypedDict):
    IdentityId: str


class Credentials(TypedDict):
    AccessKeyId: str
    SecretKey: str
    SessionToken: str
    Expiration: str


class CognitoCredentialsResponse(TypedDict):
    IdentityId: str
    Credentials: Credentials


class AuthenticateReturn(TypedDict):
    cognito_client_response: CognitoClientResponse
    cognito_identity_response: CognitoIdentityResponse
    cognito_credentials: CognitoCredentialsResponse
