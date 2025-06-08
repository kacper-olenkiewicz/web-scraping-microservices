import asyncio
from bs4 import BeautifulSoup
from multiprocessing import Pool
import redis
import os
import json
import time

redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

async def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    for ticket in soup.select('.match-ticket'):
        event = {
            'title': ticket.select_one('.title').text.strip() if ticket.select_one('.title') else '',
            'date': ticket.select_one('.date').text.strip() if ticket.select_one('.date') else '',
            'prices': [price.text for price in ticket.select('.price')],
            'category': ticket.get('data-category', ''),
            'link': ticket.select_one('.buy-button')['href'] if ticket.select_one('.buy-button') else ''
        }
        events.append(event)
    return events

def process_chunk(html_chunk):
    return asyncio.run(parse_html(html_chunk))

if __name__ == '__main__':
    
    while True:
        try:
            with open('sample.html', 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            print("Brak pliku sample.html!")
            time.sleep(30)
            continue

        with Pool(os.cpu_count()) as pool:
            chunks = [html] * 4  
            results = pool.map(process_chunk, chunks)

        all_events = [event for sublist in results for event in sublist]
        if all_events:
            r.set('last_scrape', json.dumps(all_events))
            print(f"Zapisano {len(all_events)} wydarzeń do Redis")
        else:
            print("Brak danych do zapisania")

        time.sleep(30)  
