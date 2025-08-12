# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_pdb_object_info
import cohesity_management_sdk.models_v2.key_value_pair

class OraclePdbRestoreParams(object):

    """Implementation of the 'OraclePdbRestoreParams' model.

    Specifies information about the list of pdbs to be restored.

    Attributes:
        drop_duplicate_pdb (bool): Specifies if the PDB should be ignored if a
            PDB already exists with same name.
        include_in_restore (bool): Specifies whether to restore or skip the provided PDBs list.
        pdb_objects (list of OraclePdbObjectInfo): Specifies list of PDB
            objects to restore.
        rename_pdb_map (KeyValuePair): Specifies the new PDB name mapping to existing PDBs.
        restore_to_existing_cdb (bool): Specifies if pdbs should be restored
            to an existing CDB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "drop_duplicate_pdb":'dropDuplicatePDB',
        "include_in_restore":'includeInRestore',
        "pdb_objects":'pdbObjects',
        "rename_pdb_map":'renamePdbMap',
        "restore_to_existing_cdb":'restoreToExistingCdb'
    }

    def __init__(self,
                 drop_duplicate_pdb=None,
                 include_in_restore=None,
                 pdb_objects=None,
                 rename_pdb_map=None,
                 restore_to_existing_cdb=None):
        """Constructor for the OraclePdbRestoreParams class"""

        # Initialize members of the class
        self.drop_duplicate_pdb = drop_duplicate_pdb
        self.include_in_restore = include_in_restore
        self.pdb_objects = pdb_objects
        self.rename_pdb_map = rename_pdb_map
        self.restore_to_existing_cdb = restore_to_existing_cdb


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
        drop_duplicate_pdb = dictionary.get('dropDuplicatePDB')
        include_in_restore = dictionary.get('includeInRestore')
        pdb_objects = None
        if dictionary.get("pdbObjects") is not None:
            pdb_objects = list()
            for structure in dictionary.get('pdbObjects'):
                pdb_objects.append(cohesity_management_sdk.models_v2.oracle_pdb_object_info.OraclePdbObjectInfo.from_dictionary(structure))
        rename_pdb_map = None
        if dictionary.get('renamePdbMap') is not None:
            rename_pdb_map = list()
            for structure in dictionary.get('renamePdbMap'):
                rename_pdb_map.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        restore_to_existing_cdb = dictionary.get('restoreToExistingCdb')

        # Return an object of this model
        return cls(drop_duplicate_pdb,
                   include_in_restore,
                   pdb_objects,
                   rename_pdb_map,
                   restore_to_existing_cdb)