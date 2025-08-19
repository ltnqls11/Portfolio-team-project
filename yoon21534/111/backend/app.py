from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from datetime import datetime
from config import config

# Flask application initialization
app = Flask(__name__)

# Configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Extension initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Response helper functions
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

# Models will be imported after app context is created

# Basic routes
@app.route('/')
def index():
    """API 정보 및 사용 가능한 엔드포인트"""
    endpoints = {
        'clients': '/api/clients',
        'campaigns': '/api/campaigns',
        'creators': '/api/creators',
        'copy_variants': '/api/copy-variants',
        'email_templates': '/api/email-templates',
        'outreach': '/api/outreach',
        'dashboard_stats': '/api/stats/dashboard',
        'health': '/health'
    }
    
    return success_response({
        'message': 'Marketing Automation RPA API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': endpoints
    }, "API is running successfully")

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    
    return success_response({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }, "Health check completed")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return error_response("Resource not found", 404)

@app.errorhandler(400)
def bad_request(error):
    return error_response("Bad request", 400)

@app.errorhandler(405)
def method_not_allowed(error):
    return error_response("Method not allowed", 405)

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return error_response("Internal server error", 500)

# ============================================================================
# CLIENT API ENDPOINTS
# ============================================================================

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get client list with pagination"""
    try:
        from models import Client
        
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

@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get specific client"""
    try:
        from models import Client
        client = Client.query.get(client_id)
        
        if not client:
            return error_response("Client not found", 404)
        
        return success_response(client.to_dict(), "Client retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve client: {str(e)}", 500)

@app.route('/api/clients', methods=['POST'])
def create_client():
    """Create new client"""
    try:
        from models import Client
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

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update client"""
    try:
        from models import Client
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

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete client"""
    try:
        from models import Client
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

# ============================================================================
# CAMPAIGN API ENDPOINTS
# ============================================================================

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get campaign list with pagination and filters"""
    try:
        from models import Campaign
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        client_id = request.args.get('client_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search', '')
        
        query = Campaign.query
        
        if client_id:
            query = query.filter_by(client_id=client_id)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                db.or_(
                    Campaign.name.contains(search),
                    Campaign.description.contains(search)
                )
            )
        
        pagination = query.order_by(Campaign.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        campaigns = [campaign.to_dict() for campaign in pagination.items]
        
        return paginated_response(
            campaigns, page, per_page, pagination.total, "Campaigns retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve campaigns: {str(e)}", 500)

@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get specific campaign"""
    try:
        from models import Campaign
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return error_response("Campaign not found", 404)
        
        return success_response(campaign.to_dict(), "Campaign retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve campaign: {str(e)}", 500)

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create new campaign"""
    try:
        from models import Campaign, Client
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        if not data.get('name') or not data.get('client_id'):
            return error_response("Name and client_id are required", 400)
        
        # Verify client exists
        client = Client.query.get(data['client_id'])
        if not client:
            return error_response("Client not found", 404)
        
        campaign = Campaign(
            name=data['name'],
            description=data.get('description'),
            product_info=data.get('product_info'),
            keywords=data.get('keywords'),
            reference_links=data.get('reference_links'),
            target_audience=data.get('target_audience'),
            budget=data.get('budget'),
            client_id=data['client_id'],
            status=data.get('status', 'draft')
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        return success_response(campaign.to_dict(), "Campaign created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create campaign: {str(e)}", 500)

@app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """Update campaign"""
    try:
        from models import Campaign
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return error_response("Campaign not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update fields
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'product_info' in data:
            campaign.product_info = data['product_info']
        if 'keywords' in data:
            campaign.keywords = data['keywords']
        if 'reference_links' in data:
            campaign.reference_links = data['reference_links']
        if 'target_audience' in data:
            campaign.target_audience = data['target_audience']
        if 'budget' in data:
            campaign.budget = data['budget']
        if 'status' in data:
            campaign.status = data['status']
        if 'scheduled_at' in data:
            campaign.scheduled_at = datetime.fromisoformat(data['scheduled_at']) if data['scheduled_at'] else None
        
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(campaign.to_dict(), "Campaign updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update campaign: {str(e)}", 500)

@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete campaign"""
    try:
        from models import Campaign
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return error_response("Campaign not found", 404)
        
        db.session.delete(campaign)
        db.session.commit()
        
        return success_response(None, "Campaign deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete campaign: {str(e)}", 500)

# ============================================================================
# CREATOR API ENDPOINTS
# ============================================================================

