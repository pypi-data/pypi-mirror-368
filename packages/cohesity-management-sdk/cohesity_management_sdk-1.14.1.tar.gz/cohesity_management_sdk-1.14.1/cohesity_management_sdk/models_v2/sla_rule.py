# -*- coding: utf-8 -*-


class SlaRule(object):

    """Implementation of the 'SlaRule' model.

    Specifies an SLA rule for a specific Protection Group run type.

    Attributes:
        backup_run_type (BackupRunTypeEnum): Specifies the type of run this
            rule should apply to.
        sla_minutes (long|int): Specifies the number of minutes allotted to a
            run of the specified type before SLA is considered violated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_run_type":'backupRunType',
        "sla_minutes":'slaMinutes'
    }

    def __init__(self,
                 backup_run_type=None,
                 sla_minutes=None):
        """Constructor for the SlaRule class"""

        # Initialize members of the class
        self.backup_run_type = backup_run_type
        self.sla_minutes = sla_minutes


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
        backup_run_type = dictionary.get('backupRunType')
        sla_minutes = dictionary.get('slaMinutes')

        # Return an object of this model
        return cls(backup_run_type,
                   sla_minutes)


