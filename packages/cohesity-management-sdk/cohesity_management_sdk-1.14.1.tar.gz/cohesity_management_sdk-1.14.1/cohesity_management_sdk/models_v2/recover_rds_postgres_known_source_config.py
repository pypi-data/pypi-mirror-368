# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier

class RecoverRdsPostgresKnownSourceConfig(object):

    """Implementation of the 'RecoverRdsPostgresKnownSourceConfig' model.

    Specifies the parameters to recover RDS Postgres.

    Attributes:
        instance (RecoveryObjectIdentifier): Specifies the instance in which to deploy the Rds instance.
        recover_to_new_source (bool): Specifies the parameter whether the recovery should be performed
          to a new target.
        region (RecoveryObjectIdentifier): Specifies the AWS region in which to deploy the Rds instance.
        source (RecoveryObjectIdentifier): Specifies the target source details where RDS Postgres database
          will be recovered. This source id should be a RDS Postgres target instance
          id were databases could be restored.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "instance":'instance',
        "recover_to_new_source":'recoverToNewSource',
        "region":'region',
        "source":'source'
    }

    def __init__(self,
                 instance=None,
                 recover_to_new_source=None,
                 region=None,
                 source=None):
        """Constructor for the RecoverRdsPostgresKnownSourceConfig class"""

        # Initialize members of the class
        self.instance = instance
        self.recover_to_new_source = recover_to_new_source
        self.region = region
        self.source = source


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
        instance = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('instance')) if dictionary.get('instance') else None
        recover_to_new_source = dictionary.get('recoverToNewSource')
        region = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(instance,
                   recover_to_new_source,
                   region,
                   source)