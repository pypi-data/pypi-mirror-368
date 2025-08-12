# -*- coding: utf-8 -*-


class RequestParamsToClaimRigelToHelios(object):

    """Implementation of the 'Request params to claim Rigel to Helios.' model.

    Specifies the request params to claim Rigel to Helios.

    Attributes:
        rigel_guid (long|int): Unique id for rigel instance.
        claim_token (string): Claim token used for authentication.
        rigel_type (RigelTypeEnum): Specifies the Rigel type that is being
            claimed.
        cluster_id (long|int): Specifies the cluster id.
        cluster_incarnation_id (long|int): Specifies the cluster incarnation
            id.
        rigel_name (string): Specifies the Rigel name.
        rigel_ip (string): Specifies the Rigel IP.
        software_version (string): Specifies the Rigel Software version.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rigel_guid":'rigelGuid',
        "claim_token":'claimToken',
        "rigel_type":'rigelType',
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "rigel_name":'rigelName',
        "rigel_ip":'rigelIp',
        "software_version":'softwareVersion'
    }

    def __init__(self,
                 rigel_guid=None,
                 claim_token=None,
                 rigel_type=None,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 rigel_name=None,
                 rigel_ip=None,
                 software_version=None):
        """Constructor for the RequestParamsToClaimRigelToHelios class"""

        # Initialize members of the class
        self.rigel_guid = rigel_guid
        self.claim_token = claim_token
        self.rigel_type = rigel_type
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.rigel_name = rigel_name
        self.rigel_ip = rigel_ip
        self.software_version = software_version


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
        rigel_guid = dictionary.get('rigelGuid')
        claim_token = dictionary.get('claimToken')
        rigel_type = dictionary.get('rigelType')
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        rigel_name = dictionary.get('rigelName')
        rigel_ip = dictionary.get('rigelIp')
        software_version = dictionary.get('softwareVersion')

        # Return an object of this model
        return cls(rigel_guid,
                   claim_token,
                   rigel_type,
                   cluster_id,
                   cluster_incarnation_id,
                   rigel_name,
                   rigel_ip,
                   software_version)


