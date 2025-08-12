import pandas as pd
import pytest
from config import CAMP_TOKEN

from byterat.filter import Filter, FilterGroup, FilterOperator
from byterat.sync.client import Client


class TestObservationMetrics:
  @classmethod
  def setup_class(cls):
    cls.client = Client(CAMP_TOKEN)

  def test_base(self):
    data = self.client.get_observation_metrics()
    assert data is not None
    assert len(data.data) > 0

  def test_by_dataset_key(self):
    data = self.client.get_observation_metrics_by_dataset_key('B14B-6')
    assert data is not None
    assert len(data.data) > 0

  def test_filter_group(self):
    filter_group = FilterGroup(
      [
        Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
        Filter('dataset_cycle', FilterOperator.GT, 500),
      ]
    )
    data = self.client.get_filtered_observation_data(filter_group)
    assert data is not None
    assert len(data.data) > 0

  def test_nested_filter_groups(self):
    inner_group = FilterGroup(
      [
        Filter('dataset_cycle', FilterOperator.GT, 500),
        Filter('dataset_cycle', FilterOperator.LT, 600),
      ]
    )
    outer_group = FilterGroup(
      [Filter('dataset_key', FilterOperator.EQ, 'B14B-6'), inner_group]
    )
    data = self.client.get_filtered_observation_data(outer_group)
    assert data is not None
    assert len(data.data) > 0

  def test_multiple_dataset_keys_filter(self):
    filters = [
      Filter('dataset_key', FilterOperator.IN, ['B14B-6', 'B14B-7']),
    ]

    data = self.client.get_filtered_observation_data(filters)
    assert data is not None
    assert len(data.data) > 0

  def test_numeric_comparison_filters(self):
    filters = FilterGroup(
      [
        Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
        Filter('dataset_cycle', FilterOperator.GTE, 500),
        Filter('dataset_cycle', FilterOperator.LTE, 600),
      ]
    )
    data = self.client.get_filtered_observation_data(filters)
    assert data is not None
    assert len(data.data) > 0

  def test_by_dataset_key_and_cycle(self):
    data = self.client.get_observation_metrics_by_dataset_key_and_dataset_cycle(
      'B14B-6', 570
    )
    assert data is not None
    assert len(data.data) > 0

  def test_by_filename(self):
    data = self.client.get_observation_metrics_by_filename(
      'ARGONNE_11_CFF-B14B-P6f.014'
    )
    assert data is not None
    assert len(data.data) > 0

  def test_continuation_token(self):
    data = self.client.get_observation_metrics_by_dataset_key('B14B-6')
    assert data is not None
    assert len(data.data) > 0

    next_data = self.client.get_observation_metrics_by_dataset_key(
      'B14B-6', continuation_token=data.continuation_token
    )
    assert next_data is not None

  @pytest.mark.skip(
    reason='Seems to error with connection errors. Only happens for `get_observation_metrics`. Not sure why, and local testing (running gql locally) causes computer to freeze. so havent been able to do testing'
  )
  def test_continuation_token_no_filter(self):
    data = self.client.get_observation_metrics(None)
    assert data is not None
    assert len(data.data) > 0

    next_data = self.client.get_observation_metrics(
      continuation_token=data.continuation_token
    )
    assert next_data is not None

  def test_simple_filter(self):
    filters = Filter('dataset_key', FilterOperator.EQ, 'B14B-6')
    data = self.client.get_filtered_observation_data(filters)

    assert data is not None
    assert len(data.data) > 0

  def test_simple_filter_list(self):
    filters = [
      Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
      Filter('dataset_cycle', FilterOperator.EQ, 570),
    ]

    data = self.client.get_filtered_observation_data(filters)

    assert data is not None
    assert len(data.data) > 0

    expected_data = (
      self.client.get_observation_metrics_by_dataset_key_and_dataset_cycle(
        'B14B-6', 570
      )
    )

    assert expected_data is not None
    assert len(expected_data.data) > 0

    assert False not in (expected_data.data.columns == data.data.columns)
    assert len(data.data) == len(expected_data.data)
    assert data.data.equals(expected_data.data)

  def test_simple_filtergroup(self):
    filters = FilterGroup(
      [
        Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
        Filter('dataset_cycle', FilterOperator.EQ, 570),
      ]
    )

    data = self.client.get_filtered_observation_data(filters)

    assert data is not None
    assert len(data.data) > 0

    expected_data = (
      self.client.get_observation_metrics_by_dataset_key_and_dataset_cycle(
        'B14B-6', 570
      )
    )

    assert expected_data is not None
    assert len(expected_data.data) > 0

    assert False not in (expected_data.data.columns == data.data.columns)
    assert len(data.data) == len(expected_data.data)
    assert data.data.equals(expected_data.data)

  def test_empty_result_handling(self):
    filters = FilterGroup(
      [
        Filter('dataset_key', FilterOperator.EQ, 'NONEXISTENT'),
        Filter('dataset_cycle', FilterOperator.EQ, 999999),
      ]
    )

    data = self.client.get_filtered_observation_data(filters)
    assert data is not None
    assert len(data.data) == 0
    assert data.continuation_token is None

  def test_get_all_filtered_data(self):
    filters = FilterGroup(
      [
        Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
        Filter('dataset_cycle', FilterOperator.GT, 500),
        Filter('dataset_cycle', FilterOperator.LT, 600),
      ]
    )

    # Get all data at once
    all_data = self.client.get_all_filtered_observation_data(filters)
    assert isinstance(all_data, pd.DataFrame)
    assert len(all_data) > 0

    # Compare with paginated approach
    paginated_data = []
    continuation_token = None

    while True:
      data = self.client.get_filtered_observation_data(
        filters, continuation_token=continuation_token
      )
      paginated_data.append(data.data)
      if not data.continuation_token:
        break
      continuation_token = data.continuation_token

    combined_paginated = pd.concat(paginated_data, ignore_index=True)
    assert len(all_data) == len(combined_paginated)
    assert all_data.equals(combined_paginated)

