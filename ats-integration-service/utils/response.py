from flask import jsonify


def ok(data, status_code: int = 200):
    return jsonify(data), status_code


def error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code

