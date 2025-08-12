from byterat.filter import Filter, FilterOperator
from byterat.sync.client import Client

client = Client('testing')

filters = [
  Filter('dataset_key', FilterOperator.EQ, 'B14B-6'),
  Filter('dataset_cycle', FilterOperator.EQ, 570),
]

data = client.get_filtered_observation_data(filters)

print(f'len: {len(data.data.columns)}\n{data.data.columns}')

expected_data = client.get_observation_metrics_by_dataset_key_and_dataset_cycle(
  'B14B-6', 570
)
print(f'len: {len(expected_data.data.columns)}\n{expected_data.data.columns}')

print(expected_data.data.columns == data.data.columns)

print(f'{data.data["dataset_cycle"].unique()}')
print(f'{expected_data.data["dataset_cycle"].unique()}')

print(f'{data.data["dataset_key"].unique()}')
print(f'{expected_data.data["dataset_key"].unique()}')
