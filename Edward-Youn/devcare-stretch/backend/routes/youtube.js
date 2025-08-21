const express = require('express');
const router = express.Router();
const YouTubeService = require('../services/youtube');
const GeminiService = require('../services/gemini');
const VideoModel = require('../models/video');

const youtubeService = new YouTubeService(process.env.YOUTUBE_API_KEY);
const geminiService = new GeminiService(process.env.GEMINI_API_KEY);

/**
 * POST /api/youtube/search
 * YouTube 영상 검색 및 분석
 */
router.post('/search', async (req, res) => {
  try {
    const { keyword, maxResults = 25 } = req.body;

    if (!keyword) {
      return res.status(400).json({
        error: 'Keyword required',
        message: '검색 키워드가 필요합니다.'
      });
    }

    console.log(`Searching YouTube for: ${keyword}`);

    // 1. YouTube 영상 검색
    const searchResults = await youtubeService.searchVideos(keyword, maxResults);
    
    if (searchResults.length === 0) {
      return res.json({
        success: true,
        data: {
          videos: [],
          message: '검색 결과가 없습니다.'
        }
      });
    }

    console.log(`Found ${searchResults.length} videos`);

    // 2. 영상 상세 정보 가져오기
    const videoIds = searchResults.map(video => video.videoId);
    const videoDetails = await youtubeService.getVideoDetails(videoIds);

    console.log(`Retrieved details for ${videoDetails.length} videos`);

    // 3. 각 영상의 댓글 분석 (병렬 처리)
    const processedVideos = await Promise.allSettled(
      videoDetails.map(async (video) => {
        try {
          // 댓글 가져오기 (최대 20개)
          const comments = await youtubeService.getVideoComments(video.videoId, 20);
          
          // Gemini로 댓글 분석
          const commentAnalysis = await geminiService.analyzeComments(comments, keyword);
          
          // 영상 카테고리 분류
          const categoryAnalysis = await geminiService.categorizeExerciseApproach(
            video.title, 
            video.description
          );

          // 데이터 통합
          const processedVideo = {
            ...video,
            commentAnalysis,
            category: categoryAnalysis.category,
            approachKeywords: categoryAnalysis.keywords || [],
            confidence: categoryAnalysis.confidence || 0.5
          };

          // 데이터베이스에 저장
          await VideoModel.upsertVideo({
            ...video,
            category: categoryAnalysis.category,
            approachKeywords: categoryAnalysis.keywords
          });

          // 댓글 요약 저장
          if (commentAnalysis.totalComments > 0) {
            await VideoModel.saveCommentSummary(video.videoId, commentAnalysis);
          }

          // 증상-영상 연관도 저장 (임시 점수)
          const relevanceScore = calculateRelevanceScore(video, commentAnalysis, keyword);
          await VideoModel.saveSymptomIndex(video.videoId, keyword, relevanceScore);

          return processedVideo;

        } catch (error) {
          console.error(`Error processing video ${video.videoId}:`, error.message);
          // 에러가 발생해도 기본 정보는 반환
          return {
            ...video,
            commentAnalysis: {
              totalComments: 0,
              positiveRatio: 0,
              negativeRatio: 0,
              overallSentiment: 'neutral'
            },
            category: 'general',
            error: error.message
          };
        }
      })
    );

    // 성공한 결과만 필터링
    const videos = processedVideos
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value);

    console.log(`Successfully processed ${videos.length} videos`);

    res.json({
      success: true,
      data: {
        videos,
        totalFound: searchResults.length,
        keyword,
        processedAt: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('YouTube Search Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'YouTube 검색 중 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/youtube/video/:videoId
 * 특정 영상 상세 정보 조회
 */
router.get('/video/:videoId', async (req, res) => {
  try {
    const { videoId } = req.params;

    // 데이터베이스에서 먼저 조회
    let video = await VideoModel.getVideoDetails(videoId);

    if (!video) {
      // 데이터베이스에 없으면 실시간 조회
      console.log(`Video ${videoId} not in database, fetching from YouTube...`);
      
      const videoDetails = await youtubeService.getVideoDetails([videoId]);
      
      if (videoDetails.length === 0) {
        return res.status(404).json({
          error: 'Video not found',
          message: '영상을 찾을 수 없습니다.'
        });
      }

      video = videoDetails[0];
      
      // 데이터베이스에 저장
      await VideoModel.upsertVideo(video);
    }

    res.json({
      success: true,
      data: video
    });

  } catch (error) {
    console.error('Get Video Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '영상 정보 조회 중 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/youtube/bulk-process
 * 대량 영상 처리 (n8n에서 호출)
 */
router.post('/bulk-process', async (req, res) => {
  try {
    const { symptoms = [], maxResultsPerSymptom = 30 } = req.body;

    if (symptoms.length === 0) {
      return res.status(400).json({
        error: 'Symptoms required',
        message: '처리할 증상 목록이 필요합니다.'
      });
    }

    const results = {};

    for (const symptom of symptoms) {
      try {
        console.log(`Processing symptom: ${symptom}`);
        
        // 증상별 검색 및 처리
        const response = await processSymptomVideos(symptom, maxResultsPerSymptom);
        results[symptom] = {
          success: true,
          videosProcessed: response.videos.length,
          data: response
        };

      } catch (error) {
        console.error(`Error processing symptom ${symptom}:`, error);
        results[symptom] = {
          success: false,
          error: error.message
        };
      }
    }

    res.json({
      success: true,
      data: {
        results,
        processedAt: new Date().toISOString(),
        totalSymptoms: symptoms.length
      }
    });

  } catch (error) {
    console.error('Bulk Process Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '대량 처리 중 오류가 발생했습니다.'
    });
  }
});

/**
 * 증상별 영상 처리 헬퍼 함수
 */
async function processSymptomVideos(symptom, maxResults) {
  // YouTube 검색
  const searchResults = await youtubeService.searchVideos(symptom, maxResults);
  
  if (searchResults.length === 0) {
    return { videos: [], message: 'No videos found' };
  }

  // 영상 상세 정보
  const videoIds = searchResults.map(v => v.videoId);
  const videoDetails = await youtubeService.getVideoDetails(videoIds);

  // 병렬 처리로 댓글 분석
  const processedVideos = await Promise.allSettled(
    videoDetails.map(async (video) => {
      const comments = await youtubeService.getVideoComments(video.videoId, 20);
      const commentAnalysis = await geminiService.analyzeComments(comments, symptom);
      const categoryAnalysis = await geminiService.categorizeExerciseApproach(
        video.title, 
        video.description
      );

      // 데이터베이스 저장
      await VideoModel.upsertVideo({
        ...video,
        category: categoryAnalysis.category,
        approachKeywords: categoryAnalysis.keywords
      });

      if (commentAnalysis.totalComments > 0) {
        await VideoModel.saveCommentSummary(video.videoId, commentAnalysis);
      }

      const relevanceScore = calculateRelevanceScore(video, commentAnalysis, symptom);
      await VideoModel.saveSymptomIndex(video.videoId, symptom, relevanceScore);

      return {
        ...video,
        commentAnalysis,
        category: categoryAnalysis.category,
        relevanceScore
      };
    })
  );

  return {
    videos: processedVideos
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value),
    symptom,
    totalFound: searchResults.length
  };
}

/**
 * 연관도 점수 계산
 */
function calculateRelevanceScore(video, commentAnalysis, keyword) {
  let score = 0;

  // 제목에 키워드 포함 (30%)
  if (video.title.toLowerCase().includes(keyword.toLowerCase())) {
    score += 0.3;
  }

  // 댓글 긍정 비율 (25%)
  score += (commentAnalysis.positiveRatio || 0) * 0.25;

  // 조회수 정규화 (20%)
  const viewScore = Math.min(video.viewCount / 100000, 1);
  score += viewScore * 0.2;

  // 댓글 수 정규화 (15%)
  const commentScore = Math.min(commentAnalysis.totalComments / 50, 1);
  score += commentScore * 0.15;

  // 자막 여부 (10%)
  if (video.hasCaption) {
    score += 0.1;
  }

  return Math.round(score * 100) / 100;
}

module.exports = router;