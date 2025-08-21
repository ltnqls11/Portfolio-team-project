import React, { useState, useEffect } from 'react';
import { UserInfo, ExerciseRoutine, YouTubeVideo } from '../types';
import { exerciseRoutines, workEnvironmentExercises } from '../data/exercises';
import { searchExerciseVideos, getMockExerciseVideos, analyzeComments } from '../services/youtubeService';
import { requestNotificationPermission, startBreakNotifications, startExerciseReminders } from '../services/notificationService';
import './ExerciseRecommendation.css';

interface ExerciseRecommendationProps {
  userInfo: UserInfo;
  onBack: () => void;
}

const ExerciseRecommendation: React.FC<ExerciseRecommendationProps> = ({ userInfo, onBack }) => {
  const [recommendedRoutines, setRecommendedRoutines] = useState<ExerciseRoutine[]>([]);
  const [youtubeVideos, setYoutubeVideos] = useState<YouTubeVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  useEffect(() => {
    generateRecommendations();
    setupNotifications();
  }, []);

  const generateRecommendations = async () => {
    setLoading(true);
    
    // 증상별 운동 루틴 추천
    const routines: ExerciseRoutine[] = [];
    userInfo.symptoms.forEach(symptom => {
      const symptomRoutines = exerciseRoutines[symptom] || [];
      routines.push(...symptomRoutines);
    });

    // 작업 환경별 추가 운동
    const workEnvExercises = workEnvironmentExercises[userInfo.workEnvironment] || [];
    if (workEnvExercises.length > 0) {
      routines.push({
        id: 'work_env_routine',
        name: `${getWorkEnvironmentLabel(userInfo.workEnvironment)} 맞춤 루틴`,
        exercises: workEnvExercises,
        totalDuration: workEnvExercises.reduce((sum, ex) => sum + ex.duration, 0),
        frequency: '근무 중 2-3회',
        description: '작업 환경에 맞춘 간단한 스트레칭 루틴입니다.'
      });
    }

    setRecommendedRoutines(routines);

    // YouTube 비디오 검색
    try {
      const videos = await searchExerciseVideos(userInfo.symptoms);
      setYoutubeVideos(videos.length > 0 ? videos : getMockExerciseVideos());
    } catch (error) {
      console.error('YouTube 비디오 검색 실패:', error);
      setYoutubeVideos(getMockExerciseVideos());
    }

    setLoading(false);
  };

  const setupNotifications = async () => {
    const permissionGranted = await requestNotificationPermission();
    setNotificationsEnabled(permissionGranted);
    
    if (permissionGranted) {
      // 휴식 알림 시작
      startBreakNotifications(60); // 60분마다
      
      // 운동 알림 시작
      startExerciseReminders();
    }
  };

  const getWorkEnvironmentLabel = (env: string): string => {
    const labels: Record<string, string> = {
      office_desk: '사무실',
      standing_work: '서서하는 작업',
      manual_labor: '육체 노동',
      driving: '운전',
      home_office: '재택 근무'
    };
    return labels[env] || env;
  };

  const getSymptomLabels = (symptoms: string[]): string => {
    const labels: Record<string, string> = {
      turtle_neck: '거북목',
      rounded_shoulders: '둥근 어깨',
      disc_herniation: '디스크 탈출증',
      carpal_tunnel_syndrome: '손목 터널 증후군'
    };
    return symptoms.map(s => labels[s] || s).join(', ');
  };

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'beginner': return '#4CAF50';
      case 'intermediate': return '#FF9800';
      case 'advanced': return '#F44336';
      default: return '#666';
    }
  };

  if (loading) {
    return (
      <div className="exercise-recommendation">
        <div className="loading">
          <div className="spinner"></div>
          <p>맞춤 운동을 분석하고 있습니다...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="exercise-recommendation">
      <div className="header">
        <button onClick={onBack} className="back-btn">
          ← 뒤로 가기
        </button>
        <h1>맞춤 운동 추천</h1>
      </div>

      {/* 사용자 정보 요약 */}
      <div className="user-summary">
        <h2>사용자 정보</h2>
        <div className="summary-grid">
          <div className="summary-item">
            <strong>증상:</strong> {getSymptomLabels(userInfo.symptoms)}
          </div>
          <div className="summary-item">
            <strong>통증 심각도:</strong> {userInfo.painSeverity}점
          </div>
          <div className="summary-item">
            <strong>작업 환경:</strong> {getWorkEnvironmentLabel(userInfo.workEnvironment)}
          </div>
          <div className="summary-item">
            <strong>운동 모드:</strong> {userInfo.mode === 'prevention' ? '예방' : userInfo.mode === 'exercise' ? '운동' : '재활'}
          </div>
        </div>
      </div>

      {/* 알림 설정 */}
      <div className="notification-section">
        <h2>알림 설정</h2>
        <div className="notification-status">
          <span className={`status ${notificationsEnabled ? 'enabled' : 'disabled'}`}>
            {notificationsEnabled ? '✓ 알림 활성화됨' : '✗ 알림 비활성화됨'}
          </span>
          {notificationsEnabled && (
            <p className="notification-info">
              • 60분마다 휴식 알림<br/>
              • 매일 오전 9시, 오후 6시 운동 알림
            </p>
          )}
        </div>
      </div>

      {/* 추천 운동 루틴 */}
      <div className="routines-section">
        <h2>추천 운동 루틴</h2>
        <div className="routines-grid">
          {recommendedRoutines.map((routine, index) => (
            <div key={routine.id} className="routine-card">
              <div className="routine-header">
                <h3>{routine.name}</h3>
                <span className="duration">{routine.totalDuration}분</span>
              </div>
              <p className="routine-description">{routine.description}</p>
              <div className="routine-frequency">
                <strong>권장 빈도:</strong> {routine.frequency}
              </div>
              
              <div className="exercises-list">
                <h4>포함 운동:</h4>
                {routine.exercises.map((exercise, exIndex) => (
                  <div key={exercise.id} className="exercise-item">
                    <div className="exercise-header">
                      <span className="exercise-name">{exercise.name}</span>
                      <span 
                        className="difficulty"
                        style={{ backgroundColor: getDifficultyColor(exercise.difficulty) }}
                      >
                        {exercise.difficulty === 'beginner' ? '초급' : 
                         exercise.difficulty === 'intermediate' ? '중급' : '고급'}
                      </span>
                    </div>
                    <p className="exercise-description">{exercise.description}</p>
                    <div className="exercise-duration">{exercise.duration}분</div>
                    
                    <div className="instructions">
                      <strong>운동 방법:</strong>
                      <ol>
                        {exercise.instructions.map((instruction, instIndex) => (
                          <li key={instIndex}>{instruction}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* YouTube 비디오 추천 */}
      <div className="videos-section">
        <h2>추천 운동 비디오</h2>
        <div className="videos-grid">
          {youtubeVideos.map((video) => {
            const analysis = analyzeComments(video.comments);
            return (
              <div key={video.id} className="video-card">
                <div className="video-thumbnail">
                  <img src={video.thumbnail} alt={video.title} />
                  <div className="video-duration">{video.duration}</div>
                </div>
                <div className="video-info">
                  <h3>{video.title}</h3>
                  <p className="video-description">{video.description}</p>
                  <div className="video-stats">
                    <span className="views">조회수: {parseInt(video.viewCount).toLocaleString()}</span>
                    <span className="rating">평점: {video.rating.toFixed(1)}/5</span>
                  </div>
                  
                  {analysis.overallSentiment !== 'neutral' && (
                    <div className={`sentiment ${analysis.overallSentiment}`}>
                      {analysis.overallSentiment === 'positive' ? '👍 긍정적' : '👎 부정적'} 
                      ({analysis.helpfulness.toFixed(0)}% 도움됨)
                    </div>
                  )}
                  
                  {analysis.commonIssues.length > 0 && (
                    <div className="common-issues">
                      <strong>주요 피드백:</strong>
                      <ul>
                        {analysis.commonIssues.map((issue, index) => (
                          <li key={index}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 건강 팁 */}
      <div className="health-tips">
        <h2>건강 관리 팁</h2>
        <div className="tips-grid">
          <div className="tip-card">
            <h3>💡 자세 교정</h3>
            <p>올바른 자세를 유지하는 것이 가장 중요합니다. 정기적으로 자세를 점검하고 교정하세요.</p>
          </div>
          <div className="tip-card">
            <h3>⏰ 휴식 시간</h3>
            <p>1시간마다 5-10분씩 휴식을 취하고 간단한 스트레칭을 하세요.</p>
          </div>
          <div className="tip-card">
            <h3>🏃‍♂️ 규칙적 운동</h3>
            <p>매일 조금씩이라도 꾸준히 운동하는 것이 효과적입니다.</p>
          </div>
          <div className="tip-card">
            <h3>💧 수분 섭취</h3>
            <p>충분한 수분 섭취는 근육과 관절 건강에 도움이 됩니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExerciseRecommendation;
