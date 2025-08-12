# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class SqlPackage(object):

    """Implementation of the 'SqlPackage' model.

    Details can be found here https://tinyurl.com/ysryshrx

    Attributes:
        compression (int): Only applies to backup.
        max_parallelism (string): Specifies the degree of parallelism for
            concurrent operations running against a database. The default
            value is 8.
            Applies to backup/restore.
        verify_extraction (bool): Specifies whether the extracted schema model
            should be verified.
            If set to true, schema validation rules are run on the dacpac or bacpac.
            Only applies to backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "compression":'compression',
        "max_parallelism":'maxParallelism',
        "verify_extraction":'verifyExtraction'
    }

    def __init__(self,
                 compression=None,
                 max_parallelism=None,
                 verify_extraction=None):
        """Constructor for the SqlPackage class"""

        # Initialize members of the class
        self.compression = compression
        self.max_parallelism = max_parallelism
        self.verify_extraction = verify_extraction


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
        compression = dictionary.get('compression')
        max_parallelism = dictionary.get('maxParallelism')
        verify_extraction = dictionary.get('verifyExtraction')

        # Return an object of this model
        return cls(compression,
                   max_parallelism,
                   verify_extraction)


