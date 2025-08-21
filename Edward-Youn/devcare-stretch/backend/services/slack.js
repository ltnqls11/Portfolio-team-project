const axios = require('axios');

class SlackService {
  constructor(botToken, signingSecret) {
    this.botToken = botToken;
    this.signingSecret = signingSecret;
    this.baseUrl = 'https://slack.com/api';
  }

  /**
   * 스케줄 메시지 발송
   * @param {string} channel - 채널 ID 또는 사용자 ID
   * @param {string} text - 메시지 텍스트
   * @param {number} postAt - Unix timestamp
   * @param {Array} blocks - Slack blocks (선택사항)
   * @returns {Promise<Object>} 스케줄 메시지 결과
   */
  async scheduleMessage(channel, text, postAt, blocks = null) {
    try {
      const payload = {
        channel,
        text,
        post_at: postAt
      };

      if (blocks) {
        payload.blocks = blocks;
      }

      const response = await axios.post(
        `${this.baseUrl}/chat.scheduleMessage`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${this.botToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.data.ok) {
        throw new Error(`Slack API Error: ${response.data.error}`);
      }

      return response.data;

    } catch (error) {
      console.error('Slack Schedule Message Error:', error.response?.data || error.message);
      throw new Error('Failed to schedule message');
    }
  }

  /**
   * 즉시 메시지 발송
   * @param {string} channel - 채널 ID 또는 사용자 ID
   * @param {string} text - 메시지 텍스트
   * @param {Array} blocks - Slack blocks (선택사항)
   * @returns {Promise<Object>} 메시지 발송 결과
   */
  async sendMessage(channel, text, blocks = null) {
    try {
      const payload = {
        channel,
        text
      };

      if (blocks) {
        payload.blocks = blocks;
      }

      const response = await axios.post(
        `${this.baseUrl}/chat.postMessage`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${this.botToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.data.ok) {
        throw new Error(`Slack API Error: ${response.data.error}`);
      }

      return response.data;

    } catch (error) {
      console.error('Slack Send Message Error:', error.response?.data || error.message);
      throw new Error('Failed to send message');
    }
  }

  /**
   * 운동 시작 알림 메시지 생성
   * @param {string} userName - 사용자 이름
   * @param {Array} exercises - 추천 운동 목록
   * @param {number} sessionDuration - 세션 시간 (분)
   * @returns {Object} Slack 메시지 블록
   */
  createWorkoutStartMessage(userName, exercises, sessionDuration) {
    return {
      text: `${userName}님, 운동 시간입니다! 💪`,
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: `🏃‍♂️ ${userName}님의 운동 시간입니다!`
          }
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `오늘의 추천 운동 (${sessionDuration}분 세션):`
          }
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: exercises.slice(0, 3).map((exercise, index) => 
              `${index + 1}. *${exercise.title}* (${this.formatDuration(exercise.duration)})`
            ).join('\n')
          }
        },
        {
          type: "actions",
          elements: [
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "🚀 시작하기"
              },
              style: "primary",
              action_id: "workout_start",
              value: JSON.stringify({ exercises: exercises.slice(0, 3) })
            },
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "⏰ 10분 후"
              },
              action_id: "workout_snooze",
              value: "10"
            },
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "✅ 완료"
              },
              style: "danger",
              action_id: "workout_complete",
              value: "skip"
            }
          ]
        }
      ]
    };
  }

  /**
   * 운동 진행 중 메시지 생성
   * @param {Array} exercises - 운동 목록
   * @returns {Object} Slack 메시지 블록
   */
  createWorkoutInProgressMessage(exercises) {
    return {
      text: "운동 진행 중입니다!",
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: "🔥 운동 진행 중!"
          }
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: "오늘의 운동 목록:"
          }
        },
        ...exercises.map(exercise => ({
          type: "section",
          text: {
            type: "mrkdwn",
            text: `• *${exercise.title}* - ${this.formatDuration(exercise.duration)}`
          },
          accessory: {
            type: "button",
            text: {
              type: "plain_text",
              text: "영상 보기"
            },
            url: `https://www.youtube.com/watch?v=${exercise.videoId}`,
            action_id: "view_video"
          }
        })),
        {
          type: "actions",
          elements: [
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "✅ 운동 완료"
              },
              style: "primary",
              action_id: "workout_complete",
              value: JSON.stringify({ exercises })
            }
          ]
        }
      ]
    };
  }

  /**
   * 운동 완료 메시지 생성
   * @param {string} userName - 사용자 이름
   * @param {number} duration - 운동 시간 (분)
   * @param {Object} stats - 누적 통계
   * @returns {Object} Slack 메시지 블록
   */
  createWorkoutCompleteMessage(userName, duration, stats) {
    return {
      text: "운동 완료! 수고하셨습니다!",
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: `🎉 ${userName}님, 운동 완료!`
          }
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `오늘 운동 시간: *${duration}분*`
          }
        },
        {
          type: "section",
          fields: [
            {
              type: "mrkdwn",
              text: `*이번 주 운동:*\n${stats.weeklyCount || 0}회`
            },
            {
              type: "mrkdwn",
              text: `*총 운동 시간:*\n${stats.totalDuration || 0}분`
            },
            {
              type: "mrkdwn",
              text: `*연속 운동:*\n${stats.streakDays || 0}일`
            },
            {
              type: "mrkdwn",
              text: `*이번 달:*\n${stats.monthlyCount || 0}회`
            }
          ]
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: stats.streakDays >= 7 ? "🔥 일주일 연속 운동! 대단해요!" : "💪 꾸준히 운동하고 계시네요!"
          }
        }
      ]
    };
  }

  /**
   * 사용자 ID로 DM 채널 열기
   * @param {string} userId - 슬랙 사용자 ID
   * @returns {Promise<string>} DM 채널 ID
   */
  async openDirectMessage(userId) {
    try {
      const response = await axios.post(
        `${this.baseUrl}/conversations.open`,
        { users: userId },
        {
          headers: {
            'Authorization': `Bearer ${this.botToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.data.ok) {
        throw new Error(`Slack API Error: ${response.data.error}`);
      }

      return response.data.channel.id;

    } catch (error) {
      console.error('Slack Open DM Error:', error.response?.data || error.message);
      throw new Error('Failed to open direct message');
    }
  }

  /**
   * 초를 MM:SS 형식으로 변환
   * @param {number} seconds - 초
   * @returns {string} MM:SS 형식
   */
  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  /**
   * Unix timestamp를 원하는 시간으로 계산
   * @param {string} time - "09:00" 형식
   * @param {Array} weekdays - [1,2,3,4,5] 형식 (월-금)
   * @returns {Array<number>} Unix timestamp 배열
   */
  calculateScheduleTimes(time, weekdays) {
    const times = [];
    const [hour, minute] = time.split(':').map(Number);
    
    // 다음 주의 해당 요일들에 대한 timestamp 계산
    const now = new Date();
    const currentDay = now.getDay(); // 0=일요일, 1=월요일, ...
    
    weekdays.forEach(targetDay => {
      const daysUntil = (targetDay - currentDay + 7) % 7 || 7; // 0이면 7로 (다음 주)
      const targetDate = new Date(now);
      targetDate.setDate(now.getDate() + daysUntil);
      targetDate.setHours(hour, minute, 0, 0);
      
      times.push(Math.floor(targetDate.getTime() / 1000));
    });
    
    return times;
  }
}

module.exports = SlackService;