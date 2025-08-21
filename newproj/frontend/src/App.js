import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const API_BASE_URL = 'http://127.0.0.1:5000';

// --- 아이콘 컴포넌트 ---
const DashboardIcon = () => <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>;
const ResetIcon = () => <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h5M20 20v-5h-5M4 4l16 16" /></svg>;
const Loader = () => <div className="w-8 h-8 border-2 border-gray-200 border-t-primary rounded-full animate-spin"></div>;
const GoogleIcon = () => <svg className="w-5 h-5 mr-3" viewBox="0 0 48 48"><path fill="#4285F4" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"></path><path fill="#34A853" d="m6.306 14.691 6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"></path><path fill="#FBBC05" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"></path><path fill="#EA4335" d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.574l.007-.007 6.19 5.238C43.021 36.258 48 30.455 48 24c0-1.341-.138-2.65-.389-3.917z"></path></svg>;

// --- 컴포넌트들 ---

const Login = () => {
  const handleLogin = () => { window.location.href = `${API_BASE_URL}/api/login`; };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-text-main">CodingFit</h1>
        <p className="text-text-light mt-4 text-lg">개발자를 위한 스마트 헬스케어 파트너</p>
        <button onClick={handleLogin} className="mt-8 bg-white text-text-main font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition flex items-center mx-auto">
          <GoogleIcon /> Google 계정으로 시작하기
        </button>
      </div>
    </div>
  );
};

