"""
Standardized response utilities
"""
from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """표준화된 성공 응답"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error occurred", status_code=400, error_code=None):
    """표준화된 에러 응답"""
    response = {
        'success': False,
        'message': message
    }
    if error_code:
        response['error_code'] = error_code
    return jsonify(response), status_code

def paginated_response(items, page, per_page, total, message="Success"):
    """페이지네이션 응답"""
    return jsonify({
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })