"""
Client API routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from models import Client

client_bp = Blueprint('clients', __name__)

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

@client_bp.route('', methods=['GET'])
def get_clients():
    """Get client list with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Client.query
        
        if search:
            query = query.filter(
                db.or_(
                    Client.name.contains(search),
                    Client.email.contains(search),
                    Client.company.contains(search)
                )
            )
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        clients = [client.to_dict() for client in pagination.items]
        
        return paginated_response(
            clients, page, per_page, pagination.total, "Clients retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve clients: {str(e)}", 500)

@client_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get specific client"""
    try:
        client = Client.query.get(client_id)
        
        if not client:
            return error_response("Client not found", 404)
        
        return success_response(client.to_dict(), "Client retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve client: {str(e)}", 500)

@client_bp.route('', methods=['POST'])
def create_client():
    """Create new client"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        if not data.get('name') or not data.get('email'):
            return error_response("Name and email are required", 400)
        
        # Check if email already exists
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            return error_response("Email already exists", 409)
        
        client = Client(
            name=data['name'],
            email=data['email'],
            company=data.get('company'),
            role=data.get('role', 'user')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return success_response(client.to_dict(), "Client created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create client: {str(e)}", 500)

@client_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update client"""
    try:
        client = Client.query.get(client_id)
        
        if not client:
            return error_response("Client not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Check if email is being changed and if it already exists
        if 'email' in data and data['email'] != client.email:
            existing_client = Client.query.filter_by(email=data['email']).first()
            if existing_client:
                return error_response("Email already exists", 409)
        
        # Update fields
        if 'name' in data:
            client.name = data['name']
        if 'email' in data:
            client.email = data['email']
        if 'company' in data:
            client.company = data['company']
        if 'role' in data:
            client.role = data['role']
        if 'is_active' in data:
            client.is_active = data['is_active']
        
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(client.to_dict(), "Client updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update client: {str(e)}", 500)

@client_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete client"""
    try:
        client = Client.query.get(client_id)
        
        if not client:
            return error_response("Client not found", 404)
        
        # Check if client has campaigns
        if client.campaigns:
            return error_response("Cannot delete client with existing campaigns", 409)
        
        db.session.delete(client)
        db.session.commit()
        
        return success_response(None, "Client deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete client: {str(e)}", 500)