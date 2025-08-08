import asyncio
from autumn import Autumn


async def main():
    client = Autumn(
        token="am_sk_test_zzKIp2wyp6QkCsUekw7OOGC4tqQg1AdfLAFFiXpDtG")

    res = await client.checkout(customer_id="123", product_id="pro")
    print(res)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
