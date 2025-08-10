import asyncio
from cryptonow import NOW

# تست sync
print("🟢 BTC (دلار):", NOW['BTC'])
print("🟢 اتریوم (تومان):", NOW['اتریوم', 'irr'])
print("🟢 اطلاعات کامل:", NOW.info['BTC'])

# تست async
async def test_async():
    price = await NOW.async_get('BTC')
    print("🔵 BTC (async):", price)

asyncio.run(test_async())
