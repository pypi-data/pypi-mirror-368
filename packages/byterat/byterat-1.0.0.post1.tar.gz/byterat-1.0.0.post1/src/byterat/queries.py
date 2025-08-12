"""
get_observation_data(dataset_key: String, dataset_cycle: Int, file_name: String, continuation_token: String): API_Data!
get_dataset_cycle_data(dataset_key: String, dataset_cycle: Int, file_name: String, continuation_token: String): API_Data!
get_metadata(dataset_key: String, continuation_token: String): API_Data!
"""

GET_OBSERVATION_DATA = """
    query($dataset_key: String, $dataset_cycle: Int, $file_name: String, $continuation_token: String) {
        get_observation_data_by_workspace(dataset_key: $dataset_key, dataset_cycle: $dataset_cycle, file_name: $file_name, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
"""

GET_DATASET_CYCLE_DATA = """
    query($dataset_key: String, $dataset_cycle: Int, $file_name: String, $continuation_token: String) {
        get_dataset_cycle_data_by_workspace(dataset_key: $dataset_key, dataset_cycle: $dataset_cycle, file_name: $file_name, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
"""

GET_METADATA = """
    query($dataset_key: String, $continuation_token: String) {
        get_metadata_by_workspace(dataset_key: $dataset_key, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
"""

GET_FILTERED_OBSERVATION_DATA = {
  'endpoint': 'get_filtered_observation_data',
  'query': """
    query($filter_group: API_Filter_Group!, $continuation_token: String) {
        get_filtered_observation_data(filter_group: $filter_group, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
""",
}

GET_FILTERED_DATASET_CYCLE_DATA = {
  'endpoint': 'get_filtered_dataset_cycle_data',
  'query': """
    query($filter_group: API_Filter_Group!, $continuation_token: String) {
        get_filtered_dataset_cycle_data(filter_group: $filter_group, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
""",
}

GET_FILTERED_METADATA = {
  'endpoint': 'get_filtered_metadata',
  'query': """
    query($filter_group: API_Filter_Group!, $continuation_token: String) {
        get_filtered_metadata(filter_group: $filter_group, continuation_token: $continuation_token) {
            data
            continuation_token
        }
    }
""",
}
