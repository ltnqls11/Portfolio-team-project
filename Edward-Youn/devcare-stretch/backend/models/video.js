const { supabase, supabaseAdmin } = require('../config/supabase');

class VideoModel {
  /**
   * 영상 데이터 삽입 또는 업데이트
   * @param {Object} videoData - 영상 데이터
   * @returns {Promise<Object>} 삽입/업데이트 결과
   */
  static async upsertVideo(videoData) {
    try {
      const { data, error } = await supabaseAdmin
        .from('videos')
        .upsert([{
          video_id: videoData.videoId,
          title: videoData.title,
          description: videoData.description,
          thumbnail_url: videoData.thumbnail,
          channel_title: videoData.channelTitle,
          published_at: videoData.publishedAt,
          duration_seconds: videoData.duration,
          view_count: videoData.viewCount,
          like_count: videoData.likeCount,
          comment_count: videoData.commentCount,
          has_caption: videoData.hasCaption,
          category: videoData.category || 'general',
          approach_keywords: videoData.approachKeywords || [],
          updated_at: new Date().toISOString()
        }], {
          onConflict: 'video_id',
          returning: 'minimal'
        });

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Video Upsert Error:', error);
      throw new Error('Failed to upsert video data');
    }
  }

  /**
   * 증상별 영상 검색
   * @param {Array<string>} symptoms - 증상 목록
   * @param {number} limit - 결과 제한 수
   * @returns {Promise<Array>} 영상 목록
   */
  static async getVideosBySymptoms(symptoms, limit = 20) {
    try {
      let query = supabase
        .from('videos')
        .select(`
          *,
          video_comment_summary (
            total_comments,
            positive_count,
            negative_count,
            positive_ratio,
            negative_ratio,
            effect_keywords,
            side_effect_keywords,
            representative_positive,
            representative_negative,
            overall_sentiment
          ),
          symptom_index!inner (
            symptom_name,
            relevance_score
          )
        `)
        .in('symptom_index.symptom_name', symptoms)
        .order('symptom_index.relevance_score', { ascending: false })
        .limit(limit);

      const { data, error } = await query;

      if (error) throw error;
      return data || [];

    } catch (error) {
      console.error('Get Videos By Symptoms Error:', error);
      throw new Error('Failed to get videos by symptoms');
    }
  }

  /**
   * 특정 영상 상세 정보 조회
   * @param {string} videoId - 영상 ID
   * @returns {Promise<Object>} 영상 상세 정보
   */
  static async getVideoDetails(videoId) {
    try {
      const { data, error } = await supabase
        .from('videos')
        .select(`
          *,
          video_comment_summary (*),
          symptom_index (*)
        `)
        .eq('video_id', videoId)
        .single();

      if (error) throw error;
      return data;

    } catch (error) {
      console.error('Get Video Details Error:', error);
      throw new Error('Failed to get video details');
    }
  }

  /**
   * 영상의 댓글 요약 저장
   * @param {string} videoId - 영상 ID
   * @param {Object} commentSummary - 댓글 요약 데이터
   * @returns {Promise<Object>} 저장 결과
   */
  static async saveCommentSummary(videoId, commentSummary) {
    try {
      const { data, error } = await supabaseAdmin
        .from('video_comment_summary')
        .upsert([{
          video_id: videoId,
          total_comments: commentSummary.totalComments,
          positive_count: commentSummary.positiveCount,
          negative_count: commentSummary.negativeCount,
          positive_ratio: commentSummary.positiveRatio,
          negative_ratio: commentSummary.negativeRatio,
          effect_keywords: commentSummary.effectKeywords,
          side_effect_keywords: commentSummary.sideEffectKeywords,
          representative_positive: commentSummary.representativePositive,
          representative_negative: commentSummary.representativeNegative,
          overall_sentiment: commentSummary.overallSentiment,
          analyzed_at: new Date().toISOString()
        }], {
          onConflict: 'video_id'
        });

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Save Comment Summary Error:', error);
      throw new Error('Failed to save comment summary');
    }
  }

  /**
   * 증상-영상 연관도 저장
   * @param {string} videoId - 영상 ID
   * @param {string} symptom - 증상명
   * @param {number} relevanceScore - 연관도 점수
   * @returns {Promise<Object>} 저장 결과
   */
  static async saveSymptomIndex(videoId, symptom, relevanceScore) {
    try {
      const { data, error } = await supabaseAdmin
        .from('symptom_index')
        .upsert([{
          video_id: videoId,
          symptom_name: symptom,
          relevance_score: relevanceScore,
          indexed_at: new Date().toISOString()
        }], {
          onConflict: 'video_id,symptom_name'
        });

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Save Symptom Index Error:', error);
      throw new Error('Failed to save symptom index');
    }
  }

  /**
   * 추천 점수 계산 및 정렬된 영상 목록 조회
   * @param {Array<string>} symptoms - 증상 목록
   * @param {number} workHours - 근무 시간 (분)
   * @param {number} limit - 결과 제한 수
   * @returns {Promise<Array>} 정렬된 영상 목록
   */
  static async getRecommendedVideos(symptoms, workHours = 480, limit = 20) {
    try {
      const videos = await this.getVideosBySymptoms(symptoms, limit * 2);
      
      // 추천 점수 계산
      const scoredVideos = videos.map(video => {
        let score = 0;
        
        // 기본 연관도 점수 (40%)
        const relevanceScore = video.symptom_index?.[0]?.relevance_score || 0;
        score += relevanceScore * 0.4;
        
        // 댓글 긍정 비율 (30%)
        const positiveRatio = video.video_comment_summary?.[0]?.positive_ratio || 0;
        score += positiveRatio * 0.3;
        
        // 조회수 정규화 (15%)
        const viewScore = Math.min(video.view_count / 100000, 1);
        score += viewScore * 0.15;
        
        // 자막 여부 (10%)
        if (video.has_caption) {
          score += 0.1;
        }
        
        // 시간 적합성 (5%) - 근무시간에 맞는 짧은 영상 선호
        const durationScore = workHours < 300 ? 
          Math.max(0, (300 - video.duration_seconds) / 300) : 0.5;
        score += durationScore * 0.05;
        
        return {
          ...video,
          recommendation_score: Math.round(score * 100) / 100
        };
      });
      
      // 점수순 정렬 후 상위 limit개 반환
      return scoredVideos
        .sort((a, b) => b.recommendation_score - a.recommendation_score)
        .slice(0, limit);

    } catch (error) {
      console.error('Get Recommended Videos Error:', error);
      throw new Error('Failed to get recommended videos');
    }
  }

  /**
   * 영상 통계 업데이트
   * @param {string} videoId - 영상 ID
   * @param {Object} stats - 업데이트할 통계
   * @returns {Promise<Object>} 업데이트 결과
   */
  static async updateVideoStats(videoId, stats) {
    try {
      const updateData = {};
      
      if (stats.viewCount !== undefined) updateData.view_count = stats.viewCount;
      if (stats.likeCount !== undefined) updateData.like_count = stats.likeCount;
      if (stats.commentCount !== undefined) updateData.comment_count = stats.commentCount;
      
      updateData.updated_at = new Date().toISOString();

      const { data, error } = await supabaseAdmin
        .from('videos')
        .update(updateData)
        .eq('video_id', videoId);

      if (error) throw error;
      return { success: true, data };

    } catch (error) {
      console.error('Update Video Stats Error:', error);
      throw new Error('Failed to update video stats');
    }
  }
}

module.exports = VideoModel;