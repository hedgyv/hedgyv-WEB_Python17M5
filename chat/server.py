import asyncio
import logging
import websockets 
import names
import aiohttp
import httpx
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

#______________Ku4ma
# async def request(url: str) -> dict | str:
#     async with httpx.AsyncClient() as client:
#         r = await client.get(url)
#         if r.status_code == 200:
#             result = r.json()
#             return result
#         else:
#             return "Не вийшло в мене взнати курс. Приват не відповідає :)"

# async def get_exchange():
#     response = await request(f'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
#     # переробить на більш придатний результат
#     return str(response)
#______________Ku4ma

#______________14WEB
async def get_exchange():
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5') as resp:
            if resp.status == 200:
                r = await resp.json()
                currency_data = {}
                for exch in ['EUR', 'USD']:
                    exc, = list(filter(lambda el: el["ccy"] == exch, r))
                    print(exc)
                    currency_data.update([(exch, {
                    "sale": exc["sale"], 
                    "purchase": exc["buy"]
                })])
                
                print(str(currency_data))    
            #return f"{exch}: {exc}"
            return str(currency_data)
#______________14WEB


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message == 'exchange':
                m = await get_exchange()
                await self.send_to_clients(m)
            else:    
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())