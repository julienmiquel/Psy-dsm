import os
from app import datastore_service, firestore_service, local_file_service

def get_database_service_instance():
    """
    Factory function to get the database service based on the environment variable.
    """
    service_type = os.getenv("DATABASE_SERVICE", "local")

    if service_type == "firestore":
        # TODO: The firestore_service.py implementation seems to be a mix of
        # datastore and firestore code, and may not work as expected.
        return firestore_service
    elif service_type == "local":
        return local_file_service
    elif service_type == "datastore":
        return datastore_service

# Centralized service instance
db_service = get_database_service_instance()
