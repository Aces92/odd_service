from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

AUTH_SERVICE_URL = "https://auth_service-klbd.onrender.com/verify"

RATE_LIMIT = {}
MAX_REQUESTS = 5
WINDOW = 60 #seconds

@app.route("/odd/<int:n>")
def odd_numbers(n):

   # get api key First
   api_key = request.headers.get("X-API-KEY")
   if not api_key:
     return jsonify({"error": "API key required"}), 401
   
   #rate limiting
   current_time = time.time()
   user_requests = RATE_LIMIT.get(api_key, [])

   #remove old requests outside the window
   user_requests = [
      t for t in user_requests if current_time - t < WINDOW
   ]

   if len(user_requests) >= MAX_REQUESTS:
      return jsonify({"error": "Rate limit exceeded"}), 429
   
   #save current request
   user_requests.append(current_time)
   RATE_LIMIT[api_key] = user_requests
   
   #Auth service verification
   auth_response = requests.post(
      AUTH_SERVICE_URL,
      headers={"X-API-KEY": api_key},
      )    
   if auth_response.status_code != 200:
      return jsonify({"error": "Unauthorized"}), 403
   
   # business logic (odd_numbers)
   result = []
   for i in range (1,n + 1):
      if i % 2 != 0:
        result.append(i)

   return jsonify({
   "input": n,
   "odd_numbers": result
 })

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)