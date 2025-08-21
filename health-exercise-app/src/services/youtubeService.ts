import { YouTubeVideo, Comment } from '../types';

// YouTube API 키 (실제 사용시 환경변수로 관리해야 함)
const YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'; // 실제 API 키로 교체 필요

// YouTube API 기본 URL
const YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3';

// 운동 키워드 매핑
const exerciseKeywords: Record<string, string[]> = {
  turtle_neck: ['거북목 운동', '목 스트레칭', '턱 당기기 운동', 'neck exercise'],
  rounded_shoulders: ['둥근 어깨 교정', '어깨 자세 교정', 'shoulder posture correction'],
  disc_herniation: ['허리 디스크 운동', '허리 스트레칭', 'back exercise'],
  carpal_tunnel_syndrome: ['손목 터널 증후군 운동', '손목 스트레칭', 'wrist exercise']
};

// YouTube 비디오 검색 함수
export const searchExerciseVideos = async (
  symptoms: string[],
  maxResults: number = 10
): Promise<YouTubeVideo[]> => {
  try {
    const keywords = symptoms
      .map(symptom => exerciseKeywords[symptom] || [])
      .flat()
      .slice(0, 3); // 상위 3개 키워드만 사용

    const searchQuery = keywords.join(' OR ');
    
    const response = await fetch(
      `${YOUTUBE_API_BASE_URL}/search?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&maxResults=${maxResults}&key=${YOUTUBE_API_KEY}`
    );

    if (!response.ok) {
      throw new Error('YouTube API 요청 실패');
    }

    const data = await response.json();
    
    // 비디오 상세 정보 가져오기
    const videoIds = data.items.map((item: any) => item.id.videoId).join(',');
    const videoDetailsResponse = await fetch(
      `${YOUTUBE_API_BASE_URL}/videos?part=snippet,statistics,contentDetails&id=${videoIds}&key=${YOUTUBE_API_KEY}`
    );

    if (!videoDetailsResponse.ok) {
      throw new Error('비디오 상세 정보 요청 실패');
    }

    const videoDetails = await videoDetailsResponse.json();

    // 댓글 정보 가져오기 (상위 3개 비디오만)
    const topVideoIds = data.items.slice(0, 3).map((item: any) => item.id.videoId);
    const commentsPromises = topVideoIds.map(async (videoId: string) => {
      try {
        const commentsResponse = await fetch(
          `${YOUTUBE_API_BASE_URL}/commentThreads?part=snippet&videoId=${videoId}&maxResults=10&key=${YOUTUBE_API_KEY}`
        );
        
        if (commentsResponse.ok) {
          const commentsData = await commentsResponse.json();
          return {
            videoId,
            comments: commentsData.items.map((item: any) => ({
              id: item.id,
              author: item.snippet.topLevelComment.snippet.authorDisplayName,
              text: item.snippet.topLevelComment.snippet.textDisplay,
              rating: 0, // YouTube API에서 별점 정보는 제공하지 않음
              date: item.snippet.topLevelComment.snippet.publishedAt
            }))
          };
        }
        return { videoId, comments: [] };
      } catch (error) {
        console.error(`댓글 가져오기 실패 (${videoId}):`, error);
        return { videoId, comments: [] };
      }
    });

    const commentsResults = await Promise.all(commentsPromises);

    // 결과 조합
    return data.items.map((item: any, index: number) => {
      const videoDetail = videoDetails.items.find((v: any) => v.id === item.id.videoId);
      const commentsData = commentsResults.find(c => c.videoId === item.id.videoId);
      
      return {
        id: item.id.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnail: item.snippet.thumbnails.high.url,
        duration: videoDetail?.contentDetails?.duration || 'PT0S',
        viewCount: videoDetail?.statistics?.viewCount || '0',
        rating: calculateVideoRating(commentsData?.comments || []),
        comments: commentsData?.comments || []
      };
    });
  } catch (error) {
    console.error('YouTube 비디오 검색 오류:', error);
    return [];
  }
};

