
"""
`Configs` is a class that contains the global configuration variables/parameters
to be used in the services
"""


class Configs:
    BASE_URL:str = "https://api-{env}.on.sportsxapp.com"
    GRAPHQL_URL: str = "https://api-{env}.on.sportsxapp.com/api/graphql"
    WS_URL: str = "wss://api-{env}.on.sportsxapp.com/socket/websocket"
    API_ENV = "staging"
    LOGIN_API: str = "login"
    CONFIRM_2FA: str = "confirm2Fa"
    REFRESH_TOKEN_API: str = "newToken"
    REGISTER_API:str = "register"
    CHANNEL_CONNECTION_URL: str = "{url}?token={token}&vsn=2.0.0"
    GRAPHQL_VERSION_URL:str = BASE_URL+"/api_version"
    GRAPHQL_VERSION:str = "v3.0.52-3"
    SCHEMA_PATH:str= "https://schema.stxapp.io"

