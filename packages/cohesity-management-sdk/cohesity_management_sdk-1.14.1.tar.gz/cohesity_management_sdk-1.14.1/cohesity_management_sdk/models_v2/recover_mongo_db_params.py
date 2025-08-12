# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_mongo_db_snapshot_params

class RecoverMongoDBParams(object):

    """Implementation of the 'Recover MongoDB params.' model.

    Specifies the parameters to recover MongoDB objects.

    Attributes:
        recover_to (long|int): Specifies the 'Source Registration ID' of the
            source where the objects are to be recovered. If this is not
            specified, the recovery job will recover to the original
            location.
        overwrite (bool): Set to true to overwrite an existing object at the
            destination. If set to false, and the same object exists at the
            destination, then recovery will fail for that object.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster.
        bandwidth_mbps (long|int): Specifies the maximum network bandwidth
            that each concurrent IO Stream can use for exchanging data with
            the cluster.
        warnings (list of string): This field will hold the warnings in cases
            where the job status is SucceededWithWarnings.
        snapshots (list of RecoverMongoDBSnapshotParams): Specifies the local
            snapshot ids of the Objects to be recovered.
        suffix (string): A suffix that is to be applied to all recovered
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots":'snapshots',
        "recover_to":'recoverTo',
        "overwrite":'overwrite',
        "concurrency":'concurrency',
        "bandwidth_mbps":'bandwidthMBPS',
        "warnings":'warnings',
        "suffix":'suffix'
    }

    def __init__(self,
                 snapshots=None,
                 recover_to=None,
                 overwrite=None,
                 concurrency=None,
                 bandwidth_mbps=None,
                 warnings=None,
                 suffix=None):
        """Constructor for the RecoverMongoDBParams class"""

        # Initialize members of the class
        self.recover_to = recover_to
        self.overwrite = overwrite
        self.concurrency = concurrency
        self.bandwidth_mbps = bandwidth_mbps
        self.warnings = warnings
        self.snapshots = snapshots
        self.suffix = suffix


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
        snapshots = None
        if dictionary.get("snapshots") is not None:
            snapshots = list()
            for structure in dictionary.get('snapshots'):
                snapshots.append(cohesity_management_sdk.models_v2.recover_mongo_db_snapshot_params.RecoverMongoDBSnapshotParams.from_dictionary(structure))
        recover_to = dictionary.get('recoverTo')
        overwrite = dictionary.get('overwrite')
        concurrency = dictionary.get('concurrency')
        bandwidth_mbps = dictionary.get('bandwidthMBPS')
        warnings = dictionary.get('warnings')
        suffix = dictionary.get('suffix')

        # Return an object of this model
        return cls(snapshots,
                   recover_to,
                   overwrite,
                   concurrency,
                   bandwidth_mbps,
                   warnings,
                   suffix)


