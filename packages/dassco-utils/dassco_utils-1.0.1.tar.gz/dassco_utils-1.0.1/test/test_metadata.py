import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import json
from datetime import datetime
import unittest
from dassco_utils.metadata import MetadataHandler

class TestMetadata(unittest.TestCase):

    def test_create_json_metadata(self):

        data = {
            'asset_guid': '7e8-8-08-0c-1b-15-2-003-04-000-0d4437',
            'date_asset_taken': '2024-08-16T08:44:57+02:00',
            'collection': 'Entomology',
            'digitiser': 'John Doe',
            'external_publishers': [{"name": "newspaper"}],
            'file_format': 'tif',   
            'payload_type': 'image',
            'pipeline_name': 'PIPEHERB0001',
            'preparation_type': ['sheet'],
            'workstation_name': 'WORKHERB0001',
            'institution': 'NHMD',
            'funding': ["DaSSCo", "DiSSCo"],
            'legality': {'copyright':"Kanon"},
            'issues': [{'category':"buffer", 'name':"crash", 'timestamp':'2024-08-16T08:44:57+02:00', 'status':'ARCHIVED', 'description':"good job", 'notes':"again!!", 'solved':False}],
            'specify_attachment_remarks': "Im so readfy for specify",
            'specify_attachment_title': "Payload type, collection, guid and prep type mesh"
        }

        handler = MetadataHandler(**data)

        expected_json_output = {
            "asset_created_by":None,
            "asset_deleted_by":None,
            "asset_guid":"7e8-8-08-0c-1b-15-2-003-04-000-0d4437",
            "asset_pid":None,
            "asset_subject":None,
            "asset_updated_by":None,
            "audited":False,
            "audited_by":None,
            "barcode":[],
            "camera_setting_control":None,
            "collection":"Entomology",
            "complete_digitiser_list":[],
            "date_asset_created_ars":None,
            "date_asset_deleted_ars":None,
            "date_asset_finalised":None,
            "date_asset_taken":"2024-08-16T08:44:57+02:00",
            "date_asset_updated_ars":None,
            "date_audited":None,
            "date_metadata_created_ars":None,
            "date_metadata_ingested":None,
            "date_metadata_updated_ars":None,
            "date_pushed_to_specify":None,
            "digitiser":"John Doe",
            "external_publishers":[{"name": "newspaper"}],
            "file_format":"tif",
            "funding":["DaSSCo", "DiSSCo"],
            "institution":"NHMD",
            "issues":[{'category':"buffer", 'name':"crash", 'timestamp':'2024-08-16T08:44:57+02:00', 'status':'ARCHIVED', 'description':"good job", 'notes':"again!!", 'solved':False}],
            "legality":{"copyright": "Kanon", "license": None, "credit": None},
            "make_public":False,
            "metadata_created_by":None,
            "metadata_source":None,
            "metadata_updated_by":None,
            "metadata_version":"v3.0.4",
            "mime_type":None,
            "mos_id":None,
            "multi_specimen":False,
            "parent_guids":[],
            "payload_type":"image",
            "pipeline_name":"PIPEHERB0001",
            "preparation_type":["sheet"],
            "push_to_specify":False,
            "restricted_access":[],
            "session_id":None,
            'specify_attachment_remarks': "Im so readfy for specify",
            'specify_attachment_title': "Payload type, collection, guid and prep type mesh",
            "specimen_pid":None,
            "status":None,
            "tags":{},
            "workstation_name":"WORKHERB0001",
            "has_thumbnail":False,
            }
        metadata_dict = handler.metadata_to_dict()

        for key, value in metadata_dict.items():
            
            if key == "date_metadata_ingested":
                continue
            
            if isinstance(value, list):
                list_number = 0
                for entry in value:
                    
                    if isinstance(entry, dict):
                        for key2, value2 in entry.items():
                            
                            if isinstance(value2, datetime) and value2 is not None:
                                value2 = datetime.strftime(value2, "%Y-%m-%dT%H:%M:%S%Z")
                                                        
                            self.assertEqual(value2, expected_json_output[key][list_number][key2], f"Failed: {key2}:{value2}")

                        list_number =+ 1
                    else:
                        self.assertEqual(value, expected_json_output[key], f"Failed: {key}:{value}")
                        continue  
            
            else:
                
                if isinstance(value, datetime) and value is not None:
                    value = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S%Z")

                self.assertEqual(value, expected_json_output[key], f"Failed: {key}:{value}")

        metadata_json = handler.metadata_to_json()

        mdata = json.loads(metadata_json)

        for key, value in mdata.items():
            
            if key == "date_metadata_ingested":
                continue

            self.assertEqual(value, expected_json_output[key], f"Failed: {key}:{value}")

        handler.update_metadata_value("asset_created_by", "Test User")

        metadata_dict = handler.metadata_to_dict()

        self.assertEqual(metadata_dict["asset_created_by"], "Test User", "Failed to update metadata value")

        handler = MetadataHandler(**data)

        handler.save_metadata_to_file("test_metadata.json")

        self.assertTrue(os.path.isfile("test_metadata.json"), "Failed to save metadata to file")

        with open("test_metadata.json", "r", encoding="utf-8") as f:
            saved_metadata = json.load(f)

        for key, value in saved_metadata.items():
            
            if key == "date_metadata_ingested":
                continue

            self.assertEqual(value, expected_json_output[key], f"Failed: {key}:{value}")

        handler = MetadataHandler(metadata_path="test_metadata.json")

        metadata_dict = handler.metadata_to_dict()

        self.assertTrue(isinstance(metadata_dict, dict), "Failed to load metadata from file")

        os.remove("test_metadata.json")


if __name__ == "__main__":
    unittest.main()