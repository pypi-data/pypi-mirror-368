from byterat.client import ByteratClientAsync
import asyncio

# Replace with API_KEY
API_TOKEN = "****************"


async def main():
    client = ByteratClientAsync(API_TOKEN)

    # Up to 100 entries are returned in one go by default.
    continuation_token = None
    while True:
        resp = await client.get_observation_metrics(continuation_token)
        continuation_token = resp.continuation_token
        if not continuation_token:
            break

        print(resp.data)

if __name__ == "__main__":
    asyncio.run(main)
