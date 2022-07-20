import flask


def make_error(status_code, message):
    response = flask.jsonify({
        'status': status_code,
        'message': message,
    })
    response.status_code = status_code
    return response
