import os
from app import datastore_service, firestore_service, local_file_service
import importlib

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
    elif service_type == "local":
        # importlib.reload(local_file_service)
        return local_file_service
    elif service_type == "datastore":
        importlib.reload(datastore_service)
        return datastore_service

# Centralized service instance
db_service = get_database_service_instance()
