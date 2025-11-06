"""
This module acts as a factory to select and initialize the database service
based on the `DATABASE_SERVICE` environment variable.
"""

import os
import importlib

from app import datastore_service, firestore_service, local_file_service


def get_database_service_instance():
    """
    Factory function to get the database service based on the environment variable.
    """
    service_type = os.getenv("DATABASE_SERVICE", "local")

    if service_type == "firestore":
        # TODO: The firestore_service.py implementation seems to be a mix of
        # datastore and firestore code, and may not work as expected.
        importlib.reload(firestore_service)
        return firestore_service
    if service_type == "local":
        return local_file_service
    if service_type == "datastore":
        importlib.reload(datastore_service)
        return datastore_service

    # Default to local if the service_type is unknown
    return local_file_service


# Centralized service instance
db_service = get_database_service_instance()
