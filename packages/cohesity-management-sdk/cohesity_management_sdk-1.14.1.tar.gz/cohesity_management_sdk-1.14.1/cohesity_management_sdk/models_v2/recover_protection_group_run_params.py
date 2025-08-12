# -*- coding: utf-8 -*-


class RecoverProtectionGroupRunParams(object):

    """Implementation of the 'Recover Protection Group Run Params.' model.

    Specifies the Protection Group Run params to recover. All the VM's that
    are successfully backed up by specified Runs will be recovered.

    Attributes:
        protection_group_run_id (string): Specifies the Protection Group Run
            id from which to recover VMs. All the VM's that are successfully
            protected by this Run will be recovered.
        protection_group_instance_id (long|int): Specifies the Protection
            Group Instance id.
        archival_target_id (long|int): Specifies the archival target id. If
            specified and Protection Group run has an archival snapshot then
            VMs are recovered from the specified archival snapshot. If not
            specified (default), VMs are recovered from local snapshot.
        protection_group_id (string): Specifies the local Protection Group id.
            In case of recovering a replication Run, this field should be
            provided with local Protection Group id.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_run_id":'protectionGroupRunId',
        "protection_group_instance_id":'protectionGroupInstanceId',
        "archival_target_id":'archivalTargetId',
        "protection_group_id":'protectionGroupId'
    }

    def __init__(self,
                 protection_group_run_id=None,
                 protection_group_instance_id=None,
                 archival_target_id=None,
                 protection_group_id=None):
        """Constructor for the RecoverProtectionGroupRunParams class"""

        # Initialize members of the class
        self.protection_group_run_id = protection_group_run_id
        self.protection_group_instance_id = protection_group_instance_id
        self.archival_target_id = archival_target_id
        self.protection_group_id = protection_group_id


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
        protection_group_run_id = dictionary.get('protectionGroupRunId')
        protection_group_instance_id = dictionary.get('protectionGroupInstanceId')
        archival_target_id = dictionary.get('archivalTargetId')
        protection_group_id = dictionary.get('protectionGroupId')

        # Return an object of this model
        return cls(protection_group_run_id,
                   protection_group_instance_id,
                   archival_target_id,
                   protection_group_id)


