import pytest
from config import CAMP_TOKEN, INVALID_TOKEN

from byterat.client import ByteratClientSync


def test_client_creation():
  client = ByteratClientSync(CAMP_TOKEN)
  assert client is not None, 'Unable to create client'


@pytest.mark.skip(
  reason='Currently will succeed, should add a check for the propelauth key in the client'
)
def test_invalid_token_failure():
  ByteratClientSync(INVALID_TOKEN)
