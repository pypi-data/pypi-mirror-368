# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class RestoreSpfileOrPfileInfo(object):
    """Implementation of the 'RestoreSpfileOrPfileInfo' model.

    Specifies information related to restoring Spfile/Pfile.

    Attributes:
        file_location (string): Specifies the location where spfile/file will be restored. If this is empty and shouldRestoreSpfileOrPfile is true we restore at default location: $ORACLE_HOME/dbs
        should_restore_spfile_or_pfile (bool): Specifies whether to restore spfile/pfile or skip it.
    """

    _names = {
        "file_location":"fileLocation",
        "should_restore_spfile_or_pfile":"shouldRestoreSpfileOrPfile",
    }

    def __init__(self,
                 file_location=None,
                 should_restore_spfile_or_pfile=None):
        """Constructor for the RestoreSpfileOrPfileInfo class"""

        self.file_location = file_location
        self.should_restore_spfile_or_pfile = should_restore_spfile_or_pfile


    @classmethod
    def from_dictionary(cls, dictionary):
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

        file_location = dictionary.get('fileLocation')
        should_restore_spfile_or_pfile = dictionary.get('shouldRestoreSpfileOrPfile')

        return cls(
            file_location,
            should_restore_spfile_or_pfile
        )