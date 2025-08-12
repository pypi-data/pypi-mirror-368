import pytest
from config import CAMP_TOKEN

from byterat.filter import Filter, FilterGroup, FilterGroupType, FilterOperator
from byterat.sync.client import Client


class TestObservationMetrics:
  @classmethod
  def setup_class(cls):
    cls.client: Client = Client(CAMP_TOKEN)

  def test_filter_group(self):
    filters = [Filter('dataset_key', FilterOperator.EQ, 'B14B-6')]
    fg = FilterGroup(filters)

    assert fg.mode == FilterGroupType.AND
    assert len(fg) == 1
    assert fg[0] == filters[0]

    new_filter = Filter('dataset_key', FilterOperator.CONTAINS, 'B14B-6')
    fg.append(new_filter)

    assert len(fg) == 2
    assert fg[1] == new_filter

    fg[0] = new_filter

    assert len(fg) == 2
    assert fg[0] == new_filter

    fg[0:1] = filters
    assert len(fg) == 2
    assert fg[0:1] == filters

    with pytest.raises(ValueError):
      fg[0:2] = filters

    fg.remove(filters[0])
    assert len(fg) == 1
    assert fg[0] == new_filter

    fg = fg.concat(filters)
    
    assert len(fg) == 2
    assert fg[0] == new_filter
    assert fg[1] == filters[0]

    concat_fg = fg.concat(new_filter)
    assert len(fg) == 3
    assert fg[2] == new_filter
    assert concat_fg == fg

    # Just tests that we **can** iterate through it
    for _ in fg:
      pass

    fg.insert(0, filters[0])
    assert len(fg) == 4
    assert fg[0] == filters[0]

    del fg[0]
    assert len(fg) == 3

    del fg[0:3]
    assert len(fg) == 0

  def test_or_filter_group(self):
    filters = [
      Filter('dataset_cycle', FilterOperator.EQ, 1),
      Filter('dataset_cycle', FilterOperator.EQ, 2),
    ]
    fg = FilterGroup(filters, mode=FilterGroupType.OR)

    assert fg.mode == FilterGroupType.OR
    assert len(fg) == 2

    resp = self.client.get_filtered_observation_data(fg)

    assert resp is not None
    assert len(resp.data) > 0

    dataset_cycles = resp.data['dataset_cycle'].unique()
    assert len(dataset_cycles) == 2
    assert 1 in dataset_cycles
    assert 2 in dataset_cycles
