const { GoogleGenerativeAI } = require('@google/generative-ai');

class GeminiService {
  constructor(apiKey) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' });
  }

  /**
   * 댓글 목록을 분석하여 효과/부정 신호 추출
   * @param {Array} comments - 댓글 배열
   * @param {string} symptom - 증상명
   * @returns {Promise<Object>} 분석 결과
   */
  async analyzeComments(comments, symptom) {
    if (!comments || comments.length === 0) {
      return {
        totalComments: 0,
        positiveCount: 0,
        negativeCount: 0,
        positiveRatio: 0,
        negativeRatio: 0,
        effectKeywords: [],
        sideEffectKeywords: [],
        representativePositive: '',
        representativeNegative: '',
        overallSentiment: 'neutral'
      };
    }

    try {
      const commentsText = comments.map(c => c.text).join('\n---\n');
      
      const prompt = `
다음은 "${symptom}" 관련 운동 영상의 댓글들입니다. 이 댓글들을 분석해서 JSON 형태로 결과를 제공해주세요.

댓글들:
${commentsText}

분석 요구사항:
1. 긍정적 효과를 언급한 댓글 개수
2. 부정적 효과나 불편함을 언급한 댓글 개수  
3. 주요 효과 키워드들 (최대 5개)
4. 부작용/주의사항 키워드들 (최대 3개)
5. 가장 대표적인 긍정 댓글 (20자 이내)
6. 가장 대표적인 부정 댓글 (20자 이내, 없으면 빈 문자열)
7. 전체적인 감정 (positive/negative/neutral)

JSON 형태로만 답변해주세요:
{
  "positiveCount": 숫자,
  "negativeCount": 숫자,
  "effectKeywords": ["키워드1", "키워드2"],
  "sideEffectKeywords": ["주의사항1"],
  "representativePositive": "대표 긍정 댓글",
  "representativeNegative": "대표 부정 댓글",
  "overallSentiment": "positive/negative/neutral"
}`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      // JSON 파싱 시도
      let analysisData;
      try {
        // JSON 부분만 추출
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          analysisData = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('No JSON found in response');
        }
      } catch (parseError) {
        console.warn('Failed to parse Gemini response, using fallback analysis');
        analysisData = this.fallbackAnalysis(comments, symptom);
      }

      // 비율 계산
      const totalComments = comments.length;
      const positiveRatio = totalComments > 0 ? (analysisData.positiveCount / totalComments) : 0;
      const negativeRatio = totalComments > 0 ? (analysisData.negativeCount / totalComments) : 0;

      return {
        totalComments,
        positiveCount: analysisData.positiveCount || 0,
        negativeCount: analysisData.negativeCount || 0,
        positiveRatio: Math.round(positiveRatio * 100) / 100,
        negativeRatio: Math.round(negativeRatio * 100) / 100,
        effectKeywords: analysisData.effectKeywords || [],
        sideEffectKeywords: analysisData.sideEffectKeywords || [],
        representativePositive: analysisData.representativePositive || '',
        representativeNegative: analysisData.representativeNegative || '',
        overallSentiment: analysisData.overallSentiment || 'neutral'
      };

    } catch (error) {
      console.error('Gemini API Error:', error);
      // 폴백 분석 사용
      return this.fallbackAnalysis(comments, symptom);
    }
  }

  /**
   * Gemini API 실패 시 사용할 폴백 분석
   * @param {Array} comments - 댓글 배열
   * @param {string} symptom - 증상명
   * @returns {Object} 기본 분석 결과
   */
  fallbackAnalysis(comments, symptom) {
    const positiveKeywords = ['좋아', '효과', '나아', '시원', '개선', '추천', '도움', '완화', '감사'];
    const negativeKeywords = ['아프', '악화', '별로', '실망', '효과없', '안좋', '위험'];
    
    let positiveCount = 0;
    let negativeCount = 0;
    let representativePositive = '';
    let representativeNegative = '';

    comments.forEach(comment => {
      const text = comment.text.toLowerCase();
      const hasPositive = positiveKeywords.some(keyword => text.includes(keyword));
      const hasNegative = negativeKeywords.some(keyword => text.includes(keyword));
      
      if (hasPositive && !hasNegative) {
        positiveCount++;
        if (!representativePositive && comment.text.length <= 30) {
          representativePositive = comment.text;
        }
      } else if (hasNegative && !hasPositive) {
        negativeCount++;
        if (!representativeNegative && comment.text.length <= 30) {
          representativeNegative = comment.text;
        }
      }
    });

    const totalComments = comments.length;
    const positiveRatio = totalComments > 0 ? (positiveCount / totalComments) : 0;
    const negativeRatio = totalComments > 0 ? (negativeCount / totalComments) : 0;

    let overallSentiment = 'neutral';
    if (positiveRatio > negativeRatio && positiveRatio > 0.3) {
      overallSentiment = 'positive';
    } else if (negativeRatio > positiveRatio && negativeRatio > 0.2) {
      overallSentiment = 'negative';
    }

    return {
      totalComments,
      positiveCount,
      negativeCount,
      positiveRatio: Math.round(positiveRatio * 100) / 100,
      negativeRatio: Math.round(negativeRatio * 100) / 100,
      effectKeywords: positiveRatio > 0.3 ? ['효과적', '도움됨'] : [],
      sideEffectKeywords: negativeRatio > 0.2 ? ['주의필요'] : [],
      representativePositive: representativePositive || '',
      representativeNegative: representativeNegative || '',
      overallSentiment
    };
  }

  /**
   * 영상 제목과 설명을 분석하여 운동 접근법 분류
   * @param {string} title - 영상 제목
   * @param {string} description - 영상 설명
   * @returns {Promise<Object>} 분류 결과
   */
  async categorizeExerciseApproach(title, description) {
    try {
      const prompt = `
영상 제목: ${title}
영상 설명: ${description.substring(0, 200)}...

이 운동 영상을 다음 카테고리 중 하나로 분류해주세요:
1. "stretching" - 스트레칭, 유연성 운동
2. "strengthening" - 근력 강화 운동  
3. "posture" - 자세 교정 운동
4. "mobilization" - 관절 가동성 운동
5. "relaxation" - 이완, 마사지

JSON 형태로만 답변:
{
  "category": "카테고리명",
  "confidence": 0.8,
  "keywords": ["키워드1", "키워드2"]
}`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      try {
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      } catch (parseError) {
        console.warn('Failed to parse categorization, using fallback');
      }

      // 폴백 분류
      return this.fallbackCategorization(title, description);

    } catch (error) {
      console.error('Gemini Categorization Error:', error);
      return this.fallbackCategorization(title, description);
    }
  }

  /**
   * 폴백 운동 분류
   */
  fallbackCategorization(title, description) {
    const text = (title + ' ' + description).toLowerCase();
    
    if (text.includes('스트레칭') || text.includes('stretch')) {
      return { category: 'stretching', confidence: 0.7, keywords: ['스트레칭'] };
    } else if (text.includes('근력') || text.includes('strength')) {
      return { category: 'strengthening', confidence: 0.7, keywords: ['근력'] };
    } else if (text.includes('자세') || text.includes('posture')) {
      return { category: 'posture', confidence: 0.7, keywords: ['자세교정'] };
    } else if (text.includes('마사지') || text.includes('이완')) {
      return { category: 'relaxation', confidence: 0.7, keywords: ['이완'] };
    } else {
      return { category: 'mobilization', confidence: 0.5, keywords: ['운동'] };
    }
  }
}

module.exports = GeminiService;