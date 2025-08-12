# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto

class EncryptionParams(object):

    """Implementation of the 'EncryptionParams' model.

    TODO: type model description here.

    Attributes:
        kms_key (EntityProto): Specifies the attributes and the latest
            statistics about an entity.
        custom_kms_key_arn (string): String containing kms key arn in case of
            custom key option.
            Example: arn:aws:kms:<region>:<account_id>:key/<key_id>
        should_encrypt (bool): Whether to encrypt the restored instance''s
            volumes or not.
            For recovery to new location, this will be true by default

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "custom_kms_key_arn":'customKmsKeyArn',
        "kms_key":'kmsKey',
        "should_encrypt":'shouldEncrypt'
    }

    def __init__(self,
                 custom_kms_key_arn=None ,
                 kms_key=None,
                 should_encrypt=None):
        """Constructor for the EncryptionParams class"""

        # Initialize members of the class
        self.custom_kms_key_arn = custom_kms_key_arn
        self.kms_key = kms_key
        self.should_encrypt = should_encrypt


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
        custom_kms_key_arn = dictionary.get('customKmsKeyArn')
        kms_key = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('kmsKey')) if dictionary.get('kmsKey') else None
        should_encrypt = dictionary.get('shouldEncrypt')

        # Return an object of this model
        return cls(
                   custom_kms_key_arn,
                   kms_key,
                   should_encrypt)
