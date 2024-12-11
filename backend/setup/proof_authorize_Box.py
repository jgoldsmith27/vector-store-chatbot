from boxsdk import OAuth2, Client, DeveloperTokenClient

def authorize_box(inDev = True, client_id = None, client_secret = None, access_token = None):
    """
    Authorizes a Box account and returns the Box client

    inDev: Boolean (default to True)
        whether the app is in development mode or not

    client_id: String (default to None)
        the client id for the Box client

    client_secret: String (default to None)
        the client secret for the Box client
    
    access_token: String (default to None)
        the access toke for the Box client
    """
    # To determine which client to use
    inDev = True
    # Instantiate the client
    client = None

    # Try to authorize the client
    print("Authorizing client...")

    # Use DeveloperToken Client if app is still in development -- will prompt for developer token
    if inDev:
        client = DeveloperTokenClient()

    # Otherwise app is in production and authenticate with OAuth2 -- need to authroize app in Dev Console to access refresh token
    else:
        auth = OAuth2(
            client_id = client_id,
            client_secret = client_secret,
            access_token = access_token
        )
        client = Client(auth)

    return client