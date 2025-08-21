const axios = require('axios');

class YouTubeService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://www.googleapis.com/youtube/v3';
  }

  /**
   * 증상 키워드로 YouTube 영상 검색
   * @param {string} keyword - 검색 키워드
   * @param {number} maxResults - 최대 결과 수 (기본 25)
   * @returns {Promise<Array>} 검색 결과
   */
  async searchVideos(keyword, maxResults = 25) {
    try {
      const response = await axios.get(`${this.baseUrl}/search`, {
        params: {
          key: this.apiKey,
          q: `${keyword} 운동 스트레칭 치료`,
          part: 'snippet',
          type: 'video',
          maxResults,
          order: 'relevance',
          videoDefinition: 'any',
          videoDuration: 'any',
          regionCode: 'KR',
          relevanceLanguage: 'ko'
        }
      });

      return response.data.items.map(item => ({
        videoId: item.id.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnail: item.snippet.thumbnails.medium.url,
        channelTitle: item.snippet.channelTitle,
        publishedAt: item.snippet.publishedAt
      }));
    } catch (error) {
      console.error('YouTube Search Error:', error.response?.data || error.message);
      throw new Error('Failed to search YouTube videos');
    }
  }

  /**
   * 여러 영상의 상세 정보 가져오기
   * @param {Array<string>} videoIds - 영상 ID 배열
   * @returns {Promise<Array>} 영상 상세 정보
   */
  async getVideoDetails(videoIds) {
    try {
      const response = await axios.get(`${this.baseUrl}/videos`, {
        params: {
          key: this.apiKey,
          id: videoIds.join(','),
          part: 'snippet,contentDetails,statistics'
        }
      });

      return response.data.items.map(item => ({
        videoId: item.id,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnail: item.snippet.thumbnails.medium.url,
        channelTitle: item.snippet.channelTitle,
        publishedAt: item.snippet.publishedAt,
        duration: this.parseDuration(item.contentDetails.duration),
        viewCount: parseInt(item.statistics.viewCount || 0),
        likeCount: parseInt(item.statistics.likeCount || 0),
        commentCount: parseInt(item.statistics.commentCount || 0),
        hasCaption: item.contentDetails.caption === 'true'
      }));
    } catch (error) {
      console.error('YouTube Video Details Error:', error.response?.data || error.message);
      throw new Error('Failed to get video details');
    }
  }

  /**
   * 영상의 댓글 가져오기 (최대 20개)
   * @param {string} videoId - 영상 ID
   * @param {number} maxResults - 최대 댓글 수 (기본 20)
   * @returns {Promise<Array>} 댓글 목록
   */
  async getVideoComments(videoId, maxResults = 20) {
    try {
      const response = await axios.get(`${this.baseUrl}/commentThreads`, {
        params: {
          key: this.apiKey,
          videoId,
          part: 'snippet',
          order: 'relevance',
          maxResults,
          textFormat: 'plainText'
        }
      });

      return response.data.items.map(item => ({
        commentId: item.id,
        text: item.snippet.topLevelComment.snippet.textDisplay,
        authorDisplayName: item.snippet.topLevelComment.snippet.authorDisplayName,
        likeCount: item.snippet.topLevelComment.snippet.likeCount,
        publishedAt: item.snippet.topLevelComment.snippet.publishedAt
      }));
    } catch (error) {
      // 댓글이 비활성화된 경우 빈 배열 반환
      if (error.response?.status === 403) {
        console.warn(`Comments disabled for video: ${videoId}`);
        return [];
      }
      console.error('YouTube Comments Error:', error.response?.data || error.message);
      return []; // 댓글 에러 시 빈 배열 반환
    }
  }

  /**
   * ISO 8601 duration을 초로 변환
   * @param {string} duration - PT4M13S 형식
   * @returns {number} 초 단위 시간
   */
  parseDuration(duration) {
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    const hours = parseInt(match[1] || 0);
    const minutes = parseInt(match[2] || 0);
    const seconds = parseInt(match[3] || 0);
    return hours * 3600 + minutes * 60 + seconds;
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
}

module.exports = YouTubeService;