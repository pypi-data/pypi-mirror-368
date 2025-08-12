# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_user_response_params
import cohesity_management_sdk.models_v2.s_3_account_params

class UserParams(object):

    """Implementation of the 'UserParams' model.

    Specifies a User

    Attributes:
        created_time_msecs (long|int): Specifies the epoch time in milliseconds when the user account
            was created.
        domain (string): Specifies the domain of the user. For active directories, this
            is the fully qualified domain name (FQDN). It is 'LOCAL' for local users
            on the Cohesity Cluster. A user is uniquely identified by combination
            of the username and the domain.
        force_password_change (bool): Specifies if the user must change password.
        last_login_time_msecs (long|int): Specifies the epoch time in milliseconds when the user last
            logged in successfully.
        last_updated_time_msecs (long|int): Specifies the epoch time in milliseconds when the user account
            was last modified.
        local_user_params (LocalUserResponseParams): Specifies the LOCAL user properties. This field is required
            when adding a new LOCAL Cohesity User.
        locked_reason (LockedReasonEnum): Specifies the reason for locking the User.
        other_groups (string): Specifies additional groups the User may belong to.
        primary_group (string): Specifies the primary group of the User. Primary group is used
            for file access.
        s_3_account_params (S3AccountParams): Specifies the S3 Account parameters of the User.
        sid (string): Specifies the sid of the User.
        tenant_id (string): Specifies the tenant id of the User.
        username (string): Specifies the username.
        description (string): Specifies the description of the User.
        effective_time_msecs (long|int): Specifies the epoch time in milliseconds since when the user
          can login.
        expiry_time_msecs (long|int): Specifies the epoch time in milliseconds when the user expires.
          Post expiry the user cannot access Cohesity cluster.
        locked (bool): Specifies whether the User is locked.
        restricted (bool): Specifies whether the User is restricted. A restricted user can
          only view & manage the objects it has permissions to.
        roles (list of string): Specifies the Cohesity roles to associate with the user. The
          Cohesity roles determine privileges on the Cohesity Cluster for this user.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "created_time_msecs" : 'createdTimeMsecs',
        "domain" : 'domain',
        "force_password_change" : 'forcePasswordChange',
        "last_login_time_msecs" : 'lastLoginTimeMsecs',
        "last_updated_time_msecs" : 'lastUpdatedTimeMsecs',
        "local_user_params" : 'localUserParams',
        "locked_reason" : 'lockedReason',
        "other_groups" :"otherGroups",
        "primary_group" : 'primaryGroup',
        "s_3_account_params" : 's3AccountParams',
        "sid" : 'sid',
        "tenant_id" : 'tenantId',
        "username" : 'username',
        "description" : 'description',
        "effective_time_msecs" : 'effectiveTimeMsecs',
        "expiry_time_msecs" : 'expiryTimeMsecs',
        "locked" : 'locked',
        "restricted" : 'restricted',
        "roles" : 'roles'
    }

    def __init__(self,
                 created_time_msecs=None,
                 domain=None,
                 force_password_change=None,
                 last_login_time_msecs=None,
                 last_updated_time_msecs=None,
                 local_user_params=None,
                 locked_reason=None,
                 other_groups=None,
                 primary_group=None,
                 s_3_account_params=None,
                 sid=None,
                 tenant_id=None,
                 username=None,
                 description=None,
                 effective_time_msecs=None,
                 expiry_time_msecs=None,
                 locked=None,
                 restricted=None,
                 roles=None
                 ):
        """Constructor for the UserParams class"""

        # Initialize members of the class
        self.created_time_msecs = created_time_msecs
        self.domain = domain
        self.force_password_change = force_password_change
        self.last_login_time_msecs = last_login_time_msecs
        self.last_updated_time_msecs = last_updated_time_msecs
        self.local_user_params = local_user_params
        self.locked_reason = locked_reason
        self.other_groups = other_groups
        self.primary_group = primary_group
        self.s_3_account_params =  s_3_account_params
        self.sid = sid
        self.tenant_id = tenant_id
        self.username = username
        self.description = description
        self.effective_time_msecs = effective_time_msecs
        self.expiry_time_msecs = expiry_time_msecs
        self.locked = locked
        self.restricted = restricted
        self.roles = roles

    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        created_time_msecs = dictionary.get('createdTimeMsecs')
        domain = dictionary.get('domain')
        force_password_change = dictionary.get('forcePasswordChange')
        last_login_time_msecs = dictionary.get('lastLoginTimeMsecs')
        last_updated_time_msecs = dictionary.get('lastUpdatedTimeMsecs')
        local_user_params = cohesity_management_sdk.models_v2.local_user_response_params.LocalUserResponseParams.from_dictionary(dictionary.get('localUserParams')) if dictionary.get('localUserParams') else None
        locked_reason = dictionary.get('lockedReason')
        other_groups = dictionary.get('otherGroups')
        primary_group = dictionary.get('primaryGroup')
        s_3_account_params = cohesity_management_sdk.models_v2.s_3_account_params.S3AccountParams.from_dictionary(dictionary.get('s3AccountParams')) if dictionary.get('s3AccountParams') else None
        sid = dictionary.get('sid')
        tenant_id = dictionary.get('tenantId')
        username = dictionary.get('username')
        description = dictionary.get('description')
        effective_time_msecs = dictionary.get('effectiveTimeMsecs')
        expiry_time_msecs = dictionary.get('expiryTimeMsecs')
        locked = dictionary.get('locked')
        restricted = dictionary.get('restricted')
        roles = dictionary.get('roles')

        # Return an object of this model
        return cls(created_time_msecs,
                   domain,
                   force_password_change,
                   last_login_time_msecs,
                   last_updated_time_msecs,
                   local_user_params,
                   locked_reason,
                   other_groups,
                   primary_group,
                   s_3_account_params,
                   sid,
                   tenant_id,
                   username,
                   description,
                   effective_time_msecs,
                   expiry_time_msecs,
                   locked,
                   restricted,
                   roles)