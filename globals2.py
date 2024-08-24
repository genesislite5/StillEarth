import aiohttp
from bs4 import BeautifulSoup
import asyncio

environmental_cache = {}

async def is_environmentally_friendly(item_name):
    if item_name in environmental_cache:
        print(f"Cache hit for {item_name}: {environmental_cache[item_name]}") # Debug print
        return environmental_cache[item_name]
    
    search_url = f"https://www.google.com/search?q=is+{item_name}+environmentally+friendly"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
            if "not environmentally friendly" in soup.text.lower() or "harmful to the environment" in soup.text.lower():
                print(f"{item_name} is not environmentally friendly") # Debug print
                environmental_cache[item_name] = False
                return False
            
            if "environmentally friendly" in soup.text.lower():
                environmental_cache[item_name] = True
                print(f"{item_name} is environmentally friendly") # Debug print
                return True
            
            environmental_cache[item_name] = False
            print(f"No clear answer found for {item_name}, defaulting to not environmentally friendly") # Debug print
            return False

def sync_is_environmentally_friendly(item_name):
    return asyncio.run(is_environmentally_friendly(item_name))