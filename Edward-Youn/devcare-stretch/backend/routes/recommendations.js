const express = require('express');
const router = express.Router();
const VideoModel = require('../models/video');
const UserModel = require('../models/user');
const OpenAIService = require('../services/openai');

const openaiService = new OpenAIService(process.env.OPENAI_API_KEY);

/**
 * POST /api/recommendations/generate
 * 사용자 증상에 맞는 운동 영상 추천
 */
router.post('/generate', async (req, res) => {
  try {
    const { userId, symptoms, workHours = 480, sessionDuration = 30 } = req.body;

    if (!symptoms || symptoms.length === 0) {
      return res.status(400).json({
        error: 'Symptoms required',
        message: '증상 정보가 필요합니다.'
      });
    }

    console.log(`Generating recommendations for symptoms: ${symptoms.join(', ')}`);

    // 1. 증상별 추천 영상 조회
    const recommendedVideos = await VideoModel.getRecommendedVideos(
      symptoms, 
      workHours, 
      50
    );

    if (recommendedVideos.length === 0) {
      return res.json({
        success: true,
        data: {
          topVideos: [],
          allVideos: [],
          message: '해당 증상에 대한 추천 영상을 찾을 수 없습니다.',
          totalFound: 0
        }
      });
    }

    // 2. Top 3 영상 선정
    const topVideos = recommendedVideos.slice(0, 3);

    // 3. 추천 이유 생성 (GPT)
    const topVideosWithReasons = await Promise.allSettled(
      topVideos.map(async (video) => {
        try {
          const reason = await openaiService.generateRecommendationReason(video, symptoms);
          return { ...video, recommendationReason: reason };
        } catch (error) {
          return {
            ...video,
            recommendationReason: `${video.title}은(는) ${symptoms.join(', ')} 증상 완화에 도움이 되는 운동입니다.`
          };
        }
      })
    );

    const processedTopVideos = topVideosWithReasons
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value);

    res.json({
      success: true,
      data: {
        topVideos: processedTopVideos,
        allVideos: recommendedVideos,
        totalFound: recommendedVideos.length,
        symptoms,
        sessionDuration,
        message: `귀하의 상태에 맞춰 총 ${recommendedVideos.length}개의 운동을 추천 드립니다. 그 중 상위 3개의 운동은 다음과 같습니다.`,
        generatedAt: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('Generate Recommendations Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '추천 시스템 처리 중 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/recommendations/user/:userId
 * 사용자별 추천 영상 조회
 */
router.get('/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { sessionDuration = 30 } = req.query;

    const latestSurvey = await UserModel.getLatestSurveyResponse(userId);
    if (!latestSurvey) {
      return res.status(404).json({
        error: 'Survey not found',
        message: '설문 응답을 찾을 수 없습니다.'
      });
    }

    const symptoms = latestSurvey.symptoms || [];
    const recommendedVideos = await VideoModel.getRecommendedVideos(symptoms, 480, 30);
    
    const topVideos = recommendedVideos.slice(0, 3);
    const topVideosWithReasons = await Promise.allSettled(
      topVideos.map(async (video) => {
        try {
          const reason = await openaiService.generateRecommendationReason(video, symptoms);
          return { ...video, recommendationReason: reason };
        } catch (error) {
          return {
            ...video,
            recommendationReason: `${video.title}은(는) ${symptoms.join(', ')} 증상 완화에 도움이 되는 운동입니다.`
          };
        }
      })
    );

    const processedTopVideos = topVideosWithReasons
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value);

    res.json({
      success: true,
      data: {
        topVideos: processedTopVideos,
        allVideos: recommendedVideos,
        totalFound: recommendedVideos.length,
        symptoms,
        user: { id: userId }
      }
    });

  } catch (error) {
    console.error('Get User Recommendations Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '사용자 추천 조회 중 오류가 발생했습니다.'
    });
  }
});

module.exports = router;