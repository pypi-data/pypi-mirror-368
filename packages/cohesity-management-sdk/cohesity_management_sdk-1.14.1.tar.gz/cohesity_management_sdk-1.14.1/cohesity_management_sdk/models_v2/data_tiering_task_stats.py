# -*- coding: utf-8 -*-


class DataTieringTaskStats(object):

    """Implementation of the 'DataTieringTaskStats' model.

    Specifies the stats of data tiering task.

    Attributes:
        logical_size_bytes (long|int): Specifies total logical size of
            object(s) in bytes.
        bytes_written (long|int): Specifies total size of data in bytes
            written after taking backup.
        bytes_read (long|int): Specifies total logical bytes read for creating
            the snapshot.
        entity_count (long|int): Specifies total entity count.
        changed_entity_count (long|int): Specifies changed entity count.
        is_tiering_goal_met (bool): Specifies whether tiering goal has been
            met.
        total_tiered_bytes (long|int): Specifies total amount of data
            successfully tiered from the NAS source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "logical_size_bytes":'logicalSizeBytes',
        "bytes_written":'bytesWritten',
        "bytes_read":'bytesRead',
        "entity_count":'entityCount',
        "changed_entity_count":'changedEntityCount',
        "is_tiering_goal_met":'isTieringGoalMet',
        "total_tiered_bytes":'totalTieredBytes'
    }

    def __init__(self,
                 logical_size_bytes=None,
                 bytes_written=None,
                 bytes_read=None,
                 entity_count=None,
                 changed_entity_count=None,
                 is_tiering_goal_met=False,
                 total_tiered_bytes=None):
        """Constructor for the DataTieringTaskStats class"""

        # Initialize members of the class
        self.logical_size_bytes = logical_size_bytes
        self.bytes_written = bytes_written
        self.bytes_read = bytes_read
        self.entity_count = entity_count
        self.changed_entity_count = changed_entity_count
        self.is_tiering_goal_met = is_tiering_goal_met
        self.total_tiered_bytes = total_tiered_bytes


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
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        bytes_written = dictionary.get('bytesWritten')
        bytes_read = dictionary.get('bytesRead')
        entity_count = dictionary.get('entityCount')
        changed_entity_count = dictionary.get('changedEntityCount')
        is_tiering_goal_met = dictionary.get("isTieringGoalMet") if dictionary.get("isTieringGoalMet") else False
        total_tiered_bytes = dictionary.get('totalTieredBytes')

        # Return an object of this model
        return cls(logical_size_bytes,
                   bytes_written,
                   bytes_read,
                   entity_count,
                   changed_entity_count,
                   is_tiering_goal_met,
                   total_tiered_bytes)