@app.route('/api/creators', methods=['GET'])
def get_creators():
    """Get creator list with pagination and filters"""
    try:
        from models import Creator
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        platform = request.args.get('platform')
        category = request.args.get('category')
        min_followers = request.args.get('min_followers', type=int)
        max_followers = request.args.get('max_followers', type=int)
        search = request.args.get('search', '')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = Creator.query.filter_by(is_active=is_active)
        
        if platform:
            query = query.filter_by(platform=platform)
        if category:
            query = query.filter_by(category=category)
        if min_followers:
            query = query.filter(Creator.followers_count >= min_followers)
        if max_followers:
            query = query.filter(Creator.followers_count <= max_followers)
        if search:
            query = query.filter(
                db.or_(
                    Creator.name.contains(search),
                    Creator.username.contains(search),
                    Creator.display_name.contains(search)
                )
            )
        
        pagination = query.order_by(Creator.followers_count.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        creators = [creator.to_dict() for creator in pagination.items]
        
        return paginated_response(
            creators, page, per_page, pagination.total, "Creators retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve creators: {str(e)}", 500)

@app.route('/api/creators/<int:creator_id>', methods=['GET'])
def get_creator(creator_id):
    """Get specific creator"""
    try:
        from models import Creator
        creator = Creator.query.get(creator_id)
        
        if not creator:
            return error_response("Creator not found", 404)
        
        return success_response(creator.to_dict(), "Creator retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve creator: {str(e)}", 500)

@app.route('/api/creators', methods=['POST'])
def create_creator():
    """Create new creator"""
    try:
        from models import Creator
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        if not data.get('name') or not data.get('platform'):
            return error_response("Name and platform are required", 400)
        
        creator = Creator(
            name=data['name'],
            email=data.get('email'),
            platform=data['platform'],
            username=data.get('username'),
            display_name=data.get('display_name'),
            followers_count=data.get('followers_count', 0),
            engagement_rate=data.get('engagement_rate', 0.0),
            category=data.get('category'),
            bio=data.get('bio'),
            location=data.get('location'),
            collaboration_rate=data.get('collaboration_rate'),
            profile_image_url=data.get('profile_image_url'),
            external_id=data.get('external_id'),
            contact_info=data.get('contact_info'),
            profile_data=data.get('profile_data'),
            language=data.get('language', 'ko'),
            is_verified=data.get('is_verified', False)
        )
        
        db.session.add(creator)
        db.session.commit()
        
        return success_response(creator.to_dict(), "Creator created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create creator: {str(e)}", 500)

@app.route('/api/creators/<int:creator_id>', methods=['PUT'])
def update_creator(creator_id):
    """Update creator"""
    try:
        from models import Creator
        creator = Creator.query.get(creator_id)
        
        if not creator:
            return error_response("Creator not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update fields
        updatable_fields = [
            'name', 'email', 'platform', 'username', 'display_name',
            'followers_count', 'engagement_rate', 'category', 'bio',
            'location', 'collaboration_rate', 'profile_image_url',
            'external_id', 'contact_info', 'profile_data', 'language',
            'is_verified', 'is_active', 'avg_likes', 'avg_comments'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(creator, field, data[field])
        
        if 'last_post_date' in data and data['last_post_date']:
            creator.last_post_date = datetime.fromisoformat(data['last_post_date'])
        
        creator.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(creator.to_dict(), "Creator updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update creator: {str(e)}", 500)

@app.route('/api/creators/<int:creator_id>', methods=['DELETE'])
def delete_creator(creator_id):
    """Delete creator (soft delete by setting is_active=False)"""
    try:
        from models import Creator
        creator = Creator.query.get(creator_id)
        
        if not creator:
            return error_response("Creator not found", 404)
        
        # Soft delete
        creator.is_active = False
        creator.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(None, "Creator deactivated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete creator: {str(e)}", 500)

# ============================================================================
# COPY VARIANT API ENDPOINTS
# ============================================================================

@app.route('/api/copy-variants', methods=['GET'])
def get_copy_variants():
    """Get copy variants list with pagination and filters"""
    try:
        from models import CopyVariant
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        campaign_id = request.args.get('campaign_id', type=int)
        channel = request.args.get('channel')
        is_selected = request.args.get('is_selected')
        
        query = CopyVariant.query
        
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)
        if channel:
            query = query.filter_by(channel=channel)
        if is_selected is not None:
            query = query.filter_by(is_selected=is_selected.lower() == 'true')
        
        pagination = query.order_by(CopyVariant.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        copy_variants = [variant.to_dict() for variant in pagination.items]
        
        return paginated_response(
            copy_variants, page, per_page, pagination.total, "Copy variants retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve copy variants: {str(e)}", 500)

@app.route('/api/copy-variants/<int:variant_id>', methods=['GET'])
def get_copy_variant(variant_id):
    """Get specific copy variant"""
    try:
        from models import CopyVariant
        variant = CopyVariant.query.get(variant_id)
        
        if not variant:
            return error_response("Copy variant not found", 404)
        
        return success_response(variant.to_dict(), "Copy variant retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve copy variant: {str(e)}", 500)

@app.route('/api/copy-variants', methods=['POST'])
def create_copy_variant():
    """Create new copy variant"""
    try:
        from models import CopyVariant, Campaign
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['channel', 'content', 'campaign_id']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Verify campaign exists
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return error_response("Campaign not found", 404)
        
        variant = CopyVariant(
            channel=data['channel'],
            content=data['content'],
            title=data.get('title'),
            hashtags=data.get('hashtags'),
            campaign_id=data['campaign_id'],
            is_selected=data.get('is_selected', False),
            ai_generated=data.get('ai_generated', True),
            generation_prompt=data.get('generation_prompt'),
            character_count=len(data['content'])
        )
        
        db.session.add(variant)
        db.session.commit()
        
        return success_response(variant.to_dict(), "Copy variant created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create copy variant: {str(e)}", 500)

@app.route('/api/copy-variants/<int:variant_id>', methods=['PUT'])
def update_copy_variant(variant_id):
    """Update copy variant"""
    try:
        from models import CopyVariant
        variant = CopyVariant.query.get(variant_id)
        
        if not variant:
            return error_response("Copy variant not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update fields
        if 'content' in data:
            variant.content = data['content']
            variant.character_count = len(data['content'])
        if 'title' in data:
            variant.title = data['title']
        if 'hashtags' in data:
            variant.hashtags = data['hashtags']
        if 'is_selected' in data:
            variant.is_selected = data['is_selected']
        if 'generation_prompt' in data:
            variant.generation_prompt = data['generation_prompt']
        
        variant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(variant.to_dict(), "Copy variant updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update copy variant: {str(e)}", 500)

@app.route('/api/copy-variants/<int:variant_id>', methods=['DELETE'])
def delete_copy_variant(variant_id):
    """Delete copy variant"""
    try:
        from models import CopyVariant
        variant = CopyVariant.query.get(variant_id)
        
        if not variant:
            return error_response("Copy variant not found", 404)
        
        db.session.delete(variant)
        db.session.commit()
        
        return success_response(None, "Copy variant deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete copy variant: {str(e)}", 500)

# ============================================================================
# EMAIL TEMPLATE API ENDPOINTS
# ============================================================================

@app.route('/api/email-templates', methods=['GET'])
def get_email_templates():
    """Get email templates list with pagination and filters"""
    try:
        from models import EmailTemplate
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        client_id = request.args.get('client_id', type=int)
        category = request.args.get('category')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = EmailTemplate.query.filter_by(is_active=is_active)
        
        if client_id:
            query = query.filter_by(client_id=client_id)
        if category:
            query = query.filter_by(category=category)
        
        pagination = query.order_by(EmailTemplate.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        templates = [template.to_dict() for template in pagination.items]
        
        return paginated_response(
            templates, page, per_page, pagination.total, "Email templates retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve email templates: {str(e)}", 500)

@app.route('/api/email-templates/<int:template_id>', methods=['GET'])
def get_email_template(template_id):
    """Get specific email template"""
    try:
        from models import EmailTemplate
        template = EmailTemplate.query.get(template_id)
        
        if not template:
            return error_response("Email template not found", 404)
        
        return success_response(template.to_dict(), "Email template retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve email template: {str(e)}", 500)

@app.route('/api/email-templates', methods=['POST'])
def create_email_template():
    """Create new email template"""
    try:
        from models import EmailTemplate, Client
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['name', 'subject', 'content', 'client_id']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Verify client exists
        client = Client.query.get(data['client_id'])
        if not client:
            return error_response("Client not found", 404)
        
        template = EmailTemplate(
            name=data['name'],
            subject=data['subject'],
            content=data['content'],
            client_id=data['client_id'],
            variables=data.get('variables'),
            category=data.get('category'),
            language=data.get('language', 'ko'),
            is_default=data.get('is_default', False)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return success_response(template.to_dict(), "Email template created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create email template: {str(e)}", 500)

@app.route('/api/email-templates/<int:template_id>', methods=['PUT'])
def update_email_template(template_id):
    """Update email template"""
    try:
        from models import EmailTemplate
        template = EmailTemplate.query.get(template_id)
        
        if not template:
            return error_response("Email template not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update fields
        updatable_fields = [
            'name', 'subject', 'content', 'variables', 'category',
            'language', 'is_default', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(template, field, data[field])
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(template.to_dict(), "Email template updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update email template: {str(e)}", 500)

@app.route('/api/email-templates/<int:template_id>', methods=['DELETE'])
def delete_email_template(template_id):
    """Delete email template (soft delete by setting is_active=False)"""
    try:
        from models import EmailTemplate
        template = EmailTemplate.query.get(template_id)
        
        if not template:
            return error_response("Email template not found", 404)
        
        # Check if template is being used in outreach records
        if template.outreach_records:
            # Soft delete
            template.is_active = False
            template.updated_at = datetime.utcnow()
            db.session.commit()
            return success_response(None, "Email template deactivated successfully")
        else:
            # Hard delete if not used
            db.session.delete(template)
            db.session.commit()
            return success_response(None, "Email template deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete email template: {str(e)}", 500)

# ============================================================================
# OUTREACH RECORD API ENDPOINTS
# ============================================================================

@app.route('/api/outreach', methods=['GET'])
def get_outreach_records():
    """Get outreach records list with pagination and filters"""
    try:
        from models import OutreachRecord
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        campaign_id = request.args.get('campaign_id', type=int)
        creator_id = request.args.get('creator_id', type=int)
        status = request.args.get('status')
        
        query = OutreachRecord.query
        
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)
        if creator_id:
            query = query.filter_by(creator_id=creator_id)
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(OutreachRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        records = [record.to_dict() for record in pagination.items]
        
        return paginated_response(
            records, page, per_page, pagination.total, "Outreach records retrieved successfully"
        )
    except Exception as e:
        return error_response(f"Failed to retrieve outreach records: {str(e)}", 500)

@app.route('/api/outreach/<int:record_id>', methods=['GET'])
def get_outreach_record(record_id):
    """Get specific outreach record"""
    try:
        from models import OutreachRecord
        record = OutreachRecord.query.get(record_id)
        
        if not record:
            return error_response("Outreach record not found", 404)
        
        return success_response(record.to_dict(), "Outreach record retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve outreach record: {str(e)}", 500)

@app.route('/api/outreach', methods=['POST'])
def create_outreach_record():
    """Create new outreach record"""
    try:
        from models import OutreachRecord, Campaign, Creator
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['campaign_id', 'creator_id', 'email_address']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Verify campaign and creator exist
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return error_response("Campaign not found", 404)
        
        creator = Creator.query.get(data['creator_id'])
        if not creator:
            return error_response("Creator not found", 404)
        
        record = OutreachRecord(
            campaign_id=data['campaign_id'],
            creator_id=data['creator_id'],
            email_address=data['email_address'],
            template_id=data.get('template_id'),
            email_subject=data.get('email_subject'),
            email_content=data.get('email_content'),
            personalization_data=data.get('personalization_data'),
            status=data.get('status', 'pending')
        )
        
        db.session.add(record)
        db.session.commit()
        
        return success_response(record.to_dict(), "Outreach record created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create outreach record: {str(e)}", 500)

@app.route('/api/outreach/<int:record_id>', methods=['PUT'])
def update_outreach_record(record_id):
    """Update outreach record"""
    try:
        from models import OutreachRecord
        record = OutreachRecord.query.get(record_id)
        
        if not record:
            return error_response("Outreach record not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update fields
        updatable_fields = [
            'email_subject', 'email_content', 'personalization_data',
            'status', 'error_message', 'response_data', 'retry_count',
            'external_message_id', 'delivery_status'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(record, field, data[field])
        
        # Handle datetime fields
        datetime_fields = ['sent_at', 'opened_at', 'replied_at']
        for field in datetime_fields:
            if field in data and data[field]:
                setattr(record, field, datetime.fromisoformat(data[field]))
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(record.to_dict(), "Outreach record updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update outreach record: {str(e)}", 500)

@app.route('/api/outreach/<int:record_id>', methods=['DELETE'])
def delete_outreach_record(record_id):
    """Delete outreach record"""
    try:
        from models import OutreachRecord
        record = OutreachRecord.query.get(record_id)
        
        if not record:
            return error_response("Outreach record not found", 404)
        
        db.session.delete(record)
        db.session.commit()
        
        return success_response(None, "Outreach record deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete outreach record: {str(e)}", 500)

# Dashboard stats API
@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        from models import Campaign, Creator, OutreachRecord, CopyVariant, EmailTemplate
        client_id = request.args.get('client_id', type=int)
        
        campaigns_query = Campaign.query
        creators_query = Creator.query.filter_by(is_active=True)
        outreach_query = OutreachRecord.query
        copy_variants_query = CopyVariant.query
        templates_query = EmailTemplate.query.filter_by(is_active=True)
        
        if client_id:
            campaigns_query = campaigns_query.filter_by(client_id=client_id)
            outreach_query = outreach_query.join(Campaign).filter(Campaign.client_id == client_id)
            copy_variants_query = copy_variants_query.join(Campaign).filter(Campaign.client_id == client_id)
            templates_query = templates_query.filter_by(client_id=client_id)
        
        stats = {
            'campaigns': {
                'total': campaigns_query.count(),
                'active': campaigns_query.filter_by(status='active').count(),
                'completed': campaigns_query.filter_by(status='completed').count(),
                'draft': campaigns_query.filter_by(status='draft').count(),
                'paused': campaigns_query.filter_by(status='paused').count()
            },
            'creators': {
                'total': creators_query.count(),
                'instagram': creators_query.filter_by(platform='instagram').count(),
                'youtube': creators_query.filter_by(platform='youtube').count(),
                'blog': creators_query.filter_by(platform='blog').count(),
                'tiktok': creators_query.filter_by(platform='tiktok').count()
            },
            'outreach': {
                'total': outreach_query.count(),
                'sent': outreach_query.filter_by(status='sent').count(),
                'replied': outreach_query.filter_by(status='replied').count(),
                'pending': outreach_query.filter_by(status='pending').count(),
                'failed': outreach_query.filter_by(status='failed').count(),
                'opened': outreach_query.filter(OutreachRecord.opened_at.isnot(None)).count()
            },
            'copy_variants': {
                'total': copy_variants_query.count(),
                'selected': copy_variants_query.filter_by(is_selected=True).count(),
                'ai_generated': copy_variants_query.filter_by(ai_generated=True).count()
            },
            'templates': {
                'total': templates_query.count(),
                'default': templates_query.filter_by(is_default=True).count()
            }
        }
        
        return success_response(stats, "Dashboard statistics retrieved successfully")
    except Exception as e:
        return error_response(f"Failed to retrieve dashboard statistics: {str(e)}", 500)

# ============================================================================
# UTILITY API ENDPOINTS
# ============================================================================

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get available platforms for creators"""
    platforms = [
        {'value': 'instagram', 'label': 'Instagram'},
        {'value': 'youtube', 'label': 'YouTube'},
        {'value': 'blog', 'label': 'Blog'},
        {'value': 'tiktok', 'label': 'TikTok'}
    ]
    return success_response(platforms, "Platforms retrieved successfully")

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get available channels for copy variants"""
    channels = [
        {'value': 'naver_blog', 'label': '네이버 블로그'},
        {'value': 'instagram_feed', 'label': '인스타그램 피드'},
        {'value': 'youtube', 'label': '유튜브'},
        {'value': 'tiktok', 'label': '틱톡'}
    ]
    return success_response(channels, "Channels retrieved successfully")

@app.route('/api/campaign-statuses', methods=['GET'])
def get_campaign_statuses():
    """Get available campaign statuses"""
    statuses = [
        {'value': 'draft', 'label': '초안'},
        {'value': 'active', 'label': '진행중'},
        {'value': 'paused', 'label': '일시정지'},
        {'value': 'completed', 'label': '완료'}
    ]
    return success_response(statuses, "Campaign statuses retrieved successfully")

@app.route('/api/outreach-statuses', methods=['GET'])
def get_outreach_statuses():
    """Get available outreach statuses"""
    statuses = [
        {'value': 'pending', 'label': '대기중'},
        {'value': 'sent', 'label': '발송완료'},
        {'value': 'failed', 'label': '발송실패'},
        {'value': 'replied', 'label': '답장받음'},
        {'value': 'bounced', 'label': '반송됨'},
        {'value': 'opened', 'label': '열람됨'}
    ]
    return success_response(statuses, "Outreach statuses retrieved successfully")

# Models will be imported in functions to avoid circular imports

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)