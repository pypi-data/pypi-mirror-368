# -*- coding: utf-8 -*-


class PhysicalEnvJobParams(object):

    """Implementation of the 'PhysicalEnvJobParams' model.

    Protection Job parameters applicable to 'kPhysical' Environment type.
      Specifies job parameters applicable for all 'kPhysical' Environment type Protection
      Sources in a Protection Job.

    Attributes:
        cobmr_backup (bool): Specifies whether to enable CoBMR backup.
        file_path_filters (FileFilteringPolicy): Specifies filters on the backup objects like files and directories.
          Specifying filters decide which objects within a source should be backed
          up. If this field is not specified, then all of the objects within the source
          will be backed up.
        incremental_snapshot_upon_restart (bool): 'If true, performs an incremental backup after server restarts.
          Otherwise a full backup is done. NOTE: This is applicable only to Windows
          servers. If not set, default value is false.'

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cobmr_backup":'cobmrBackup',
        "file_path_filters":'filePathFilters',
        "incremental_snapshot_upon_restart":'incrementalSnapshotUponRestart'
    }

    def __init__(self,
                 cobmr_backup=None,
                 file_path_filters=None,
                 incremental_snapshot_upon_restart=None
                 ):
        """Constructor for the PhysicalEnvJobParams class"""

        # Initialize members of the class
        self.cobmr_backup = cobmr_backup
        self.file_path_filters = file_path_filters
        self.incremental_snapshot_upon_restart = incremental_snapshot_upon_restart


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
        cobmr_backup = dictionary.get('cobmrBackup')
        file_path_filters = dictionary.get('filePathFilters')
        incremental_snapshot_upon_restart = dictionary.get('incrementalSnapshotUponRestart')

        # Return an object of this model
        return cls(
            cobmr_backup,
            file_path_filters,
            incremental_snapshot_upon_restart)