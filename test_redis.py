
# test_redis.py

import asyncio

from app.db.redis import redis_client


async def main():
    try:
        response = await redis_client.ping()
        print("Redis connected successfully:", response)

    except Exception as error:
        print("Redis connection failed:", error)

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
