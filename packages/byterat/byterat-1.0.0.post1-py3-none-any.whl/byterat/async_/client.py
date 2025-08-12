from typing import final

from gql import gql
from gql.client import Client as GQLClient
from gql.transport.aiohttp import AIOHTTPTransport

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


@final
class Client:
  def __init__(self, token: str) -> None:
    self.token: str = token
    self.transport: AIOHTTPTransport = AIOHTTPTransport(
      BYTERAT_URL,
      headers={'workspace_api_key': token},
    )
    self.client: GQLClient = GQLClient(
      transport=self.transport, fetch_schema_from_transport=True
    )

  async def __get_observation_metrics(
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

    async with self.client as session:
      resp = await session.execute(query, variable_values=variables)

    data: list[str] = resp['get_observation_data_by_workspace']['data']
    continuation_token = resp['get_observation_data_by_workspace']['continuation_token']
    return ByteratData(data, continuation_token)

  async def get_observation_metrics(
    self, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_observation_metrics(continuation_token=continuation_token)

  async def get_observation_metrics_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_observation_metrics(
      dataset_key=dataset_key, continuation_token=continuation_token
    )

  async def get_observation_metrics_by_dataset_key_and_dataset_cycle(
    self, dataset_key: str, dataset_cycle: int, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_observation_metrics(
      dataset_key=dataset_key,
      dataset_cycle=dataset_cycle,
      continuation_token=continuation_token,
    )

  async def get_observation_metrics_by_filename(
    self, file_name: str, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_observation_metrics(
      file_name=file_name,
      continuation_token=continuation_token,
    )

  async def __get_metdata(
    self,
    continuation_token: str | None = None,
    dataset_key: str | None = None,
  ) -> ByteratData:
    query = gql(GET_METADATA)
    variables = {'continuation_token': continuation_token}

    if dataset_key:
      variables['dataset_key'] = dataset_key

    async with self.client as session:
      resp = await session.execute(query, variable_values=variables)

    data: list[str] = resp['get_metadata_by_workspace']['data']
    continuation_token = resp['get_metadata_by_workspace']['continuation_token']
    return ByteratData(data, continuation_token)

  async def get_metadata(self, continuation_token: str | None = None) -> ByteratData:
    return await self.__get_metdata(continuation_token=continuation_token)

  async def get_metadata_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_metdata(
      dataset_key=dataset_key, continuation_token=continuation_token
    )

  async def __get_dataset_cycle_metrics(
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

    async with self.client as session:
      resp = await session.execute(query, variable_values=variables)

    data: list[str] = resp['get_dataset_cycle_data_by_workspace']['data']
    continuation_token = resp['get_dataset_cycle_data_by_workspace'][
      'continuation_token'
    ]
    return ByteratData(data, continuation_token)

  async def get_dataset_cycle_data(
    self, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_dataset_cycle_metrics(continuation_token=continuation_token)

  async def get_dataset_cycle_data_by_dataset_key(
    self, dataset_key: str, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_dataset_cycle_metrics(
      dataset_key=dataset_key, continuation_token=continuation_token
    )

  async def get_dataset_cycle_data_by_dataset_key_and_dataset_cycle(
    self, dataset_key: str, dataset_cycle: int, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_dataset_cycle_metrics(
      dataset_key=dataset_key,
      dataset_cycle=dataset_cycle,
      continuation_token=continuation_token,
    )

  async def get_dataset_cycle_data_by_filename(
    self, file_name: str, continuation_token: str | None = None
  ) -> ByteratData:
    return await self.__get_dataset_cycle_metrics(
      file_name=file_name,
      continuation_token=continuation_token,
    )

  async def __get_filtered_data(
    self,
    filters: Filter | list[Filter] | FilterGroup,
    query_info: dict[str, str] = GET_FILTERED_OBSERVATION_DATA,
    continuation_token: str | None = None,
  ):
    query = gql(query_info['query'])

    if isinstance(filters, FilterGroup):
      fg = filters
    elif isinstance(filters, list):
      # Assume list has items of type Filter
      # Assume FilterGroupType.AND
      fg = FilterGroup(filters)
    elif type(filters) is Filter:
      fg = FilterGroup([filters])

    variables = {
      'continuation_token': continuation_token,
      'filter_group': fg.to_gql_obj(),
    }

    async with self.client as session:
      resp = await session.execute(query, variable_values=variables)

    data: list[str] = resp[query_info['endpoint']]['data']
    continuation_token = resp[query_info['endpoint']]['continuation_token']
    return ByteratData(data, continuation_token)

  async def get_filtered_observation_data(
    self,
    filters: Filter | list[Filter] | FilterGroup,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return await self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_OBSERVATION_DATA,
    )

  async def get_filtered_dataset_cycle_data(
    self,
    filters: Filter | list[Filter] | FilterGroup,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return await self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_DATASET_CYCLE_DATA,
    )

  async def get_filtered_metadata(
    self,
    filters: Filter | list[Filter] | FilterGroup,
    continuation_token: str | None = None,
  ) -> ByteratData:
    return await self.__get_filtered_data(
      filters=filters,
      continuation_token=continuation_token,
      query_info=GET_FILTERED_METADATA,
    )
