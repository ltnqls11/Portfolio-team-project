const { supabase, supabaseAdmin } = require('../config/supabase');

class UserModel {
  /**
   * 새 사용자 생성
   * @param {Object} userData - 사용자 데이터
   * @returns {Promise<Object>} 생성 결과
   */
  static async createUser(userData) {
    try {
      const { data, error } = await supabaseAdmin
        .from('users')
        .insert([{
          name: userData.name,
          contact: userData.contact,
          slack_id: userData.slackId,
          symptoms: userData.symptoms || [],
          symptom_details: userData.symptomDetails || '',
          pain_level: userData.painLevel || 0,
          work_environment: userData.workEnvironment || '',
          work_hours: userData.workHours || '',
          daily_habits: userData.dailyHabits || '',
          created_at: new Date().toISOString()
        }])
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Create User Error:', error);
      throw new Error('Failed to create user');
    }
  }

  /**
   * 사용자 정보 조회
   * @param {string} identifier - 사용자 ID 또는 Slack ID
   * @param {string} type - 'id' 또는 'slack_id'
   * @returns {Promise<Object>} 사용자 정보
   */
  static async getUser(identifier, type = 'id') {
    try {
      const column = type === 'slack_id' ? 'slack_id' : 'id';
      
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq(column, identifier)
        .single();

      if (error) throw error;
      return data;

    } catch (error) {
      console.error('Get User Error:', error);
      return null;
    }
  }

  /**
   * 설문 응답 저장
   * @param {string} userId - 사용자 ID
   * @param {Object} surveyData - 설문 데이터
   * @returns {Promise<Object>} 저장 결과
   */
  static async saveSurveyResponse(userId, surveyData) {
    try {
      const { data, error } = await supabaseAdmin
        .from('survey_responses')
        .insert([{
          user_id: userId,
          symptoms: surveyData.symptoms,
          symptom_details: surveyData.symptomDetails,
          pain_level: surveyData.painLevel,
          work_environment: surveyData.workEnvironment,
          work_hours: surveyData.workHours,
          daily_habits: surveyData.dailyHabits,
          screening_summary: surveyData.screeningSummary || '',
          response_data: surveyData,
          created_at: new Date().toISOString()
        }])
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Save Survey Response Error:', error);
      throw new Error('Failed to save survey response');
    }
  }

  /**
   * 사용자의 최근 설문 응답 조회
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 최근 설문 응답
   */
  static async getLatestSurveyResponse(userId) {
    try {
      const { data, error } = await supabase
        .from('survey_responses')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (error) throw error;
      return data;

    } catch (error) {
      console.error('Get Latest Survey Response Error:', error);
      return null;
    }
  }

  /**
   * 사용자 운동 루틴 저장
   * @param {string} userId - 사용자 ID
   * @param {Object} routineData - 루틴 데이터
   * @returns {Promise<Object>} 저장 결과
   */
  static async saveWorkoutRoutine(userId, routineData) {
    try {
      const { data, error } = await supabaseAdmin
        .from('workout_routines')
        .upsert([{
          user_id: userId,
          routine_name: routineData.routineName || 'My Routine',
          time_slots: routineData.timeSlots || [], // ['morning', 'lunch', 'evening']
          weekdays: routineData.weekdays || [], // [1,2,3,4,5]
          session_duration: routineData.sessionDuration || 30,
          selected_videos: routineData.selectedVideos || [],
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }], {
          onConflict: 'user_id',
          update: ['routine_name', 'time_slots', 'weekdays', 'session_duration', 'selected_videos', 'updated_at']
        })
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Save Workout Routine Error:', error);
      throw new Error('Failed to save workout routine');
    }
  }

  /**
   * 사용자 운동 루틴 조회
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 운동 루틴
   */
  static async getWorkoutRoutine(userId) {
    try {
      const { data, error } = await supabase
        .from('workout_routines')
        .select('*')
        .eq('user_id', userId)
        .eq('is_active', true)
        .single();

      if (error) throw error;
      return data;

    } catch (error) {
      console.error('Get Workout Routine Error:', error);
      return null;
    }
  }

  /**
   * 운동 완료 기록 저장
   * @param {string} userId - 사용자 ID
   * @param {Object} workoutData - 운동 데이터
   * @returns {Promise<Object>} 저장 결과
   */
  static async recordWorkoutCompletion(userId, workoutData) {
    try {
      const { data, error } = await supabaseAdmin
        .from('workout_events')
        .insert([{
          user_id: userId,
          event_type: 'completed',
          video_ids: workoutData.videoIds || [],
          duration_minutes: workoutData.durationMinutes || 0,
          scheduled_time: workoutData.scheduledTime,
          completed_at: new Date().toISOString(),
          metadata: workoutData.metadata || {}
        }])
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Record Workout Completion Error:', error);
      throw new Error('Failed to record workout completion');
    }
  }

  /**
   * 사용자 운동 통계 조회
   * @param {string} userId - 사용자 ID
   * @param {number} days - 조회할 일수 (기본 30일)
   * @returns {Promise<Object>} 운동 통계
   */
  static async getWorkoutStats(userId, days = 30) {
    try {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);

      const { data, error } = await supabase
        .from('workout_events')
        .select('*')
        .eq('user_id', userId)
        .eq('event_type', 'completed')
        .gte('completed_at', startDate.toISOString());

      if (error) throw error;

      const events = data || [];
      
      // 통계 계산
      const stats = {
        totalWorkouts: events.length,
        totalDuration: events.reduce((sum, event) => sum + (event.duration_minutes || 0), 0),
        weeklyCount: 0,
        monthlyCount: events.length,
        streakDays: 0,
        averageDuration: 0,
        lastWorkout: events.length > 0 ? events[events.length - 1].completed_at : null
      };

      // 주간 운동 횟수 (최근 7일)
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - 7);
      stats.weeklyCount = events.filter(event => 
        new Date(event.completed_at) >= weekStart
      ).length;

      // 평균 운동 시간
      if (stats.totalWorkouts > 0) {
        stats.averageDuration = Math.round(stats.totalDuration / stats.totalWorkouts);
      }

      // 연속 운동 일수 계산 (연속으로 운동한 날)
      const uniqueDates = [...new Set(events.map(event => 
        new Date(event.completed_at).toDateString()
      ))].sort((a, b) => new Date(b) - new Date(a));

      let streakDays = 0;
      const today = new Date().toDateString();
      
      for (let i = 0; i < uniqueDates.length; i++) {
        const checkDate = new Date();
        checkDate.setDate(checkDate.getDate() - i);
        
        if (uniqueDates.includes(checkDate.toDateString())) {
          streakDays++;
        } else {
          break;
        }
      }
      
      stats.streakDays = streakDays;

      return stats;

    } catch (error) {
      console.error('Get Workout Stats Error:', error);
      throw new Error('Failed to get workout stats');
    }
  }

  /**
   * 사용자 선호도 업데이트
   * @param {string} userId - 사용자 ID
   * @param {Object} preferences - 선호도 데이터
   * @returns {Promise<Object>} 업데이트 결과
   */
  static async updateUserPreferences(userId, preferences) {
    try {
      const { data, error } = await supabaseAdmin
        .from('users')
        .update({
          preferences: preferences,
          updated_at: new Date().toISOString()
        })
        .eq('id', userId)
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Update User Preferences Error:', error);
      throw new Error('Failed to update user preferences');
    }
  }
}

module.exports = UserModel;