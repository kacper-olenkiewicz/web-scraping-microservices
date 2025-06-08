from flask import Flask, render_template
import redis
import os
import json

app = Flask(__name__)

redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

@app.route('/')
def index():
    data = []
    try:
        raw = r.get('last_scrape')
        if raw:
            loaded = json.loads(raw)
            data = [ev for ev in loaded if isinstance(ev, dict) and 'prices' in ev]
            print(f"Pobrano {len(data)} eventów z Redis")
    except Exception as e:
        print(f"Błąd pobierania danych z Redis: {e}")

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
