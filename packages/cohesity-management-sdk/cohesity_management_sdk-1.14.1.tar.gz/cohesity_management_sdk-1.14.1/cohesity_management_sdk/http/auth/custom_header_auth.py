from cohesity_management_sdk.cohesity_client import CohesityClient
from cohesity_management_sdk.models.access_token_credential import AccessTokenCredential
from cohesity_management_sdk.models_v2.create_user_session_request_params import CreateUserSessionRequestParams


class CustomHeaderAuth:
    # Add a class-level flag to prevent recursion during session creation
    session_creation_in_progress = False

    @classmethod
    def apply(cls, http_request, Configuration):
        if Configuration.api_key :
            http_request.add_header("apiKey" , Configuration.api_key)
        elif getattr(Configuration , "use_session" , False) :
            if not Configuration.session_id :
                cls.authorize_session(Configuration)
            http_request.add_header("session-id" , Configuration.session_id)
        else :
            cls.check_auth(Configuration)
            token = Configuration.auth_token.access_token
            token_type = Configuration.auth_token.token_type
            http_request.headers['Authorization'] = token_type + " " + token

    @classmethod
    def check_auth(cls, Configuration):
        """Check if an access token is available."""
        if not Configuration.auth_token:
            cls.authorize(Configuration)

    @classmethod
    def authorize(cls, Configuration):
        """Generate and store an access token."""
        body = AccessTokenCredential()
        body.username = Configuration.username
        body.password = Configuration.password
        client = CohesityClient(cluster_vip=Configuration.cluster_vip, username=body.username, password=body.password)

        if Configuration.domain:
            client.domain = Configuration.domain
            body.domain = Configuration.domain

        token = client.access_tokens.create_generate_access_token(body)
        Configuration.auth_token = token

    @classmethod
    def authorize_session(cls, Configuration):
        """Generate and store a session ID."""
        if cls.session_creation_in_progress:
            # Prevent recursion: session creation is already in progress
            return

        cls.session_creation_in_progress = True  # Set the flag to indicate session creation is in progress

        from cohesity_management_sdk.cohesity_client_v2 import CohesityClientV2

        body = CreateUserSessionRequestParams()
        body.username = Configuration.username
        body.password = Configuration.password
        v2_client = CohesityClientV2(cluster_vip=Configuration.cluster_vip, username=body.username, password=body.password,
                                     use_session=Configuration.use_session)

        if Configuration.domain:
            v2_client.domain = Configuration.domain
            body.domain = Configuration.domain
        session = v2_client.users.create_session(body)
        if session:
            Configuration.session_id = session.session_id

        cls.session_creation_in_progress = False