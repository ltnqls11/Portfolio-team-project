import { useState, FC, ChangeEvent, FormEvent } from 'react';

// Define the type for a single video object received from the YouTube API
interface Video {
  id: string;
  title: string;
  thumbnail: string;
  channel: string;
  difficulty?: string;
  durationMinutes?: number;
  equipment?: string[];
}

// ====================================================================
// The Main App Component
// ====================================================================
const App: FC = () => {
  const [symptom, setSymptom] = useState<string>('');
  const [painSide, setPainSide] = useState<string>('');
  const [painLevel, setPainLevel] = useState<string>('');
  const [workHours, setWorkHours] = useState<string>('');
  const [postureHabit, setPostureHabit] = useState<string>('');
  const [restFrequency, setRestFrequency] = useState<string>('');
  const [exerciseIntensity, setExerciseIntensity] = useState<string>('');
  const [exerciseDuration, setExerciseDuration] = useState<string>('');
  const [painOccurrence, setPainOccurrence] = useState<string>('');
  const [painNature, setPainNature] = useState<string>('');
  const [environment, setEnvironment] = useState<string>('');
  const [habit, setHabit] = useState<string>('');
  const [age, setAge] = useState<string>('');
  
  const [healthReport, setHealthReport] = useState<string>('');
  const [symptomInfo, setSymptomInfo] = useState<string>('');
  const [recommendedVideos, setRecommendedVideos] = useState<Video[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // API keys - Make sure to replace these with your actual keys
  const GEMINI_API_KEY: string = "YOUR_GEMINI_API_KEY";
  const YOUTUBE_API_KEY: string = "YOUR_YOUTUBE_API_KEY";

  /**
   * Fetches health report, symptom info, and recommended videos simultaneously.
   */
  const fetchAllRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    setRecommendedVideos(null);
    setHealthReport('');
    setSymptomInfo('');

    if (!symptom || !painLevel) {
      setError('증상과 통증 단계를 선택해주세요.');
      setIsLoading(false);
      return;
    }

    try {
      await Promise.all([
        fetchRecommendedVideoWithAIAnalysis(),
        generateHealthReport(),
        fetchSymptomInfo()
      ]);
    } catch (err: any) {
      console.error(err);
      setError('정보를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Fetches a search query from Gemini, then fetches videos from YouTube,
   * and finally analyzes each video's metadata with Gemini to get more details.
   */
  const fetchRecommendedVideoWithAIAnalysis = async () => {
    try {
      // Step 1: Generate a search query with Gemini
      const userPrompt: string = `
        다음 사용자 정보에 맞는 유튜브 운동 영상 검색어를 50자 이내의 한글로 만들어줘. '유튜브'라는 단어는 포함하지 마.
        예시: '거북목 스트레칭'
        
        사용자 정보:
        - 증상: ${symptom}
        - 통증 단계: ${painLevel}
        - 손목터널 증후군인 경우 통증 부위: ${painSide}
        - 하루 업무 시간: ${workHours}
        - 자세 습관: ${postureHabit}
        - 휴식 빈도: ${restFrequency}
        - 운동 선호 강도: ${exerciseIntensity}
        - 운동 선호 시간: ${exerciseDuration}
        - 통증 발생 시점: ${painOccurrence}
        - 통증의 성질: ${painNature}
        - 주요 업무 환경: ${environment}
        - 주요 습관: ${habit}
        - 연령: ${age}
      `;

      const geminiSearchQueryPayload = {
        contents: [{ parts: [{ text: userPrompt }] }],
      };
      const geminiSearchUrl: string = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${GEMINI_API_KEY}`;
      const geminiSearchResponse = await fetch(geminiSearchUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geminiSearchQueryPayload),
      });

      if (!geminiSearchResponse.ok) {
        throw new Error('Gemini API (검색어 생성) 호출에 실패했습니다.');
      }

      const geminiSearchQueryResult = await geminiSearchResponse.json();
      const searchQuery: string = geminiSearchQueryResult.candidates?.[0]?.content?.parts?.[0]?.text || '';

      if (!searchQuery) {
        throw new Error('AI가 검색어를 생성하지 못했습니다.');
      }

      // Step 2: Fetch videos from YouTube
      const youtubeUrl: string = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&q=${encodeURIComponent(searchQuery)}&part=snippet&type=video&maxResults=3`;
      const youtubeResponse = await fetch(youtubeUrl);

      if (!youtubeResponse.ok) {
        throw new Error('YouTube API 호출에 실패했습니다. API 키가 유효한지 확인해주세요.');
      }

      const youtubeResult = await youtubeResponse.json();
      const rawVideos = youtubeResult.items;

      // Step 3: Analyze each video with Gemini for detailed info
      const analyzedVideos = await Promise.all(
        rawVideos.map(async (item: any): Promise<Video> => {
          const videoTitle = item.snippet.title;
          const videoDescription = item.snippet.description;

          const analysisPrompt = `
            다음 유튜브 영상의 제목과 설명을 분석하여 난이도, 소요 시간(분), 필요한 장비 정보를 JSON 형식으로 제공해줘.
            난이도는 '초급', '중급', '고급' 중 하나로 분류하고, 소요 시간은 숫자(분)로, 장비는 배열로 나타내줘. 장비가 필요 없으면 '없음'으로 표시해줘.
            JSON 예시: {"difficulty": "초급", "duration_minutes": 10, "equipment": ["매트", "덤벨"]}

            ---
            제목: ${videoTitle}
            설명: ${videoDescription}
          `;

          const geminiAnalysisPayload = {
            contents: [{ parts: [{ text: analysisPrompt }] }],
            generationConfig: {
              responseMimeType: "application/json",
            },
          };

          const geminiAnalysisUrl: string = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${GEMINI_API_KEY}`;
          
          try {
            const analysisResponse = await fetch(geminiAnalysisUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(geminiAnalysisPayload),
            });
            const analysisResult = await analysisResponse.json();
            const analysisText = analysisResult.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
            const analysisData = JSON.parse(analysisText);

            return {
              id: item.id.videoId,
              title: videoTitle,
              thumbnail: item.snippet.thumbnails.high.url,
              channel: item.snippet.channelTitle,
              difficulty: analysisData.difficulty,
              durationMinutes: analysisData.duration_minutes,
              equipment: analysisData.equipment,
            };
          } catch (err) {
            console.error(`Video analysis failed for ${videoTitle}:`, err);
            return {
              id: item.id.videoId,
              title: videoTitle,
              thumbnail: item.snippet.thumbnails.high.url,
              channel: item.snippet.channelTitle,
              difficulty: '분석 불가',
              durationMinutes: null,
              equipment: ['분석 불가'],
            };
          }
        })
      );
      
      setRecommendedVideos(analyzedVideos.length > 0 ? analyzedVideos : []);
    } catch (err: any) {
      console.error(err);
      setRecommendedVideos([]);
    }
  };

  const generateHealthReport = async () => {
    try {
      const reportPrompt: string = `
        다음 사용자 정보와 증상에 대한 상세 건강 리포트를 300자 이내로 작성해줘.
        - 증상: ${symptom}
        - 통증 단계: ${painLevel}
        - 하루 업무 시간: ${workHours}
        - 자세 습관: ${postureHabit}
        - 휴식 빈도: ${restFrequency}
        - 통증 발생 시점: ${painOccurrence}
        - 통증의 성질: ${painNature}
        - 주요 업무 환경: ${environment}
        - 주요 습관: ${habit}
        - 연령: ${age}
        
        전문적이면서도 이해하기 쉽게 작성하고, 현재 상태에 대한 분석과 함께 간단한 조언을 포함해줘.
      `;
      
      const geminiPayload = {
        contents: [{ parts: [{ text: reportPrompt }] }],
      };
      const geminiUrl: string = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${GEMINI_API_KEY}`;
      const geminiResponse = await fetch(geminiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geminiPayload),
      });
      const geminiResult = await geminiResponse.json();
      const reportText: string = geminiResult.candidates?.[0]?.content?.parts?.[0]?.text || '';
      setHealthReport(reportText);
    } catch (err: any) {
      console.error(err);
      setHealthReport('건강 리포트를 생성하는 중 오류가 발생했습니다.');
    }
  };

  const fetchSymptomInfo = async () => {
    try {
      const infoPrompt: string = `
        '${symptom}'에 대한 상세 정보를 300자 이내로 작성해줘.
        - 정의:
        - 주요 원인:
        - 예방법:
        
        위의 3가지 항목을 포함하여 전문적이고 이해하기 쉽게 작성해줘.
      `;
      
      const geminiPayload = {
        contents: [{ parts: [{ text: infoPrompt }] }],
      };
      const geminiUrl: string = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${GEMINI_API_KEY}`;
      const geminiResponse = await fetch(geminiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geminiPayload),
      });
      const geminiResult = await geminiResponse.json();
      const infoText: string = geminiResult.candidates?.[0]?.content?.parts?.[0]?.text || '';
      setSymptomInfo(infoText);
    } catch (err: any) {
      console.error(err);
      setSymptomInfo('증상 정보를 불러오는 중 오류가 발생했습니다.');
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>, setter: (value: string) => void) => {
    setter(e.target.value);
    setRecommendedVideos(null);
    setHealthReport('');
    setSymptomInfo('');
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center font-sans">
      <div className="max-w-4xl w-full bg-white rounded-xl shadow-lg p-8 space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-800">개발자 헬스케어 대시보드</h1>
          <p className="mt-2 text-gray-500">사용자 정보를 입력하고 맞춤형 운동을 추천받으세요.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">1. 증상 선택</h3>
            <div className="space-y-2">
              {['거북목', '라운드숄더', '허리 디스크', '손목터널 증후군'].map((s, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="symptom"
                    value={s}
                    checked={symptom === s}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => {
                      setSymptom(e.target.value);
                      setPainSide('');
                      setRecommendedVideos(null);
                    }}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{s}</span>
                </label>
              ))}
            </div>
          </div>

          {symptom === '손목터널 증후군' && (
            <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">2. 통증 부위 (손목)</h3>
              <div className="space-y-2">
                {['왼쪽', '오른쪽', '양쪽'].map((side, index) => (
                  <label key={index} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name="painSide"
                      value={side}
                      checked={painSide === side}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setPainSide)}
                      className="form-radio text-indigo-600 h-4 w-4"
                    />
                    <span>{side}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">3. 통증 단계</h3>
            <div className="space-y-2">
              {['경미', '보통', '심함'].map((level, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="painLevel"
                    value={level}
                    checked={painLevel === level}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setPainLevel)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{level}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">4. 업무 환경</h3>
            <div className="space-y-2">
              {['집 (데스크탑)', '사무실 (데스크탑)', '카페 (노트북)'].map((env, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="environment"
                    value={env}
                    checked={environment === env}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setEnvironment)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{env}</span>
                  </label>
                ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">5. 주요 습관</h3>
            <div className="space-y-2">
              {['스트레칭을 거의 하지 않음', '틈틈이 스트레칭을 함', '자세 교정에 신경 쓰는 편'].map((h, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="habit"
                    value={h}
                    checked={habit === h}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setHabit)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{h}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">6. 연령</h3>
            <input
              type="number"
              value={age}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setAge)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="숫자만 입력"
            />
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">7. 하루 업무 시간</h3>
            <div className="space-y-2">
              {['~4시간', '5~8시간', '9시간 이상'].map((hours, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="workHours"
                    value={hours}
                    checked={workHours === hours}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setWorkHours)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{hours}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">8. 자세 습관</h3>
            <div className="space-y-2">
              {['등을 등받이에 붙이고 바르게 앉음', '앞으로 숙이거나 비스듬히 앉음', '다리를 꼬고 앉음'].map((posture, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="postureHabit"
                    value={posture}
                    checked={postureHabit === posture}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setPostureHabit)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{posture}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">9. 휴식 빈도</h3>
            <div className="space-y-2">
              {['1시간에 한 번 5분 이상', '2~3시간에 한 번', '거의 쉬지 않음'].map((frequency, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="restFrequency"
                    value={frequency}
                    checked={restFrequency === frequency}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setRestFrequency)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{frequency}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">10. 운동 강도</h3>
            <div className="space-y-2">
              {['가볍고 짧은 스트레칭', '유산소와 병행하는 조금 힘든 운동', '고강도 근력 운동'].map((intensity, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="exerciseIntensity"
                    value={intensity}
                    checked={exerciseIntensity === intensity}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setExerciseIntensity)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{intensity}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">11. 운동 시간</h3>
            <div className="space-y-2">
              {['5분 이내', '10분 이내', '20분 이내'].map((duration, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="exerciseDuration"
                    value={duration}
                    checked={exerciseDuration === duration}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setExerciseDuration)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{duration}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">12. 통증 발생 시점</h3>
            <div className="space-y-2">
              {['업무 중', '업무 후', '일상생활 내내'].map((occurrence, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="painOccurrence"
                    value={occurrence}
                    checked={painOccurrence === occurrence}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setPainOccurrence)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{occurrence}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="bg-gray-50 p-6 rounded-lg shadow-inner">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">13. 통증의 성질</h3>
            <div className="space-y-2">
              {['찌르는 듯한 통증', '결리거나 뻐근한 통증', '저릿저릿한 통증'].map((nature, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="painNature"
                    value={nature}
                    checked={painNature === nature}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleInputChange(e, setPainNature)}
                    className="form-radio text-indigo-600 h-4 w-4"
                  />
                  <span>{nature}</span>
                </label>
              ))}
            </div>
          </div>

        </div>

        {/* Recommendation Button */}
        <div className="text-center pt-4">
          <button
            onClick={fetchAllRecommendations}
            disabled={isLoading || !symptom || !painLevel}
            className={`w-full md:w-auto px-8 py-3 font-bold rounded-full shadow-lg transition-all duration-300 transform focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50
              ${isLoading || !symptom || !painLevel ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:scale-105'}`}
          >
            {isLoading ? '정보 분석 중...' : '운동 추천받기'}
          </button>
        </div>

        {/* Report Sections (New grouping) */}
        {(healthReport || symptomInfo || recommendedVideos) && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-6">나의 건강 리포트</h2>
            <div className="space-y-6">
              {healthReport && (
                <div className="p-6 bg-blue-50 border-l-4 border-blue-500 rounded-lg shadow-md">
                  <h3 className="text-lg font-bold text-blue-800 mb-2">개인 맞춤형 건강 리포트 📝</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{healthReport}</p>
                </div>
              )}
              {symptomInfo && (
                <div className="p-6 bg-green-50 border-l-4 border-green-500 rounded-lg shadow-md">
                  <h3 className="text-lg font-bold text-green-800 mb-2">증상별 상세 정보 📚</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{symptomInfo}</p>
                </div>
              )}
              {recommendedVideos && (
                <div className="mt-8">
                  <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">맞춤형 운동 추천! 💪</h3>
                  {recommendedVideos.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {recommendedVideos.map(video => (
                        <a
                          key={video.id}
                          href={`https://www.youtube.com/watch?v=${video.id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 block"
                        >
                          <img
                            src={video.thumbnail}
                            alt={video.title}
                            className="w-full h-auto rounded-t-lg object-cover"
                          />
                          <div className="p-4">
                            <h4 className="font-semibold text-gray-800 text-sm md:text-base line-clamp-2">
                              {video.title}
                            </h4>
                            {/* Display AI-analyzed details */}
                            <div className="mt-2 text-gray-600 text-xs">
                              <p>난이도: <span className="font-bold">{video.difficulty || '분석 중...'}</span></p>
                              <p>소요 시간: <span className="font-bold">{video.durationMinutes ? `${video.durationMinutes}분` : '분석 중...'}</span></p>
                              <p>장비: <span className="font-bold">{video.equipment && video.equipment.join(', ') || '분석 중...'}</span></p>
                            </div>
                            <p className="text-gray-500 text-xs mt-1">
                              채널: {video.channel}
                            </p>
                          </div>
                        </a>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-8">
                      추천할 영상을 찾지 못했습니다. 다른 조합을 시도해 보세요.
                    </div>
                  )}
                  <p className="mt-4 text-sm text-gray-500 text-center">
                    *링크를 클릭하면 새 탭에서 유튜브 영상이 열립니다.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
