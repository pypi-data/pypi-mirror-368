import pytest
from config import CAMP_TOKEN
from byterat.client import ByteratClientSync


class TestMetadata:
  @classmethod
  def setup_class(cls):
    cls.client = ByteratClientSync(CAMP_TOKEN)

  def test_base(self):
    data = self.client.get_metadata()
    assert data is not None

  def test_by_dataset_key(self):
    data = self.client.get_metadata_by_dataset_key('abcd')
    assert data is not None
