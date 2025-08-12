from dassco_utils.metadata import MetadataHandler

metadata_input = {
    'asset_guid': '1234',
    'date_asset_taken': '2024-08-16T08:44:57+02:00',
    'collection': 'test_collection',
    'digitiser': "John Doe",
    'file_format': "tif",
    'payload_type': 'image',
    'pipeline_name': "test_pipeline",
    'preparation_type': ['sheet'],
    'workstation_name': "test_workstation",
    'institution': "test_institution",
    'complete_digitiser_list': [],
    'funding': ['NHMD'],
    'metadata_source': 'Metadata Service v3.0.0',
    'status': 'PRE_PROCESSING'
}

metadata_handler = MetadataHandler(**metadata_input)
json = metadata_handler.metadata_to_json()
print(json)
