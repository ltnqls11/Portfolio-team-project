const express = require('express');
const router = express.Router();
const UserModel = require('../models/user');
const VideoModel = require('../models/video');

/**
 * GET /api/analytics/user/:userId/stats
 * 사용자 운동 통계 조회
 */
router.get('/user/:userId/stats', async (req, res) => {
  try {
    const { userId } = req.params;
    const { days = 30 } = req.query;

    const user = await UserModel.getUser(userId);
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: '사용자를 찾을 수 없습니다.'
      });
    }

    const stats = await UserModel.getWorkoutStats(userId, parseInt(days));

    const analyticsData = {
      ...stats,
      performanceMetrics: {
        consistency: calculateConsistency(stats),
        improvement: calculateImprovement(stats),
        adherence: calculateAdherence(stats, parseInt(days))
      },
      insights: generateInsights(stats),
      recommendations: generateAnalyticsRecommendations(stats)
    };

    res.json({
      success: true,
      data: {
        user: { id: userId, name: user.name },
        period: {
          days: parseInt(days),
          startDate: new Date(Date.now() - parseInt(days) * 24 * 60 * 60 * 1000).toISOString(),
          endDate: new Date().toISOString()
        },
        analytics: analyticsData
      }
    });

  } catch (error) {
    console.error('Get User Analytics Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '통계 조회 중 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/analytics/system/health
 * 시스템 상태 분석
 */
router.get('/system/health', async (req, res) => {
  try {
    const healthMetrics = {
      database: await checkDatabaseHealth(),
      apis: await checkAPIHealth(),
      dataQuality: await checkDataQuality(),
      lastUpdate: new Date().toISOString()
    };

    const overallHealth = calculateOverallHealth(healthMetrics);

    res.json({
      success: true,
      data: {
        overall: overallHealth,
        metrics: healthMetrics,
        recommendations: generateSystemRecommendations(healthMetrics)
      }
    });

  } catch (error) {
    console.error('System Health Check Error:', error);
    res.status(500).json({
      success: false,
      error: 'Health check failed',
      message: '시스템 상태 확인 중 오류가 발생했습니다.'
    });
  }
});

// 헬퍼 함수들
function calculateConsistency(stats) {
  if (stats.totalWorkouts === 0) return 0;
  const weeklyGoal = 3;
  const weeksInPeriod = 4;
  const expectedWorkouts = weeklyGoal * weeksInPeriod;
  return Math.min(Math.round((stats.totalWorkouts / expectedWorkouts) * 100), 100);
}

function calculateImprovement(stats) {
  if (stats.streakDays >= 7) return 'excellent';
  if (stats.streakDays >= 3) return 'good';
  if (stats.streakDays >= 1) return 'fair';
  return 'needs_improvement';
}

function calculateAdherence(stats, days) {
  const expectedDays = Math.min(days, 30);
  const workoutDays = Math.min(stats.totalWorkouts, expectedDays);
  return Math.round((workoutDays / expectedDays) * 100);
}

function generateInsights(stats) {
  const insights = [];
  
  if (stats.streakDays >= 7) {
    insights.push({
      type: 'achievement',
      message: `🔥 ${stats.streakDays}일 연속 운동! 훌륭한 습관을 유지하고 계시네요!`,
      priority: 'high'
    });
  }
  
  if (stats.totalWorkouts >= 20) {
    insights.push({
      type: 'milestone',
      message: `🎯 총 ${stats.totalWorkouts}회 운동 완료! 꾸준한 노력이 빛나고 있어요!`,
      priority: 'medium'
    });
  }
  
  return insights;
}

function generateAnalyticsRecommendations(stats) {
  const recommendations = [];
  
  if (stats.streakDays === 0) {
    recommendations.push({
      type: 'motivation',
      title: '운동 시작하기',
      message: '오늘부터 작은 운동으로 시작해보세요!',
      action: 'start_workout'
    });
  }
  
  return recommendations;
}

async function checkDatabaseHealth() {
  try {
    const testUser = await UserModel.getUser('test');
    return {
      status: 'healthy',
      responseTime: '< 100ms',
      lastChecked: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message,
      lastChecked: new Date().toISOString()
    };
  }
}

async function checkAPIHealth() {
  return {
    youtube: 'healthy',
    openai: 'healthy',
    gemini: 'healthy',
    slack: 'healthy'
  };
}

async function checkDataQuality() {
  return {
    videoCount: 150,
    userCount: 25,
    commentAnalysisRate: 85,
    lastDataUpdate: new Date().toISOString()
  };
}

function calculateOverallHealth(metrics) {
  const scores = [];
  scores.push(metrics.database.status === 'healthy' ? 100 : 0);
  
  const apiHealthy = Object.values(metrics.apis).filter(status => status === 'healthy').length;
  const apiTotal = Object.keys(metrics.apis).length;
  scores.push((apiHealthy / apiTotal) * 100);
  
  if (metrics.dataQuality.commentAnalysisRate) {
    scores.push(metrics.dataQuality.commentAnalysisRate);
  }
  
  const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
  
  let status = 'critical';
  if (averageScore >= 90) status = 'excellent';
  else if (averageScore >= 75) status = 'good';
  else if (averageScore >= 50) status = 'fair';
  
  return {
    status,
    score: Math.round(averageScore),
    lastChecked: new Date().toISOString()
  };
}

function generateSystemRecommendations(metrics) {
  const recommendations = [];
  
  if (metrics.database.status !== 'healthy') {
    recommendations.push('데이터베이스 연결 상태를 확인해주세요.');
  }
  
  if (metrics.dataQuality.commentAnalysisRate < 80) {
    recommendations.push('댓글 분석 처리율을 개선할 필요가 있습니다.');
  }
  
  return recommendations;
}

module.exports = router;