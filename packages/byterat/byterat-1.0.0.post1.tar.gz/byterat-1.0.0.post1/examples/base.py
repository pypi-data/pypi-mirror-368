from byterat.client import ByteratClientSync

# Replace with API_KEY
API_TOKEN = '****************'


def main():
  client = ByteratClientSync(API_TOKEN)

  # Up to 100 entries are returned in one go by default.
  continuation_token = None
  while True:
    resp = client.get_observation_metrics_by_dataset_key('abcd', continuation_token)

    print(resp.data)

    continuation_token = resp.continuation_token
    if not continuation_token:
      break


if __name__ == '__main__':
  main()
