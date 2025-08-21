const OpenAI = require('openai');

class OpenAIService {
  constructor(apiKey) {
    this.openai = new OpenAI({
      apiKey: apiKey
    });
  }

  /**
   * 설문 데이터를 기반으로 전문의 톤의 스크리닝 요약 생성
   * @param {Object} surveyData - 설문 응답 데이터
   * @returns {Promise<string>} 스크리닝 요약
   */
  async generateScreeningSummary(surveyData) {
    try {
      const prompt = this.buildScreeningPrompt(surveyData);
      
      const completion = await this.openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: `당신은 재활의학과 전문의이자 운동치료 전문가입니다. 
설문 응답을 바탕으로 해부학적, 운동학적 관점에서 전문적인 스크리닝 분석을 제공합니다.
- 3-5문장으로 간결하게 작성
- 의학 용어를 적절히 사용 (경추 전방머리자세, 흉추 후만증, 전거근, 하부승모근 등)
- 마지막에 추천 접근법과 주의사항을 각각 1줄씩 포함
- 진단이 아닌 스크리닝 관점에서 서술
- 전문적이면서도 이해하기 쉬운 톤으로 작성`
          },
          {
            role: "user", 
            content: prompt
          }
        ],
        max_tokens: 400,
        temperature: 0.7
      });

      return completion.choices[0].message.content.trim();

    } catch (error) {
      console.error('OpenAI API Error:', error);
      // 폴백 응답
      return this.generateFallbackSummary(surveyData);
    }
  }

  /**
   * 설문 데이터를 기반으로 프롬프트 구성
   * @param {Object} surveyData - 설문 응답
   * @returns {string} 구성된 프롬프트
   */
  buildScreeningPrompt(surveyData) {
    const {
      symptoms = [],
      symptomDetails = '',
      painLevel = 0,
      workEnvironment = '',
      workHours = '',
      dailyHabits = '',
      name = '',
      contact = '',
      slackId = ''
    } = surveyData;

    return `
설문자 정보 분석 요청:

주요 증상: ${symptoms.join(', ')}
증상 상세: ${symptomDetails}
통증 강도: ${painLevel}/10
업무 환경: ${workEnvironment}
근무 시간: ${workHours}
생활 습관: ${dailyHabits}

위 정보를 바탕으로 재활의학적 관점에서 스크리닝 분석을 해주세요.
해부학적 구조와 운동학적 원리를 고려하여 현재 상태를 평가하고,
적절한 운동 접근법과 주의사항을 제시해주세요.`;
  }

  /**
   * GPT API 실패 시 폴백 응답 생성
   * @param {Object} surveyData - 설문 데이터
   * @returns {string} 폴백 스크리닝 요약
   */
  generateFallbackSummary(surveyData) {
    const { symptoms = [], painLevel = 0, workEnvironment = '' } = surveyData;
    
    let summary = '';
    
    if (symptoms.includes('거북목')) {
      summary += '경추 전방머리자세(Forward Head Posture)로 인한 상부 경추 신전 및 하부 경추 굴곡 패턴이 관찰됩니다. ';
    }
    
    if (symptoms.includes('라운드숄더')) {
      summary += '견갑골 전인 및 상방회전으로 인한 흉소근 단축과 중부승모근, 능형근 약화가 예상됩니다. ';
    }
    
    if (symptoms.includes('허리통증')) {
      summary += '요추 전만 감소 또는 증가로 인한 척주기립근과 고관절굴곡근의 불균형이 의심됩니다. ';
    }
    
    if (symptoms.includes('손목통증')) {
      summary += '반복적인 수근관절 신전 동작으로 인한 수근관증후군 가능성과 전완근 과사용이 관찰됩니다. ';
    }
    
    summary += `현재 통증 강도 ${painLevel}/10으로 `;
    
    if (painLevel <= 3) {
      summary += '경미한 수준입니다. ';
    } else if (painLevel <= 6) {
      summary += '중등도 수준입니다. ';
    } else {
      summary += '높은 수준으로 주의가 필요합니다. ';
    }
    
    summary += '\n\n**추천 접근법**: 점진적 스트레칭과 자세 교정 운동을 통한 근육 균형 회복\n';
    summary += '**주의사항**: 급성 통증 시 운동 중단, 의료진 상담 권장';
    
    return summary;
  }

  /**
   * 운동 추천 이유 생성
   * @param {Object} videoData - 영상 데이터
   * @param {Array} userSymptoms - 사용자 증상
   * @returns {Promise<string>} 추천 이유
   */
  async generateRecommendationReason(videoData, userSymptoms) {
    try {
      const completion = await this.openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: "운동치료 전문가로서 왜 이 운동이 해당 증상에 도움이 되는지 간단명료하게 설명해주세요. 1-2문장으로 작성하고, 해부학적 근거를 포함해주세요."
          },
          {
            role: "user",
            content: `사용자 증상: ${userSymptoms.join(', ')}\n운동 영상: ${videoData.title}\n\n이 운동이 해당 증상에 도움이 되는 이유를 설명해주세요.`
          }
        ],
        max_tokens: 150,
        temperature: 0.6
      });

      return completion.choices[0].message.content.trim();

    } catch (error) {
      console.error('OpenAI Recommendation Error:', error);
      return `${videoData.title}은(는) ${userSymptoms.join(', ')} 증상 완화에 도움이 되는 운동입니다.`;
    }
  }
}

module.exports = OpenAIService;