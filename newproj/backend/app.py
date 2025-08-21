import os
import json
import requests
from flask import Flask, request, jsonify, redirect, session, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# --- 중요: 세션 쿠키 설정을 추가하여 로그인 반복 오류를 해결합니다. ---
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# --- Google API 설정 ---
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
CLIENT_SECRETS_FILE = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://127.0.0.1:5000/api/callback"],
    }
}
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email', 
    'https://www.googleapis.com/auth/userinfo.profile', 
    'https://www.googleapis.com/auth/calendar.events', 
    'https://www.googleapis.com/auth/fitness.activity.read'
]

# --- Gemini & YouTube API 설정 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"

# --- 데이터베이스 대신 사용할 간단한 JSON 파일 ---
DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def credentials_to_dict(credentials):
    return {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri, 'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scopes': credentials.scopes}

def get_user_id(creds):
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info.get('id')

# --- Google 인증 라우트 ---
@app.route('/api/login')
def login():
    session.pop('credentials', None)
    session.pop('state', None)
    
    flow = Flow.from_client_config(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline', 
        include_granted_scopes='true',
        prompt='consent'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/api/callback')
def callback():
    state = session['state']
    flow = Flow.from_client_config(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('callback', _external=True)
    
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        session['credentials'] = credentials_to_dict(credentials)
        return redirect('http://localhost:3000/')
    except Exception as e:
        print(f"An error occurred during token fetch: {e}")
        return redirect('http://localhost:3000/')


# ... (이하 나머지 코드는 이전과 동일) ...

@app.route('/api/logout')
def logout():
    session.pop('credentials', None)
    return jsonify({'status': 'logged_out'})

@app.route('/api/check_login')
def check_login():
    if 'credentials' not in session:
        return jsonify({'logged_in': False})
    
    creds = Credentials(**session['credentials'])
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(requests.Request())
            session['credentials'] = credentials_to_dict(creds)
        except Exception as e:
            session.pop('credentials', None)
            return jsonify({'logged_in': False})

    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    
    db = load_db()
    user_id = user_info.get('id')
    saved_diagnosis = db.get(user_id)

    return jsonify({'logged_in': True, 'user': user_info, 'saved_diagnosis': saved_diagnosis})

@app.route('/api/save_diagnosis', methods=['POST'])
def save_diagnosis():
    if 'credentials' not in session: return jsonify({'error': 'Unauthorized'}), 401
    creds = Credentials(**session['credentials'])
    user_id = get_user_id(creds)
    if not user_id: return jsonify({'error': 'Could not get user ID'}), 500
    
    db = load_db()
    db[user_id] = request.json
    save_db(db)
    return jsonify({'status': 'success', 'data': request.json})

@app.route('/api/delete_diagnosis', methods=['POST'])
def delete_diagnosis():
    if 'credentials' not in session: return jsonify({'error': 'Unauthorized'}), 401
    creds = Credentials(**session['credentials'])
    user_id = get_user_id(creds)
    if not user_id: return jsonify({'error': 'Could not get user ID'}), 500

    db = load_db()
    if user_id in db:
        del db[user_id]
        save_db(db)
    return jsonify({'status': 'success'})

@app.route('/api/activity')
def get_activity():
    if 'credentials' not in session: return jsonify({'error': 'Unauthorized'}), 401
    creds = Credentials(**session['credentials'])
    service = build('fitness', 'v1', credentials=creds)
    today = datetime.utcnow().date()
    start_time = int(datetime.combine(today - timedelta(days=6), datetime.min.time()).timestamp() * 1000)
    end_time = int(datetime.combine(today, datetime.max.time()).timestamp() * 1000)
    try:
        response = service.users().dataset().aggregate(userId='me', body={"aggregateBy": [{"dataTypeName": "com.google.step_count.delta","dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"}],"bucketByTime": {"durationMillis": 86400000},"startTimeMillis": start_time,"endTimeMillis": end_time}).execute()
        steps_data = [d['dataset'][0]['point'][0]['value'][0]['intVal'] if d['dataset'][0]['point'] else 0 for d in response['bucket']]
        return jsonify(steps_data)
    except Exception as e:
        print(f"Error fetching Google Fit data: {e}")
        return jsonify([])

@app.route('/api/schedule', methods=['POST'])
def schedule_event():
    if 'credentials' not in session: return jsonify({'error': 'Unauthorized'}), 401
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)
    event_data = request.json
    start_time = datetime.now() + timedelta(minutes=10)
    end_time = start_time + timedelta(minutes=15)
    event = {'summary': f"[코딩핏] {event_data.get('name', '스트레칭 시간')}",'description': event_data.get('description', 'AI가 추천한 맞춤 운동 시간입니다.'),'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Seoul'},'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Seoul'},}
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify({'status': 'success', 'link': created_event.get('htmlLink')})

def call_gemini_internal(prompt, is_json=False):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if is_json: payload["generationConfig"] = {"responseMimeType": "application/json"}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if result.get("candidates"): return result["candidates"][0]["content"]["parts"][0]["text"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None

@app.route('/api/routine', methods=['POST'])
def get_ai_routine():
    user_data = request.json
    prompt = f"""Based on the user profile, create a personalized exercise routine. - Goal: {user_data.get('goal', 'Pain Relief')} - Symptoms: {', '.join(user_data.get('symptoms', [])) or 'None'} - Pain Level: {user_data.get('painLevel', 3)}/5 - Frequency: {user_data.get('frequency', 3)} times a week. Provide a JSON array of 3 exercises. Each object must have "name", "duration", and "description" keys in Korean."""
    routine_text = call_gemini_internal(prompt, is_json=True)
    if routine_text:
        try: return jsonify(json.loads(routine_text))
        except json.JSONDecodeError: return jsonify({"error": "Invalid JSON from AI"}), 500
    return jsonify({"error": "Failed to generate routine"}), 500

@app.route('/api/analysis', methods=['POST'])
def get_ai_analysis():
    user_data = request.json
    activity_data = user_data.get('activity_data', [])
    activity_prompt = ""
    if activity_data:
        avg_steps = sum(activity_data) / len(activity_data) if activity_data else 0
        activity_prompt = f"- Recent Activity: User's average step count over the last few days is {avg_steps:.0f} steps."
    prompt = f"""You are a friendly health coach. A user has provided the following info: - Goal: {user_data.get('goal', 'Pain Relief')} - Symptoms: {', '.join(user_data.get('symptoms', [])) or 'None'} - Pain Level: {user_data.get('painLevel', 3)}/5 {activity_prompt}. Based on this, provide a concise, actionable analysis in Korean. Use Markdown for formatting. Keep the tone positive."""
    analysis_text = call_gemini_internal(prompt)
    if analysis_text: return jsonify({"analysis": analysis_text})
    return jsonify({"error": "Failed to generate analysis"}), 500

@app.route('/api/youtube', methods=['POST'])
def search_youtube():
    query = request.json.get('query')
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query} 스트레칭&key={YOUTUBE_API_KEY}&maxResults=1&type=video"
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        results = response.json()
        if results.get("items"): return jsonify({"videoId": results["items"][0]["id"]["videoId"]})
        else: return jsonify({"videoId": "dQw4w9WgXcQ"})
    except requests.exceptions.RequestException: return jsonify({"error": "Failed to fetch video"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)