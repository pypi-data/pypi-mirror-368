# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class AAGReplicaInfo(object):

    """Implementation of the 'AAGReplicaInfo' model.

    Specifies the information about the AAG replica.

    Attributes:
        availability_mode (AvailabilityModeEnum): Specifies the availability
            mode of the replica.
        create_date_msecs (long|int):  Specifies the time when replica is created.
        host_name (string): Specifies the host name of the replica.
        last_modified_msecs (int): Specifies the backup priority.
        operational_state (OperationalStateEnum): Specifies the operational state
            of the replica. kFailedNoQuorum, kNull
        primary_role_allow_connections (PrimaryRoleAllowConnectionsEnum):
            Specifies what are the types of connections primary role allows.
        role (RoleEnum):  Specifies the role of replica.
        secondary_role_allow_connections (SecondaryRoleAllowConnectionsEnum):
            Specifies what are the types of connections secondary role allows.
        server_name (string): Specifies the instance name along with the host
        name on which the AAG databases are hosted.
        synchronization_health (SynchronizationHealthEnum): Specifies the
            synchronization health of the replica.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "availability_mode":'availabilityMode',
        "create_date_msecs":'createDateMsecs',
        "host_name":'hostName',
        "last_modified_msecs":'lastModifiedMsecs',
        "operational_state":'operationalState',
        "primary_role_allow_connections":'primaryRoleAllowConnections',
        "role":'role',
        "secondary_role_allow_connections":'secondaryRoleAllowConnections',
        "server_name":'serverName',
        "synchronization_health":'synchronizationHealth'
    }

    def __init__(self,
                 availability_mode=None,
                 create_date_msecs=None,
                 host_name=None,
                 last_modified_msecs=None,
                 operational_state=None,
                 primary_role_allow_connections=None,
                 role=None,
                 secondary_role_allow_connections=None,
                 server_name=None,
                 synchronization_health=None):
        """Constructor for the AAGReplicaInfo class"""

        # Initialize members of the class
        self.availability_mode = availability_mode
        self.create_date_msecs = create_date_msecs
        self.host_name = host_name
        self.last_modified_msecs = last_modified_msecs
        self.operational_state = operational_state
        self.primary_role_allow_connections = primary_role_allow_connections
        self.role = role
        self.secondary_role_allow_connections = secondary_role_allow_connections
        self.server_name = server_name
        self.synchronization_health = synchronization_health


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API d escription.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        availability_mode = dictionary.get('availabilityMode')
        create_date_msecs = dictionary.get('createDateMsecs')
        host_name = dictionary.get('hostName')
        last_modified_msecs = dictionary.get('lastModifiedMsecs')
        operational_state = dictionary.get('operationalState')
        primary_role_allow_connections = dictionary.get('primaryRoleAllowConnections')
        role = dictionary.get('role')
        secondary_role_allow_connections = dictionary.get('secondaryRoleAllowConnections')
        server_name = dictionary.get('serverName')
        synchronization_health = dictionary.get('synchronizationHealth')

        # Return an object of this model
        return cls(availability_mode,
                   create_date_msecs,
                   host_name,
                   last_modified_msecs,
                   operational_state,
                   primary_role_allow_connections,
                   role,
                   secondary_role_allow_connections,
                   server_name,
                   synchronization_health)


