from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day"],
    storage_uri="memory://",
)

@app.route("/test")
@limiter.limit("2 per day", deduct_when=lambda res: res.status_code == 200)
def test():
    fail = request.args.get('fail')
    if fail:
        return jsonify(error="failed"), 500
    return jsonify(success=True)

if __name__ == "__main__":
    with app.test_client() as client:
        print("Success 1:", client.get("/test").status_code)
        print("Success 2:", client.get("/test").status_code)
        print("Success 3 (should fail):", client.get("/test").status_code)
        
        limiter.reset()
        print("\nResetting...")
        print("Fail 1:", client.get("/test?fail=1").status_code)
        print("Fail 2:", client.get("/test?fail=1").status_code)
        print("Fail 3:", client.get("/test?fail=1").status_code)
        print("Fail 4:", client.get("/test?fail=1").status_code)
        print("Success 1:", client.get("/test").status_code)
        print("Success 2:", client.get("/test").status_code)
        print("Success 3 (should fail):", client.get("/test").status_code)
