import sys
from datetime import datetime, timedelta
import logging

import aiohttp
import asyncio


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None



async def get_exchange(nums_of_days: int, exch: str=None):
    nums_of_days = int(nums_of_days)
    exchange_rates = []
    
    
    for num in range(nums_of_days):
        #for exch in ['EUR', 'USD']:
        
        dl = datetime.now() - timedelta(num)
        shift = dl.strftime("%d.%m.%Y")
        
        result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        
        if result:
            rates = result.get("exchangeRate")
            currency_data = {}
            for exch in ['EUR', 'USD']:
                exc, = list(filter(lambda element: element["currency"] == exch, rates))
                
                currency_data.update([(exch, {
                    "sale": round(exc["saleRateNB"], 1), 
                    "purchase": round(exc["purchaseRateNB"], 1)
                })])
            exchange_rates.append({shift: currency_data})
            
            
    return exchange_rates if exchange_rates else "No data for such a period"
        

async def main():
    if len(sys.argv) > 10:
        print("Usage: python privat_api.py <number_of_days>")
        return
    results = []
    
    print(sys.argv)
    
    rates = await get_exchange(sys.argv[1])
    #rates_exch = await get_exchange(sys.argv[1], sys.argv[2])
    results.extend(rates)
        
    print(results)
    
if __name__ == "__main__":
    asyncio.run(main())
