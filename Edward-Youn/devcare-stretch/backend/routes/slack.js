const express = require('express');
const router = express.Router();
const SlackService = require('../services/slack');
const UserModel = require('../models/user');
const VideoModel = require('../models/video');

const slackService = new SlackService(
  process.env.SLACK_BOT_TOKEN,
  process.env.SLACK_SIGNING_SECRET
);

/**
 * POST /api/slack/schedule-routine
 * 사용자 운동 루틴 스케줄링
 */
router.post('/schedule-routine', async (req, res) => {
  try {
    const {
      userId,
      timeSlots = ['morning'], // ['morning', 'lunch', 'evening']
      weekdays = [1, 2, 3, 4, 5], // 월-금
      sessionDuration = 30,
      selectedVideos = []
    } = req.body;

    if (!userId) {
      return res.status(400).json({
        error: 'User ID required',
        message: '사용자 ID가 필요합니다.'
      });
    }

    // 사용자 정보 조회
    const user = await UserModel.getUser(userId);
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: '사용자를 찾을 수 없습니다.'
      });
    }

    // 운동 루틴 저장
    await UserModel.saveWorkoutRoutine(userId, {
      routineName: `${user.name}의 운동 루틴`,
      timeSlots,
      weekdays,
      sessionDuration,
      selectedVideos
    });

    // Slack DM 채널 열기
    const dmChannel = await slackService.openDirectMessage(user.slack_id);

    // 시간대별 스케줄 생성
    const scheduleResults = [];
    const timeSlotMap = {
      morning: '09:00',
      lunch: '12:00',
      evening: '18:00'
    };

    for (const timeSlot of timeSlots) {
      const time = timeSlotMap[timeSlot];
      if (!time) continue;

      // 다음 주의 스케줄 시간 계산
      const scheduleTimes = slackService.calculateScheduleTimes(time, weekdays);

      for (const scheduleTime of scheduleTimes) {
        try {
          // 추천 영상 조회 (Top 3)
          const latestSurvey = await UserModel.getLatestSurveyResponse(userId);
          const symptoms = latestSurvey?.symptoms || [];
          
          let exercises = selectedVideos;
          if (exercises.length === 0) {
            const recommendedVideos = await VideoModel.getRecommendedVideos(symptoms, 480, 10);
            exercises = recommendedVideos.slice(0, 3);
          }

          // 운동 시작 메시지 생성
          const message = slackService.createWorkoutStartMessage(
            user.name,
            exercises,
            sessionDuration
          );

          // 스케줄 메시지 발송
          const scheduleResult = await slackService.scheduleMessage(
            dmChannel,
            message.text,
            scheduleTime,
            message.blocks
          );

          scheduleResults.push({
            timeSlot,
            scheduleTime,
            status: 'scheduled',
            messageId: scheduleResult.scheduled_message_id
          });

        } catch (scheduleError) {
          console.error(`Schedule error for ${timeSlot}:`, scheduleError);
          scheduleResults.push({
            timeSlot,
            scheduleTime,
            status: 'failed',
            error: scheduleError.message
          });
        }
      }
    }

    // 확인 메시지 즉시 발송
    const confirmationMessage = {
      text: `🎉 ${user.name}님의 운동 루틴이 설정되었습니다!`,
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: "🎯 운동 루틴 설정 완료!"
          }
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*${user.name}님*, 맞춤 운동 루틴이 성공적으로 설정되었습니다!`
          }
        },
        {
          type: "section",
          fields: [
            {
              type: "mrkdwn",
              text: `*운동 시간:*\n${timeSlots.map(slot => timeSlotMap[slot]).join(', ')}`
            },
            {
              type: "mrkdwn",
              text: `*요일:*\n${weekdays.map(day => ['일','월','화','수','목','금','토'][day]).join(', ')}`
            },
            {
              type: "mrkdwn",
              text: `*세션 길이:*\n${sessionDuration}분`
            },
            {
              type: "mrkdwn",
              text: `*운동 개수:*\n${selectedVideos.length || 3}개`
            }
          ]
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: "설정된 시간에 운동 알림을 보내드릴게요! 💪"
          }
        }
      ]
    };

    await slackService.sendMessage(dmChannel, confirmationMessage.text, confirmationMessage.blocks);

    res.json({
      success: true,
      data: {
        message: '운동 루틴이 성공적으로 스케줄되었습니다.',
        scheduleResults,
        user: {
          id: userId,
          name: user.name,
          slackId: user.slack_id
        },
        routine: {
          timeSlots,
          weekdays,
          sessionDuration,
          selectedVideos: selectedVideos.length
        }
      }
    });

  } catch (error) {
    console.error('Schedule Routine Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '루틴 스케줄링 중 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/slack/interactions
 * Slack 인터랙션 처리 (버튼 클릭 등)
 */
router.post('/interactions', async (req, res) => {
  try {
    const payload = JSON.parse(req.body.payload);
    const { type, user, actions, channel } = payload;

    if (type !== 'block_actions') {
      return res.status(200).send('OK');
    }

    const action = actions[0];
    const actionId = action.action_id;
    const actionValue = action.value;

    // 사용자 조회 (Slack ID 기반)
    const dbUser = await UserModel.getUser(user.id, 'slack_id');
    if (!dbUser) {
      await slackService.sendMessage(
        channel.id,
        '❌ 등록된 사용자를 찾을 수 없습니다. 먼저 설문을 진행해주세요.'
      );
      return res.status(200).send('OK');
    }

    switch (actionId) {
      case 'workout_start':
        await handleWorkoutStart(dbUser, channel.id, actionValue);
        break;
      
      case 'workout_snooze':
        await handleWorkoutSnooze(dbUser, channel.id, parseInt(actionValue));
        break;
      
      case 'workout_complete':
        await handleWorkoutComplete(dbUser, channel.id, actionValue);
        break;
      
      default:
        console.log(`Unknown action: ${actionId}`);
    }

    res.status(200).send('OK');

  } catch (error) {
    console.error('Slack Interaction Error:', error);
    res.status(500).send('Error processing interaction');
  }
});

/**
 * POST /api/slack/send-message
 * 즉시 메시지 발송 (테스트용)
 */
router.post('/send-message', async (req, res) => {
  try {
    const { slackId, message, blocks } = req.body;

    if (!slackId || !message) {
      return res.status(400).json({
        error: 'Required fields missing',
        message: 'Slack ID와 메시지가 필요합니다.'
      });
    }

    // DM 채널 열기
    const dmChannel = await slackService.openDirectMessage(slackId);
    
    // 메시지 발송
    const result = await slackService.sendMessage(dmChannel, message, blocks);

    res.json({
      success: true,
      data: {
        message: '메시지가 성공적으로 발송되었습니다.',
        messageId: result.ts,
        channel: dmChannel
      }
    });

  } catch (error) {
    console.error('Send Message Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '메시지 발송 중 오류가 발생했습니다.'
    });
  }
});

// 인터랙션 핸들러 함수들

async function handleWorkoutStart(user, channelId, actionValue) {
  try {
    let exercises = [];
    
    if (actionValue) {
      const parsed = JSON.parse(actionValue);
      exercises = parsed.exercises || [];
    }
    
    if (exercises.length === 0) {
      // 기본 추천 영상 조회
      const latestSurvey = await UserModel.getLatestSurveyResponse(user.id);
      const symptoms = latestSurvey?.symptoms || [];
      const recommendedVideos = await VideoModel.getRecommendedVideos(symptoms, 480, 5);
      exercises = recommendedVideos.slice(0, 3);
    }

    const message = slackService.createWorkoutInProgressMessage(exercises);
    await slackService.sendMessage(channelId, message.text, message.blocks);

  } catch (error) {
    console.error('Handle Workout Start Error:', error);
    await slackService.sendMessage(
      channelId,
      '❌ 운동 시작 처리 중 오류가 발생했습니다.'
    );
  }
}

async function handleWorkoutSnooze(user, channelId, minutes) {
  try {
    const snoozeTime = new Date();
    snoozeTime.setMinutes(snoozeTime.getMinutes() + minutes);
    
    const message = {
      text: `⏰ ${minutes}분 후에 다시 알려드릴게요!`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `⏰ ${user.name}님, ${minutes}분 후에 다시 알려드릴게요!\n\n*다음 알림:* ${snoozeTime.toLocaleTimeString('ko-KR')}`
          }
        }
      ]
    };

    await slackService.sendMessage(channelId, message.text, message.blocks);

    // 스누즈 메시지 스케줄링
    const scheduleTime = Math.floor(snoozeTime.getTime() / 1000);
    
    // 기본 운동 조회
    const latestSurvey = await UserModel.getLatestSurveyResponse(user.id);
    const symptoms = latestSurvey?.symptoms || [];
    const exercises = await VideoModel.getRecommendedVideos(symptoms, 480, 3);
    
    const workoutMessage = slackService.createWorkoutStartMessage(
      user.name,
      exercises.slice(0, 3),
      30
    );

    await slackService.scheduleMessage(
      channelId,
      workoutMessage.text,
      scheduleTime,
      workoutMessage.blocks
    );

  } catch (error) {
    console.error('Handle Workout Snooze Error:', error);
    await slackService.sendMessage(
      channelId,
      '❌ 스누즈 설정 중 오류가 발생했습니다.'
    );
  }
}

async function handleWorkoutComplete(user, channelId, actionValue) {
  try {
    let exercises = [];
    let duration = 30; // 기본값

    if (actionValue && actionValue !== 'skip') {
      try {
        const parsed = JSON.parse(actionValue);
        exercises = parsed.exercises || [];
        duration = parsed.duration || 30;
      } catch (e) {
        // JSON 파싱 실패 시 기본값 사용
      }
    }

    // 운동 완료 기록
    await UserModel.recordWorkoutCompletion(user.id, {
      videoIds: exercises.map(e => e.video_id),
      durationMinutes: duration,
      scheduledTime: new Date().toISOString(),
      metadata: { actionValue }
    });

    // 운동 통계 조회
    const stats = await UserModel.getWorkoutStats(user.id);

    // 완료 메시지 발송
    const message = slackService.createWorkoutCompleteMessage(
      user.name,
      duration,
      stats
    );

    await slackService.sendMessage(channelId, message.text, message.blocks);

  } catch (error) {
    console.error('Handle Workout Complete Error:', error);
    await slackService.sendMessage(
      channelId,
      '❌ 운동 완료 처리 중 오류가 발생했습니다.'
    );
  }
}

module.exports = router;