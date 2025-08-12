from collections.abc import MutableSequence, Sequence
from enum import Enum
from typing import Iterable, Iterator, final, overload, override
import json


class FilterOperator(Enum):
  LT = 'lt'
  LTE = 'lte'
  EQ = 'equals'
  GTE = 'gte'
  GT = 'gt'
  CONTAINS = 'contains'
  NOT = 'not'
  STARTS_WITH = 'startsWith'
  ENDS_WITH = 'endsWith'
  SEARCH = 'search'
  NOT_CONTAINS = 'notContains'
  IN = 'in'
  NOT_IN = 'notIn'
  IS_NULL = 'isNull'
  IS_NOT_NULL = 'isNotNull'
  HAS = 'has'
  HAS_EVERY = 'hasEvery'
  HAS_SOME = 'hasSome'


class FilterGroupType(Enum):
  AND = 'and'
  OR = 'or'


type FilterDictRepr = dict[str, str | list[str]]
type FilterGroupGqlRepr = dict[
  str, str | list[FilterDictRepr] | list[FilterGroupGqlRepr]
]


@final
class Filter:
  def __init__(
    self,
    column: str,
    operator: FilterOperator,
    value: str | int | float | bool | list[str] | list[int] | list[bool] | list[float],
    mode: str = 'default',
  ) -> None:
    if mode not in ['default', 'insensitive']:
      raise Exception("Invalid mode. Must be one of ['default', 'insensitive']")

    self.column = column
    self.operator = operator
    self.value = value
    self.mode = mode

  def to_dict(self) -> FilterDictRepr:
    """
    Convert the filter to a dictionary format, which can be handy for serialization
    or sending as part of a GraphQL query.
    """
    value = self.value
    if isinstance(value, list):
      value = json.dumps(value) 
    else:
      value = str(value)

    data: dict[str, str | list[str]] = {
      'column': self.column,
      'operator': self.operator.value,  # Use .value to get the underlying string
      'value': value,
      'mode': self.mode,
    }

    return data
  @override
  def __repr__(self) -> str:
    return (
      f'Filter(column={self.column}, operator={self.operator}, '
      f'value={self.value}, mode={self.mode})'
    )


@final
class FilterGroup(MutableSequence['Filter | FilterGroup']):
  def __init__(
    self,
    filters: Sequence['Filter | FilterGroup'],
    mode: FilterGroupType = FilterGroupType.AND,
  ) -> None:
    self._filters = list(filters)
    self.mode = mode

  @override
  def append(self, value: 'Filter | FilterGroup') -> None:
    # Add the filter to the list of filters for this FilterGroup
    self._filters.append(value)

  def concat(
    self,
    other: 'Filter | FilterGroup | Iterable[Filter | FilterGroup] | Iterable[Filter] | Iterable[FilterGroup]',
  ) -> 'FilterGroup':
    if isinstance(other, Filter):
      # Add the filter to the list of filters for this FilterGroup
      _ = self._filters.append(other)
    elif isinstance(other, FilterGroup):
      # Merge the filter groups
      for filter in other._filters:
        self._filters.append(filter)
    else:
      # Merge the list to this filter group
      for filter in other:
        self._filters.append(filter)

    return self

  @override
  def remove(self, value: 'Filter | FilterGroup'):
    self._filters.remove(value)

  @overload
  def __getitem__(self, index: int) -> 'Filter | FilterGroup': ...
  @overload
  def __getitem__(self, index: slice) -> list['Filter | FilterGroup']: ...
  @override
  def __getitem__(
    self, index: int | slice
  ) -> 'Filter | FilterGroup | list[Filter | FilterGroup] | list[Filter] | list[FilterGroup]':
    return self._filters[index]

  @overload
  def __setitem__(self, index: int, value: 'Filter | FilterGroup') -> None: ...
  @overload
  def __setitem__(self, index: slice, value: Iterable[Filter]) -> None: ...
  @overload
  def __setitem__(self, index: slice, value: Iterable['FilterGroup']) -> None: ...
  @overload
  def __setitem__(
    self, index: slice, value: Iterable['Filter | FilterGroup']
  ) -> None: ...
  @override
  # Ignore this error for now. Can't figure out what override is missing and it seems to work so eh
  def __setitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
    self,
    index: int | slice,
    value: 'Filter | FilterGroup | Iterable[Filter | FilterGroup] | Iterable[Filter] | Iterable[FilterGroup]',
  ) -> None:
    if isinstance(index, int):
      if not isinstance(value, Filter | FilterGroup):
        raise TypeError('Int index assignment must be Filter or FilterGroup')
      self._filters[index] = value  # Handle single item assignment
    elif isinstance(index, slice):
      if not isinstance(value, Iterable):
        raise TypeError('Slice assignment must be an Iterable')
      # Convert the iterable to a list before assigning to the slice
      value_list: list['Filter | FilterGroup'] = list(value)
      slice_len = len(range(*index.indices(len(self._filters))))
      if len(value_list) != slice_len:
        raise ValueError(
          f'Slice assignment length mismatch. Expected {slice_len}, got {len(value_list)}'
        )
      self._filters[index] = value_list
    else:
      raise TypeError('Index must be an integer or a slice')

  @overload
  def __delitem__(self, index: int) -> None: ...
  @overload
  def __delitem__(self, index: slice) -> None: ...
  @override
  def __delitem__(self, index: int | slice) -> None:
    del self._filters[index]

  @override
  def __len__(self) -> int:
    return len(self._filters)

  @override
  def __iter__(self) -> Iterator['Filter | FilterGroup']:
    return iter(self._filters)

  @override
  def insert(self, index: int, value: 'Filter | FilterGroup') -> None:
    self._filters.insert(index, value)

  def to_gql_obj(self) -> FilterGroupGqlRepr:
    # Convert to gql compatible type
    filters: list[FilterDictRepr] = []
    groups: list[FilterGroupGqlRepr] = []
    for item in self._filters:
      if isinstance(item, Filter):
        filters.append(item.to_dict())
      else:
        groups.append(item.to_gql_obj())

    return {
      'type': self.mode.value,
      'filters': filters,
      'groups': groups,
    }
