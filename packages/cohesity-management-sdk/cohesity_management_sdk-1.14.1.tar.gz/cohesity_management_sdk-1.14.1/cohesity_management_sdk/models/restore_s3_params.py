# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.restore_s3_params_new_location_params


class RestoreS3Params(object):

    """Implementation of the 'RestoreS3Params' model.

    TODO: type description here.


    Attributes:

        is_original_location (bool): Flag specifying if it is an original
            location recovery or a new location.
        new_location_params (RestoreS3Params_NewLocationParams): Params
            specifying new location details.
        object_prefix (string): Object prefix for the recovered objects.
            E.g. "/", "/a/b". All operations at S3 Bucket (lookup, upload, etc.)
            will prepend this prefix to the Object name.
        overwrite_objects_in_bucket (bool): Flag specifying if we should
            overwrite if files are already present in the target location.
        prefixes_to_recover (list of string): Specifies all the prefixes which
            we have to recover. If it is empty, then magneto will recover the
            whole bucket.
        preserve_object_attributes (bool): Flag specifying if we should
            preserve object attributes at the time of restore.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "is_original_location":'isOriginalLocation',
        "new_location_params":'newLocationParams',
        "object_prefix": 'objectPrefix',
        "overwrite_objects_in_bucket":'overwriteObjectsInBucket',
        "prefixes_to_recover": 'prefixesToRecover',
        "preserve_object_attributes":'preserveObjectAttributes',
    }
    def __init__(self,
                 is_original_location=None,
                 new_location_params=None,
                 object_prefix=None,
                 overwrite_objects_in_bucket=None,
                 prefixes_to_recover=None,
                 preserve_object_attributes=None,
            ):

        """Constructor for the RestoreS3Params class"""

        # Initialize members of the class
        self.is_original_location = is_original_location
        self.new_location_params = new_location_params
        self.object_prefix = object_prefix
        self.overwrite_objects_in_bucket = overwrite_objects_in_bucket
        self.prefixes_to_recover = prefixes_to_recover
        self.preserve_object_attributes = preserve_object_attributes

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
        is_original_location = dictionary.get('isOriginalLocation')
        new_location_params = cohesity_management_sdk.models.restore_s3_params_new_location_params.RestoreS3Params_NewLocationParams.from_dictionary(dictionary.get('newLocationParams')) if dictionary.get('newLocationParams') else None
        object_prefix = dictionary.get('objectPrefix')
        overwrite_objects_in_bucket = dictionary.get('overwriteObjectsInBucket')
        prefixes_to_recover = dictionary.get('prefixesToRecover')
        preserve_object_attributes = dictionary.get('preserveObjectAttributes')

        # Return an object of this model
        return cls(
            is_original_location,
            new_location_params,
            object_prefix,
            overwrite_objects_in_bucket,
            prefixes_to_recover,
            preserve_object_attributes
)