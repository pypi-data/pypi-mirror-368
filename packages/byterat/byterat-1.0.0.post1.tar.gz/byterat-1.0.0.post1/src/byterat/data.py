import json

import pandas as pd


class ByteratData:
  def __init__(self, data: list[str], continuation_token: str | None) -> None:
    self.data: pd.DataFrame = pd.DataFrame([json.loads(entry) for entry in data])
    self.continuation_token: str | None = continuation_token