const Onboarding = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const totalSteps = 7;
  const [userData, setUserData] = useState({
    symptoms: [], painLevel: 3, goal: '통증 완화', frequency: 3, environment: '데스크탑, 일반 의자', habits: [], workStart: '09:00', workEnd: '18:00',
  });

  const handleNext = () => setStep(step + 1);
  const handlePrev = () => setStep(step - 1);
  const handleSelectionChange = (key, value) => { setUserData(prev => ({ ...prev, [key]: value })); };
  const handleMultiSelectionChange = (key, value) => { setUserData(prev => ({ ...prev, [key]: prev[key].includes(value) ? prev[key].filter(i => i !== value) : [...prev[key], value] })); };

  const titles = ["가장 불편한 증상을 모두 선택해주세요.", "현재 통증의 강도는 어느 정도인가요?", "가장 큰 건강 목표는 무엇인가요?", "일주일에 몇 번 운동하고 싶으신가요?", "주로 어떤 환경에서 근무하시나요?", "해당하는 생활 습관을 모두 선택해주세요.", "쉬는 시간 알림을 위해 업무 시간을 설정해주세요."];

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-2xl">
        <div className="w-full bg-gray-200 rounded-full h-2 mb-8"><div className="bg-primary h-2 rounded-full transition-all duration-500" style={{ width: `${(step / totalSteps) * 100}%` }}></div></div>
        <h2 className="text-2xl font-bold mb-6 text-center text-text-main">{titles[step-1]}</h2>
        <div className="min-h-[250px]">
          {step === 1 && (<div className="grid grid-cols-1 md:grid-cols-2 gap-4">{['거북목', '라운드숄더', '허리 통증', '손목터널 증후군'].map(s => (<button key={s} onClick={() => handleMultiSelectionChange('symptoms', s)} className={`p-5 border-2 rounded-lg font-medium transition-all ${userData.symptoms.includes(s) ? 'border-primary bg-blue-50' : 'border-border-color'}`}>{s}</button>))}</div>)}
          {step === 2 && (<div className="flex flex-col items-center pt-4"><input type="range" min="1" max="5" value={userData.painLevel} onChange={e => handleSelectionChange('painLevel', e.target.value)} className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" /><div className="flex w-full justify-between mt-2 text-text-light"><span>안 아픔</span><span>보통</span><span>매우 아픔</span></div><p className="text-center mt-4 text-3xl font-semibold">{userData.painLevel}</p></div>)}
          {step === 3 && (<div className="grid grid-cols-1 md:grid-cols-2 gap-4">{['통증 완화', '자세 교정', '컨디션 관리', '습관 형성'].map(g => (<button key={g} onClick={() => handleSelectionChange('goal', g)} className={`p-5 border-2 rounded-lg font-medium transition-all ${userData.goal === g ? 'border-primary bg-blue-50' : 'border-border-color'}`}>{g}</button>))}</div>)}
          {step === 4 && (<div className="flex justify-around items-center pt-8">{[1,2,3,4,5].map(f => (<button key={f} onClick={() => handleSelectionChange('frequency', f)} className={`w-16 h-16 flex items-center justify-center text-xl font-semibold border-2 rounded-full transition-all ${userData.frequency === f ? 'border-primary bg-blue-50 text-primary' : 'border-border-color text-text-light'}`}>{f}일</button>))}</div>)}
          {step === 5 && (<div className="space-y-3">{['데스크탑, 일반 의자', '노트북, 일반 의자', '데스크탑/노트북, 인체공학 의자'].map(e => (<button key={e} onClick={() => handleSelectionChange('environment', e)} className={`w-full p-5 border-2 rounded-lg font-medium transition-all ${userData.environment === e ? 'border-primary bg-blue-50' : 'border-border-color'}`}>{e}</button>))}</div>)}
          {step === 6 && (<div className="grid grid-cols-1 md:grid-cols-2 gap-4">{['다리 꼬기', '턱 괴기', '모니터/스마트폰 오래 보기', '해당 없음'].map(h => (<button key={h} onClick={() => handleMultiSelectionChange('habits', h)} className={`p-5 border-2 rounded-lg font-medium transition-all ${userData.habits.includes(h) ? 'border-primary bg-blue-50' : 'border-border-color'}`}>{h}</button>))}</div>)}
          {step === 7 && (<div className="flex flex-col md:flex-row items-center justify-center gap-4"><div><label className="block text-sm font-medium text-text-light">업무 시작</label><input type="time" value={userData.workStart} onChange={e => handleSelectionChange('workStart', e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-border-color rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary" /></div><span className="text-gray-500 mt-6 md:mt-0">~</span><div><label className="block text-sm font-medium text-text-light">업무 종료</label><input type="time" value={userData.workEnd} onChange={e => handleSelectionChange('workEnd', e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-border-color rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary" /></div></div>)}
        </div>
        <div className="flex justify-between mt-10">
          <button onClick={handlePrev} disabled={step === 1} className="bg-gray-200 text-gray-700 py-2 px-6 rounded-lg font-semibold transition hover:bg-gray-300 disabled:opacity-50">이전</button>
          {step < totalSteps && <button onClick={handleNext} className="bg-primary text-white py-2 px-6 rounded-lg font-semibold transition hover:bg-blue-600">다음</button>}
          {step === totalSteps && <button onClick={() => onComplete(userData)} className="bg-secondary text-white py-2 px-6 rounded-lg font-semibold transition hover:bg-green-500">결과 보기</button>}
        </div>
      </div>
    </div>
  );
};

const Dashboard = ({ user, userData, onReset, onLogout }) => {
    const [routine, setRoutine] = useState([]);
    const [analysis, setAnalysis] = useState('');
    const [activityData, setActivityData] = useState([]);
    const [loading, setLoading] = useState({ routine: true, analysis: false, activity: true });
    const [selectedExercise, setSelectedExercise] = useState(null);

    const fetchAPI = async (endpoint, body) => {
        const options = { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), credentials: 'include' };
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!response.ok) throw new Error('Network response was not ok.');
            return await response.json();
        } catch (error) { console.error(`API call to ${endpoint} failed:`, error); return null; }
    };
    
    useEffect(() => {
        const fetchAllData = async () => {
            setLoading({ routine: true, analysis: false, activity: true });
            const activity = await fetchAPI('/api/activity');
            if(activity && !activity.error) setActivityData(activity);
            setLoading(prev => ({ ...prev, activity: false }));

            const routineResult = await fetchAPI('/api/routine', userData);
            if (routineResult && !routineResult.error) {
                const enrichedRoutine = await Promise.all(
                    routineResult.map(async (ex) => {
                        const videoData = await fetchAPI('/api/youtube', { query: ex.name });
                        return { ...ex, videoId: videoData?.videoId || 'dQw4w9WgXcQ' };
                    })
                );
                setRoutine(enrichedRoutine);
            } else { setRoutine([]); }
            setLoading(prev => ({ ...prev, routine: false }));
        };
        fetchAllData();
    }, [userData]);

    const handleAnalysis = async () => {
        setLoading(prev => ({ ...prev, analysis: true })); setAnalysis('');
        const payload = { ...userData, activity_data: activityData };
        const analysisResult = await fetchAPI('/api/analysis', payload);
        if (analysisResult && analysisResult.analysis) {
            const formatted = analysisResult.analysis.replace(/\*\s/g, '<li>').replace(/\n/g, '<br/>');
            setAnalysis(`<ul class="list-disc list-inside">${formatted}</ul>`);
        } else { setAnalysis('<p class="text-red-500">분석에 실패했습니다.</p>'); }
        setLoading(prev => ({ ...prev, analysis: false }));
    };

    const handleSchedule = async (exercise) => {
        const result = await fetchAPI('/api/schedule', exercise);
        if (result && result.status === 'success') {
            alert(`'${exercise.name}' 일정이 구글 캘린더에 추가되었습니다!`);
            window.open(result.link, '_blank');
        } else { alert('일정 추가에 실패했습니다.'); }
    };

    return (
      <div className="flex h-screen bg-background">
        <aside className="w-20 lg:w-64 bg-sidebar/80 backdrop-blur-xl border-r border-border-color flex-col p-4 hidden sm:flex">
            <div className="px-2 py-2 text-2xl font-bold text-primary">CF</div>
            <nav className="flex-1 mt-8 space-y-2">
                <a href="#" className="flex items-center justify-center lg:justify-start px-2 py-3 text-text-main bg-blue-100 text-primary rounded-lg font-semibold"><DashboardIcon /> <span className="ml-3 hidden lg:inline">대시보드</span></a>
                <a href="#" onClick={onReset} className="flex items-center justify-center lg:justify-start px-2 py-3 text-text-light rounded-lg hover:bg-gray-100 hover:text-text-main font-semibold"><ResetIcon /> <span className="ml-3 hidden lg:inline">진단 다시하기</span></a>
            </nav>
            <div className="p-2 border-t border-border-color">
                <img src={user.picture} alt="profile" className="w-10 h-10 rounded-full mx-auto lg:mx-0"/>
                <div className="hidden lg:block mt-2">
                    <p className="text-sm font-semibold text-text-main truncate">{user.name}</p>
                    <button onClick={onLogout} className="w-full text-left text-xs text-red-500 font-semibold hover:text-red-700">로그아웃</button>
                </div>
            </div>
        </aside>

        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
            <header className="mb-8">
                <h1 className="text-4xl font-bold text-text-main">안녕하세요, {user.given_name}님!</h1>
                <p className="text-text-light mt-1">오늘의 맞춤 건강 정보를 확인하세요.</p>
            </header>
            
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2 space-y-6">
                    <div className="card animate-fade-in-up">
                        <h3 className="text-xl font-bold mb-4 text-text-main">✨ AI 추천 운동</h3>
                        {loading.routine ? (
                            <div className="flex justify-center items-center p-4"><Loader /></div>
                        ) : (
                            <div className="space-y-3">
                                {routine.length > 0 ? (
                                    routine.map((ex, i) => (
                                        <div key={i} className="flex items-center justify-between p-4 bg-background rounded-lg">
                                            <div>
                                                <p className="font-semibold text-text-main">{ex.name}</p>
                                                <p className="text-sm text-text-light">{ex.duration}</p>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button onClick={() => setSelectedExercise(ex)} className="bg-primary text-white text-sm py-1.5 px-3 rounded-md font-semibold transition hover:bg-blue-600">영상</button>
                                                <button onClick={() => handleSchedule(ex)} className="bg-gray-200 text-text-main text-sm py-1.5 px-3 rounded-md font-semibold transition hover:bg-gray-300">예약</button>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p>추천 운동을 생성하지 못했습니다.</p>
                                )}
                            </div>
                        )}
                    </div>
                    <div className="card animate-fade-in-up" style={{animationDelay: '0.2s'}}>
                        <h3 className="text-xl font-bold mb-4 text-text-main">📅 주간 활동량 (걸음 수)</h3>
                        {loading.activity ? <Loader/> : <WeeklyChart activityData={activityData} />}
                    </div>
                </div>
                <div className="space-y-6">
                    <div className="card animate-fade-in-up" style={{animationDelay: '0.4s'}}>
                        <h3 className="text-xl font-bold mb-4 text-text-main">✨ AI 건강 상태 분석</h3>
                        {loading.analysis ? (<div className="flex justify-center items-center p-4"><Loader /></div>) : (<div className="text-sm text-text-main space-y-2 prose" dangerouslySetInnerHTML={{ __html: analysis || '<p className="text-text-light">버튼을 눌러 AI 분석을 받아보세요.</p>' }}></div>)}
                        <button onClick={handleAnalysis} disabled={loading.analysis} className="w-full mt-4 bg-secondary text-white py-2 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition hover:bg-green-500 disabled:opacity-50">분석하기</button>
                    </div>
                    <div className="card animate-fade-in-up" style={{animationDelay: '0.6s'}}>
                        <h3 className="text-xl font-bold mb-4 text-text-main">👤 내 정보 요약</h3>
                        <div className="space-y-2 text-sm text-text-main">
                            <p><strong>주요 목표:</strong> <span className="font-semibold text-secondary">{userData.goal}</span></p>
                            <p><strong>주요 증상:</strong> {userData.symptoms.join(', ') || '없음'}</p>
                            <p><strong>통증 강도:</strong> <span className="text-primary font-semibold">{userData.painLevel} / 5</span></p>
                            <p><strong>운동 빈도:</strong> 주 {userData.frequency}회</p>
                        </div>
                    </div>
                </div>
            </div>
            {selectedExercise && <VideoModal exercise={selectedExercise} onClose={() => setSelectedExercise(null)} />}
        </main>
      </div>
    );
};

const WeeklyChart = ({ activityData }) => {
    const chartRef = useRef(null);
    useEffect(() => {
        if (!chartRef.current) return;
        const labels = Array.from({ length: 7 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() - i); return d.toLocaleDateString('ko-KR', { weekday: 'short' }); }).reverse();
        const data = Array(7).fill(0);
        if(activityData && activityData.length > 0) {
            const startIdx = Math.max(0, 7 - activityData.length);
            activityData.slice(-7).forEach((steps, i) => { data[startIdx + i] = steps; });
        }
        const chartInstance = new Chart(chartRef.current, { type: 'bar', data: { labels, datasets: [{ label: '걸음 수', data, backgroundColor: '#3B82F6', borderWidth: 0, borderRadius: 6, barPercentage: 0.5, }] }, options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { padding: 10 } }, x: { grid: { display: false } } }, plugins: { legend: { display: false }, tooltip: { enabled: true, mode: 'index', intersect: false, backgroundColor: '#1C1C1E', titleColor: '#fff', bodyColor: '#fff', cornerRadius: 4, displayColors: false } } } });
        return () => chartInstance.destroy();
    }, [activityData]);
    return <div className="h-48"><canvas ref={chartRef}></canvas></div>;
};

