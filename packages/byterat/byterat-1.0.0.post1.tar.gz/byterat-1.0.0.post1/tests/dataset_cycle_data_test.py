import pytest
from config import CAMP_TOKEN
from byterat.client import ByteratClientSync


class TestDatasetCycleData:
  @classmethod
  def setup_class(cls):
    cls.client = ByteratClientSync(CAMP_TOKEN)

  def test_base(self):
    data = self.client.get_dataset_cycle_data()
    assert data is not None

  def test_by_dataset_key(self):
    data = self.client.get_dataset_cycle_data_by_dataset_key('B14B-6')
    assert data is not None

  def test_by_dataset_key_and_cycle(self):
    data = self.client.get_dataset_cycle_data_by_dataset_key_and_dataset_cycle(
      'B14B-6', 570
    )
    assert data is not None

  def test_by_filename(self):
    data = self.client.get_dataset_cycle_data_by_filename('ARGONNE_11_CFF-B14B-P6f.014')
    assert data is not None
