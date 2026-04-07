import pytest
import multiprocessing
import time
import requests
from main import app as flask_app

def run_server(app, port):
    app.run(port=port, use_reloader=False, debug=False)

@pytest.fixture(scope="session")
def live_server():
    port = 5001
    flask_app.config['TESTING'] = True
    server_process = multiprocessing.Process(target=run_server, args=(flask_app, port))
    server_process.start()
    
    # Wait for server to be ready
    for _ in range(10):
        try:
            res = requests.get(f"http://127.0.0.1:{port}/")
            if res.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            
    class ServerInfo:
        def __init__(self, port):
            self.url = f"http://127.0.0.1:{port}"
            
    yield ServerInfo(port)
    server_process.terminate()
    server_process.join()
