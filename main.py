from web3 import Web3, AsyncWeb3
import asyncio

async def main():
    w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/ykF8oPKAU18g2B2PzbVDrzTwgdF2-v16'))

    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://eth-mainnet.g.alchemy.com/v2/ykF8oPKAU18g2B2PzbVDrzTwgdF2-v16'))

    w3 = Web3(Web3.WebsocketProvider('wss://eth-mainnet.g.alchemy.com/v2/ykF8oPKAU18g2B2PzbVDrzTwgdF2-v16'))

    print(f"Running main...")
    print(f"Is w3 connected? ... {w3.is_connected()}\n")

    i = 1
    for key, value in w3.eth.get_block('latest').items():
        print(f"+ Item {i} - {key} : {value}")
        i += 1

asyncio.run(main())
