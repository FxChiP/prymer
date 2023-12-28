import asyncio

import aiohttp

import shapyro

async def get_IP(_):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://canhazip.com') as resp:
            return await resp.text()
        
async def nested_get_IP(_):
    ip = await get_IP(_)
    return {ip: {"ip": get_IP}}

async def main(): 
    my_IP = shapyro.port({}, {"my_IP": nested_get_IP})
    print(f"My IP raw {my_IP}")
    r_IP = await my_IP
    print(f"My IP resolved {r_IP}")

    my_IP2 = shapyro.port({}, [0, 2, nested_get_IP, 5, "beach"])
    print(f"test again raw {my_IP2}")
    r_IP = await my_IP2
    print(f"test again resolved {r_IP}")

if __name__=="__main__":
    asyncio.run(main())