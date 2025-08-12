from .models import MetadataModel
import os
import json
import datetime

class MetadataHandler:

    def __init__(self, metadata_path=None, **kwargs):
        """
        Initialize the MetadataHandler object.
        If metadata_path is provided, load metadata from file.
        Otherwise, initialize using kwargs.

        :param metadata_path: Path to existing metadata JSON file.
        :param kwargs: Metadata fields if not using a file.
        """
        try:
            copenhagen_tz = datetime.timezone(datetime.timedelta(hours=2))
            metadata_created_date = datetime.datetime.now(copenhagen_tz).replace(microsecond=0).isoformat()
            if metadata_path is not None:
                if not os.path.isfile(metadata_path):
                    raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata_dict = json.load(f)
                self.__metadata = MetadataModel(**metadata_dict)
            else:
                self.__metadata = MetadataModel(**kwargs, date_metadata_ingested=metadata_created_date)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize metadata: {e}")

    def metadata_to_json(self) -> str:
        """
        Return the metadata as a formatted JSON string
        """
        return self.__metadata.model_dump_json(indent=2)

    def metadata_to_dict(self) -> dict:
        """
        Return the metadata as a dictionary
        """
        return self.__metadata.model_dump()

    def update_metadata_value(self, key: str, value):
        """
        Update a specific metadata field with a new value.
        :param key: The metadata field to update.
        :param value: The new value for the metadata field.
        """
        if hasattr(self.__metadata, key):
            setattr(self.__metadata, key, value)
        else:
            raise KeyError(f"Metadata field '{key}' does not exist.")
    
    def save_metadata_to_file(self, file_path: str):
        """
        Save the current metadata to a JSON file.
        :param file_path: Path to the file where metadata will be saved.
        """
        try:
            m_dict = self.metadata_to_dict()
            converted_dict = self.convert_datetimes(m_dict)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(converted_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save metadata to file: {e}")
        
    def convert_datetimes(self, obj):
        """
        Recursively convert datetime objects in a dictionary or list to ISO format strings.        
        :param obj: The object to convert (can be a dict, list, or datetime).
        """
        if isinstance(obj, dict):
            return {k: self.convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_datetimes(item) for item in obj]
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return obj