// 비디오 평점 계산 함수 (댓글 분석 기반)
const calculateVideoRating = (comments: Comment[]): number => {
  if (comments.length === 0) return 0;

  // 간단한 키워드 기반 평점 계산
  const positiveKeywords = ['좋아요', '도움', '효과', '추천', '유용', '좋은', '훌륭'];
  const negativeKeywords = ['별로', '도움안됨', '효과없음', '비추천', '쓰레기', '나쁜'];

  let totalScore = 0;
  
  comments.forEach(comment => {
    const text = comment.text.toLowerCase();
    let score = 0;
    
    positiveKeywords.forEach(keyword => {
      if (text.includes(keyword)) score += 1;
    });
    
    negativeKeywords.forEach(keyword => {
      if (text.includes(keyword)) score -= 1;
    });
    
    totalScore += score;
  });

  // 0-5점 스케일로 변환
  const averageScore = totalScore / comments.length;
  return Math.max(0, Math.min(5, (averageScore + 2) * 2.5));
};

// 댓글 분석 함수
export const analyzeComments = (comments: Comment[]): {
  overallSentiment: 'positive' | 'negative' | 'neutral';
  helpfulness: number;
  commonIssues: string[];
} => {
  if (comments.length === 0) {
    return {
      overallSentiment: 'neutral',
      helpfulness: 0,
      commonIssues: []
    };
  }

  const positiveCount = comments.filter(comment => 
    comment.rating >= 4 || 
    comment.text.includes('좋아요') || 
    comment.text.includes('도움')
  ).length;

  const negativeCount = comments.filter(comment => 
    comment.rating <= 2 || 
    comment.text.includes('별로') || 
    comment.text.includes('도움안됨')
  ).length;

  const overallSentiment = positiveCount > negativeCount ? 'positive' : 
                          negativeCount > positiveCount ? 'negative' : 'neutral';

  const helpfulness = (positiveCount / comments.length) * 100;

  // 일반적인 문제점 추출
  const commonIssues: string[] = [];
  const issueKeywords = ['어려워', '복잡해', '시간이 오래', '효과없음'];
  
  issueKeywords.forEach(keyword => {
    const count = comments.filter(comment => comment.text.includes(keyword)).length;
    if (count > comments.length * 0.2) { // 20% 이상이 언급하면 공통 문제로 간주
      commonIssues.push(keyword);
    }
  });

  return {
    overallSentiment,
    helpfulness,
    commonIssues
  };
};

// 모의 데이터 (API 키가 없을 때 사용)
export const getMockExerciseVideos = (): YouTubeVideo[] => {
  return [
    {
      id: 'mock_video_1',
      title: '거북목 교정 운동 - 5분 완성',
      description: '오랜 시간 컴퓨터 작업으로 인한 거북목을 교정하는 운동입니다.',
      thumbnail: 'https://via.placeholder.com/320x180/4CAF50/FFFFFF?text=거북목+운동',
      duration: 'PT5M30S',
      viewCount: '125000',
      rating: 4.5,
      comments: [
        {
          id: 'comment_1',
          author: '김철수',
          text: '정말 도움이 되었어요! 매일 하고 있는데 목이 훨씬 좋아졌습니다.',
          rating: 5,
          date: '2024-01-15T10:30:00Z'
        },
        {
          id: 'comment_2',
          author: '이영희',
          text: '간단하고 효과적이네요. 추천합니다!',
          rating: 4,
          date: '2024-01-14T15:20:00Z'
        }
      ]
    },
    {
      id: 'mock_video_2',
      title: '둥근 어깨 교정 운동',
      description: '일상생활에서 쉽게 할 수 있는 어깨 자세 교정 운동입니다.',
      thumbnail: 'https://via.placeholder.com/320x180/2196F3/FFFFFF?text=어깨+교정',
      duration: 'PT8M15S',
      viewCount: '89000',
      rating: 4.2,
      comments: [
        {
          id: 'comment_3',
          author: '박민수',
          text: '어깨 통증이 많이 줄어들었어요. 감사합니다!',
          rating: 4,
          date: '2024-01-13T09:15:00Z'
        }
      ]
    }
  ];
};
