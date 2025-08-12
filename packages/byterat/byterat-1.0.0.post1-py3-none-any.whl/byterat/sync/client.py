from typing import final

import pandas as pd
from gql import Client as GQLClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport

from byterat.config import BYTERAT_URL
from byterat.data import ByteratData
from byterat.filter import Filter, FilterGroup
from byterat.queries import (
  GET_DATASET_CYCLE_DATA,
  GET_FILTERED_DATASET_CYCLE_DATA,
  GET_FILTERED_METADATA,
  GET_FILTERED_OBSERVATION_DATA,
  GET_METADATA,
  GET_OBSERVATION_DATA,
)

type _FilterGroup_t = Filter | list[Filter] | FilterGroup


@final
class Client:
  def __init__(self, token: str) -> None:
    self.token = token
    self.transport = RequestsHTTPTransport(
      url=BYTERAT_URL,
      headers={'workspace_api_key': token},
      verify=True,
      retries=3,
    )
    self.client = GQLClient(transport=self.transport, fetch_schema_from_transport=True)

  def __get_observation_metrics(
    self,
    continuation_token: str | None = None,
    dataset_key: str | None = None,
    dataset_cycle: int | None = None,
    file_name: str | None = None,
  ) -> ByteratData:
    query = gql(GET_OBSERVATION_DATA)

    variables: dict[str, str | int | None] = {'continuation_token': continuation_token}

    if dataset_key:
      variables['dataset_key'] = dataset_key

    if dataset_cycle:
      variables['dataset_cycle'] = dataset_cycle

    if file_name:
      variables['file_name'] = file_name

    resp = self.client.execute(query, variable_values=variables)

    data: list[str] = resp['get_observation_data_by_workspace']['data']
    continuation_token = resp['get_observation_data_by_workspace']['continuation_token']
    return ByteratData(data, continuation_token)

  def get_observation_metrics(
    self, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_observation_metrics(continuation_token=continuation_token)

  def get_observation_metrics_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_observation_metrics(
      continuation_token=continuation_token,
      dataset_key=dataset_key,
    )

  def get_observation_metrics_by_dataset_key_and_dataset_cycle(
    self, dataset_key: str, dataset_cycle: int, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_observation_metrics(
      continuation_token=continuation_token,
      dataset_key=dataset_key,
      dataset_cycle=dataset_cycle,
    )

  def get_observation_metrics_by_filename(
    self, file_name: str, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_observation_metrics(
      continuation_token=continuation_token,
      file_name=file_name,
    )

  def __get_dataset_cycle_metrics(
    self,
    continuation_token: str | None = None,
    dataset_key: str | None = None,
    dataset_cycle: int | None = None,
    file_name: str | None = None,
  ) -> ByteratData:
    query = gql(GET_DATASET_CYCLE_DATA)

    variables: dict[str, str | int | None] = {'continuation_token': continuation_token}

    if dataset_key:
      variables['dataset_key'] = dataset_key

    if dataset_cycle:
      variables['dataset_cycle'] = dataset_cycle

    if file_name:
      variables['file_name'] = file_name

    resp = self.client.execute(query, variable_values=variables)

    data: list[str] = resp['get_dataset_cycle_data_by_workspace']['data']
    continuation_token = resp['get_dataset_cycle_data_by_workspace'][
      'continuation_token'
    ]
    return ByteratData(data, continuation_token)

  def get_dataset_cycle_data(
    self, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_dataset_cycle_metrics(
      continuation_token=continuation_token,
    )

  def get_dataset_cycle_data_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_dataset_cycle_metrics(
      continuation_token=continuation_token,
      dataset_key=dataset_key,
    )

  def get_dataset_cycle_data_by_dataset_key_and_dataset_cycle(
    self, dataset_key: str, dataset_cycle: int, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_dataset_cycle_metrics(
      continuation_token=continuation_token,
      dataset_key=dataset_key,
      dataset_cycle=dataset_cycle,
    )

  def get_dataset_cycle_data_by_filename(
    self, file_name: str, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_dataset_cycle_metrics(
      continuation_token=continuation_token,
      file_name=file_name,
    )

  def __get_metadata(
    self,
    continuation_token: str | None = None,
    dataset_key: str | None = None,
  ) -> ByteratData:
    query = gql(GET_METADATA)
    variables = {'continuation_token': continuation_token}

    if dataset_key:
      variables['dataset_key'] = dataset_key

    resp = self.client.execute(query, variable_values=variables)

    data: list[str] = resp['get_metadata_by_workspace']['data']
    continuation_token = resp['get_metadata_by_workspace']['continuation_token']
    return ByteratData(data, continuation_token)

  def get_metadata(self, continuation_token: str | None = None) -> ByteratData:
    return self.__get_metadata(continuation_token=continuation_token)

  def get_metadata_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return self.__get_metadata(
      continuation_token=continuation_token, dataset_key=dataset_key
    )

  def __get_filtered_data(
    self,
    filters: _FilterGroup_t,
    query_info: dict[str, str] = GET_FILTERED_OBSERVATION_DATA,
    continuation_token: str | None = None,
  ):
    query = gql(query_info['query'])

    if type(filters) is FilterGroup:
      fg = filters
    elif type(filters) is list:
      # Assume list of Filter
      # Assume FilterGroupType.AND
      fg = FilterGroup(filters)
    elif type(filters) is Filter:
      fg = FilterGroup([filters])
    else:
      raise Exception(f'Invalid filters: {filters}. Type: {type(filters)}')

    variables = {
      'continuation_token': continuation_token,
      'filter_group': fg.to_gql_obj(),
    }

    resp = self.client.execute(query, variable_values=variables)

    data: list[str] = resp[query_info['endpoint']]['data']
    continuation_token = resp[query_info['endpoint']]['continuation_token']
    return ByteratData(data, continuation_token)

  def get_filtered_observation_data(
    self,
    filters: _FilterGroup_t,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_OBSERVATION_DATA,
    )

  def get_filtered_dataset_cycle_data(
    self,
    filters: _FilterGroup_t,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_DATASET_CYCLE_DATA,
    )

  def get_filtered_metadata(
    self,
    filters: _FilterGroup_t,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_METADATA,
    )

  def __get_all_filtered_data(
    self,
    filters: _FilterGroup_t,
    query_info: dict[str, str] = GET_FILTERED_OBSERVATION_DATA,
  ) -> pd.DataFrame:
    """
    Retrieve all filtered data by iteratively fetching data until there is no continuation token.
    **Note**: This may run for a while depending on the amount of data to be retrieved. This will be
    particularly noticable for the observation data

    Args:
        filters (_FilterGroup_t): The filter criteria for retrieving data.
        query_info (dict[str, str], optional): Additional query information. Defaults to GET_FILTERED_OBSERVATION_DATA.

    Returns:
        pd.DataFrame: A DataFrame containing the concatenated filtered data.
    """
    data_frames = []
    continuation_token = None

    while True:
      resp = self.__get_filtered_data(
        query_info=query_info, filters=filters, continuation_token=continuation_token
      )
      data_frames.append(resp.data)
      continuation_token = resp.continuation_token
      if continuation_token is None:
        break

    # Return concatenated DataFrame if any data was collected, else return an empty DataFrame
    return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()

  def get_all_filtered_observation_data(
    self,
    filters: _FilterGroup_t,
  ) -> pd.DataFrame:
    return self.__get_all_filtered_data(filters)

  def get_all_filtered_dataset_cycle_data(
    self,
    filters: _FilterGroup_t,
  ) -> pd.DataFrame:
    return self.__get_all_filtered_data(
      filters, query_info=GET_FILTERED_DATASET_CYCLE_DATA
    )

  def get_all_filtered_metadata(
    self,
    filters: _FilterGroup_t,
  ) -> pd.DataFrame:
    return self.__get_all_filtered_data(filters, query_info=GET_FILTERED_METADATA)

  def get_dataset_list(
    self,
    filters: _FilterGroup_t,
  ):
    # Based on metadata? Assumption currently
    data = self.get_all_filtered_metadata(filters=filters)
    return data['dataset_key'].unique()