const VideoModal = ({ exercise, onClose }) => {
    return (<div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={onClose}><div className="bg-white rounded-lg shadow-xl w-full max-w-2xl" onClick={e => e.stopPropagation()}><div className="p-6"><div className="flex justify-between items-start"><h3 className="text-xl font-bold text-text-main">{exercise.name}</h3><button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-3xl">&times;</button></div><div className="mt-4 aspect-w-16 aspect-h-9"><iframe className="w-full h-full rounded-md" src={`https://www.youtube.com/embed/${exercise.videoId}`} title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe></div><p className="mt-4 text-text-light">{exercise.description}</p></div></div></div>);
};

function App() {
  const [user, setUser] = useState(null);
  const [diagnosisData, setDiagnosisData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchOptions = { credentials: 'include' };

  useEffect(() => {
    const checkLoginStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/check_login`, fetchOptions);
            if (response.ok) {
                const data = await response.json();
                if(data.logged_in) {
                    setUser(data.user);
                    if(data.saved_diagnosis) {
                        setDiagnosisData(data.saved_diagnosis);
                    }
                }
            }
        } catch (error) {
            console.error("Login check failed:", error);
        }
        setIsLoading(false);
    };
    checkLoginStatus();
  }, []);

  const handleOnboardingComplete = async (data) => {
    setDiagnosisData(data);
    await fetch(`${API_BASE_URL}/api/save_diagnosis`, {
        ...fetchOptions,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
  };

  const handleReset = async () => {
    setDiagnosisData(null);
    await fetch(`${API_BASE_URL}/api/delete_diagnosis`, {
        ...fetchOptions,
        method: 'POST',
    });
  };
  
  const handleLogout = async () => {
    await fetch(`${API_BASE_URL}/api/logout`, fetchOptions);
    setUser(null);
    setDiagnosisData(null);
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader /></div>;
  }

  if (!user) {
    return <Login />;
  }

  if (!diagnosisData) {
    return <Onboarding onComplete={handleOnboardingComplete} />;
  }

  return <Dashboard user={user} userData={diagnosisData} onReset={handleReset} onLogout={handleLogout} />;
}

export default App;