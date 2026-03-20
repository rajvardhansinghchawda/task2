import json
from flask import Flask, request, jsonify
import handler  # Import our Lambda handlers

app = Flask(__name__)

def _simulate_event(req):
    """
    Given a Flask request object, simulate an AWS API Gateway event dictionary 
    to pass into the Lambda handler.
    """
    body = req.get_data(as_text=True)
    query_params = {k: v for k, v in req.args.items()}
    
    event = {
        "httpMethod": req.method,
        "path": req.path,
        "queryStringParameters": query_params if query_params else None,
        "body": body if body else None,
        "headers": dict(req.headers)
    }
    return event

def _format_lambda_response(lambda_resp):
    """
    Given a Lambda returned dictionary (statusCode, body, headers),
    convert it back to a Flask JSON response.
    """
    status_code = lambda_resp.get("statusCode", 500)
    body = lambda_resp.get("body", "{}")
    headers = lambda_resp.get("headers", {})

    try:
        json_body = json.loads(body)
    except Exception:
        json_body = body

    return jsonify(json_body), status_code, headers


@app.route('/jobs', methods=['GET'])
def get_jobs():
    event = _simulate_event(request)
    # The second parameter is 'context', which we mock as None
    lambda_response = handler.get_jobs(event, None)
    return _format_lambda_response(lambda_response)

@app.route('/candidates', methods=['POST'])
def create_candidate():
    event = _simulate_event(request)
    lambda_response = handler.create_candidate(event, None)
    return _format_lambda_response(lambda_response)

@app.route('/applications', methods=['GET'])
def get_applications():
    event = _simulate_event(request)
    lambda_response = handler.get_applications(event, None)
    return _format_lambda_response(lambda_response)

if __name__ == '__main__':
    print("Starting local Flask server simulating AWS API Gateway...")
    print("Test at: http://127.0.0.1:3000")
    app.run(port=3000, debug=True)
