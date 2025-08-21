const express = require('express');
const router = express.Router();
const UserModel = require('../models/user');
const OpenAIService = require('../services/openai');

const openaiService = new OpenAIService(process.env.OPENAI_API_KEY);

/**
 * POST /api/onboarding/submit
 * 설문 제출 및 스크리닝 요약 생성
 */
router.post('/submit', async (req, res) => {
  try {
    const {
      // 개인 정보
      name,
      contact,
      slackId,
      
      // 설문 응답
      symptoms,
      symptomDetails,
      painLevel,
      workEnvironment,
      workHours,
      dailyHabits
    } = req.body;

    // 입력 검증
    if (!name || !contact || !slackId || !symptoms || symptoms.length === 0) {
      return res.status(400).json({
        error: 'Required fields missing',
        message: '이름, 연락처, 슬랙 ID, 증상은 필수 입력 사항입니다.'
      });
    }

    // 기존 사용자 확인
    let existingUser = await UserModel.getUser(slackId, 'slack_id');
    let userId;

    if (existingUser) {
      userId = existingUser.id;
    } else {
      // 새 사용자 생성
      const userResult = await UserModel.createUser({
        name,
        contact,
        slackId,
        symptoms,
        symptomDetails,
        painLevel,
        workEnvironment,
        workHours,
        dailyHabits
      });
      
      if (!userResult.success) {
        throw new Error('Failed to create user');
      }
      
      userId = userResult.data.id;
    }

    // GPT로 스크리닝 요약 생성
    const surveyData = {
      symptoms,
      symptomDetails,
      painLevel,
      workEnvironment,
      workHours,
      dailyHabits,
      name,
      contact,
      slackId
    };

    console.log('Generating screening summary with GPT...');
    const screeningSummary = await openaiService.generateScreeningSummary(surveyData);

    // 설문 응답 저장
    await UserModel.saveSurveyResponse(userId, {
      ...surveyData,
      screeningSummary
    });

    res.json({
      success: true,
      data: {
        userId,
        screeningSummary,
        symptoms,
        message: '설문이 성공적으로 제출되었습니다.'
      }
    });

  } catch (error) {
    console.error('Onboarding Submit Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '설문 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    });
  }
});

/**
 * GET /api/onboarding/user/:userId
 * 사용자 정보 및 최근 설문 조회
 */
router.get('/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const user = await UserModel.getUser(userId);
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: '사용자를 찾을 수 없습니다.'
      });
    }

    const latestSurvey = await UserModel.getLatestSurveyResponse(userId);

    res.json({
      success: true,
      data: {
        user,
        latestSurvey
      }
    });

  } catch (error) {
    console.error('Get User Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '사용자 정보 조회 중 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/onboarding/user/slack/:slackId
 * Slack ID로 사용자 조회
 */
router.get('/user/slack/:slackId', async (req, res) => {
  try {
    const { slackId } = req.params;

    const user = await UserModel.getUser(slackId, 'slack_id');
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: '해당 Slack ID로 등록된 사용자를 찾을 수 없습니다.'
      });
    }

    const latestSurvey = await UserModel.getLatestSurveyResponse(user.id);
    const workoutStats = await UserModel.getWorkoutStats(user.id);

    res.json({
      success: true,
      data: {
        user,
        latestSurvey,
        workoutStats
      }
    });

  } catch (error) {
    console.error('Get User by Slack ID Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '사용자 조회 중 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/onboarding/regenerate-summary
 * 스크리닝 요약 재생성
 */
router.post('/regenerate-summary', async (req, res) => {
  try {
    const { userId } = req.body;

    if (!userId) {
      return res.status(400).json({
        error: 'User ID required',
        message: '사용자 ID가 필요합니다.'
      });
    }

    const latestSurvey = await UserModel.getLatestSurveyResponse(userId);
    if (!latestSurvey) {
      return res.status(404).json({
        error: 'Survey not found',
        message: '설문 응답을 찾을 수 없습니다.'
      });
    }

    // 새로운 스크리닝 요약 생성
    const screeningSummary = await openaiService.generateScreeningSummary(latestSurvey.response_data);

    // 설문 응답 업데이트
    await UserModel.saveSurveyResponse(userId, {
      ...latestSurvey.response_data,
      screeningSummary
    });

    res.json({
      success: true,
      data: {
        screeningSummary
      }
    });

  } catch (error) {
    console.error('Regenerate Summary Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '스크리닝 요약 재생성 중 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/onboarding/symptoms
 * 지원되는 증상 목록 조회
 */
router.get('/symptoms', (req, res) => {
  const symptoms = [
    {
      id: 'turtle_neck',
      name: '거북목',
      description: '목이 앞으로 나온 자세로 인한 목과 어깨 통증',
      keywords: ['거북목', '목통증', '경추']
    },
    {
      id: 'round_shoulder',
      name: '라운드숄더',
      description: '어깨가 앞으로 말린 자세로 인한 어깨와 등 통증',
      keywords: ['라운드숄더', '어깨통증', '흉추']
    },
    {
      id: 'lower_back_pain',
      name: '허리통증',
      description: '장시간 앉아있는 자세로 인한 요추 부위 통증',
      keywords: ['허리통증', '요통', '요추']
    },
    {
      id: 'wrist_pain',
      name: '손목통증',
      description: '반복적인 마우스/키보드 사용으로 인한 손목 통증',
      keywords: ['손목통증', '수근관증후군', '테니스엘보']
    },
    {
      id: 'eye_strain',
      name: '눈의피로',
      description: '장시간 모니터 사용으로 인한 눈의 피로와 두통',
      keywords: ['눈피로', '안구건조', '두통']
    }
  ];

  res.json({
    success: true,
    data: symptoms
  });
});

module.exports = router;