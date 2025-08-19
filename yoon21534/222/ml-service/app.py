from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.content_analyzer import ContentAnalyzer
from services.influencer_scorer import InfluencerScorer
from services.recommendation_engine import RecommendationEngine

load_dotenv()

app = Flask(__name__)
CORS(app)

# 서비스 인스턴스 초기화
content_analyzer = ContentAnalyzer()
influencer_scorer = InfluencerScorer()
recommendation_engine = RecommendationEngine()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Blog RPA ML Service',
        'version': '1.0.0'
    })

@app.route('/analyze/content', methods=['POST'])
def analyze_content():
    """블로그 콘텐츠 분석"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        analysis = content_analyzer.analyze(content)
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/score/influencer', methods=['POST'])
def score_influencer():
    """인플루언서 점수 계산"""
    try:
        data = request.get_json()
        influencer_data = data.get('influencer_data', {})
        
        if not influencer_data:
            return jsonify({'error': 'Influencer data is required'}), 400
        
        score = influencer_scorer.calculate_score(influencer_data)
        return jsonify({'score': score})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommend/influencers', methods=['POST'])
def recommend_influencers():
    """인플루언서 추천"""
    try:
        data = request.get_json()
        criteria = data.get('criteria', {})
        limit = data.get('limit', 10)
        
        recommendations = recommendation_engine.get_recommendations(criteria, limit)
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/categorize/content', methods=['POST'])
def categorize_content():
    """콘텐츠 자동 카테고리 분류"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        categories = content_analyzer.categorize(content)
        return jsonify({'categories': categories})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting ML Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)