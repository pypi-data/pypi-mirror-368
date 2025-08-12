# -*- coding: utf-8 -*-
# Copyright 2023 Cohesity Inc.


class CassandraTableTypeEnum(object):
    """Implementation of the 'CassandraTableType' enum.

    Specifies Type of Keyspace.
    Specifies the type of an Cassandra keyspace entity.

       Attributes:
        KREGULAR: TODO: type description here.
        KGRAPH: TODO: type description here.
        KSYSTEM: TODO: type description here.

    """

    KREGULAR = "kRegular"

    KGRAPH = "kGraph"

    KSYSTEM = "kSystem"
