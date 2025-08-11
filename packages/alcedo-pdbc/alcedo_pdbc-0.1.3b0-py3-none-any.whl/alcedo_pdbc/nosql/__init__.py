# -*- encoding：utf-8 -*-
"""
@File :__init__.py
@Time :2025-7-16  14:18
@Author：AI Lab Morgan
"""
from .es import ElasticSearch
from .mongodb import MongoDB
from .dynamodb import DynamoDB
from .redis import Redis

__all__ = ['ElasticSearch',
           'MongoDB',
           'DynamoDB',
           'Redis'
           ]
