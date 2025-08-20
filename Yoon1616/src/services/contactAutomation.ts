import { Influencer, CampaignInfluencer, GeneratedPromotion } from '../types';

// 연락 자동화 서비스
export class ContactAutomation {
  
  // 이메일 템플릿 생성
  static generateEmailTemplate(
    influencer: Influencer,
    campaign: {
      name: string;
      productName: string;
      description: string;
      budget: number;
    },
    promotion: GeneratedPromotion
  ): string {
    const template = `
안녕하세요, ${influencer.name}님!

저는 ${campaign.name} 캠페인을 담당하고 있는 마케팅 매니저입니다.

${campaign.productName}에 대한 협업을 제안드리고 싶습니다.

📋 캠페인 정보:
- 제품: ${campaign.productName}
- 설명: ${campaign.description}
- 예산: ${campaign.budget.toLocaleString()}원
- 기간: 협의 가능

💡 제안 내용:
${promotion.content}

🤝 협업 조건:
- 협의 가능한 가격
- 자유로운 콘텐츠 제작
- 성과에 따른 추가 보상

관심이 있으시면 답장 부탁드립니다.
더 자세한 내용은 언제든 연락주세요!

감사합니다.
    `.trim();
    
    return template;
  }
  
  // DM 템플릿 생성
  static generateDMTemplate(
    influencer: Influencer,
    campaign: {
      name: string;
      productName: string;
      description: string;
    },
    promotion: GeneratedPromotion
  ): string {
    const template = `
안녕하세요! ${influencer.name}님 😊

${campaign.productName} 협업 제안드려요!

${promotion.content.substring(0, 200)}...

더 자세한 내용은 이메일로 보내드릴까요?
관심 있으시면 답장 부탁드려요! 💕
    `.trim();
    
    return template;
  }
  
  // 연락 상태 업데이트
  static updateContactStatus(
    influencerId: string,
    status: '대기' | '전송' | '회신' | '수락' | '거절',
    campaignInfluencers: CampaignInfluencer[]
  ): CampaignInfluencer[] {
    return campaignInfluencers.map(ci => {
      if (ci.influencerId === influencerId) {
        return {
          ...ci,
          status,
          sentDate: status === '전송' ? new Date() : ci.sentDate,
          responseDate: status === '회신' || status === '수락' || status === '거절' ? new Date() : ci.responseDate
        };
      }
      return ci;
    });
  }
  
  // 자동 메일 발송 (시뮬레이션)
  static async sendEmail(
    influencer: Influencer,
    emailContent: string
  ): Promise<{ success: boolean; messageId?: string; error?: string }> {
    // 실제 구현에서는 이메일 서비스 API 사용
    return new Promise((resolve) => {
      setTimeout(() => {
        // 90% 성공률로 시뮬레이션
        const success = Math.random() > 0.1;
        if (success) {
          resolve({
            success: true,
            messageId: `email_${Date.now()}_${influencer.id}`
          });
        } else {
          resolve({
            success: false,
            error: '이메일 발송 실패'
          });
        }
      }, 1000);
    });
  }
  
  // 자동 DM 발송 (시뮬레이션)
  static async sendDM(
    influencer: Influencer,
    dmContent: string,
    platform: 'instagram' | 'youtube' | 'twitter'
  ): Promise<{ success: boolean; messageId?: string; error?: string }> {
    // 실제 구현에서는 소셜미디어 API 사용
    return new Promise((resolve) => {
      setTimeout(() => {
        // 85% 성공률로 시뮬레이션
        const success = Math.random() > 0.15;
        if (success) {
          resolve({
            success: true,
            messageId: `dm_${platform}_${Date.now()}_${influencer.id}`
          });
        } else {
          resolve({
            success: false,
            error: `${platform} DM 발송 실패`
          });
        }
      }, 1500);
    });
  }
  
  // 대량 연락 발송
  static async sendBulkContacts(
    influencers: Influencer[],
    campaign: {
      name: string;
      productName: string;
      description: string;
      budget: number;
    },
    promotion: GeneratedPromotion,
    contactMethod: 'email' | 'dm' | 'both'
  ): Promise<{
    success: number;
    failed: number;
    results: Array<{
      influencerId: string;
      method: string;
      success: boolean;
      messageId?: string;
      error?: string;
    }>;
  }> {
    const results: Array<{
      influencerId: string;
      method: string;
      success: boolean;
      messageId?: string;
      error?: string;
    }> = [];
    
    let successCount = 0;
    let failedCount = 0;
    
    for (const influencer of influencers) {
      if (contactMethod === 'email' || contactMethod === 'both') {
        const emailContent = this.generateEmailTemplate(influencer, campaign, promotion);
        const emailResult = await this.sendEmail(influencer, emailContent);
        
        results.push({
          influencerId: influencer.id,
          method: 'email',
          success: emailResult.success,
          messageId: emailResult.messageId,
          error: emailResult.error
        });
        
        if (emailResult.success) {
          successCount++;
        } else {
          failedCount++;
        }
      }
      
      if (contactMethod === 'dm' || contactMethod === 'both') {
        const dmContent = this.generateDMTemplate(influencer, campaign, promotion);
        const dmResult = await this.sendDM(influencer, dmContent, 'instagram');
        
        results.push({
          influencerId: influencer.id,
          method: 'dm',
          success: dmResult.success,
          messageId: dmResult.messageId,
          error: dmResult.error
        });
        
        if (dmResult.success) {
          successCount++;
        } else {
          failedCount++;
        }
      }
      
      // 요청 간격 조절 (API 제한 방지)
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    return {
      success: successCount,
      failed: failedCount,
      results
    };
  }
  
  // 연락 추적 및 알림
  static trackContactStatus(
    campaignInfluencers: CampaignInfluencer[]
  ): {
    pending: CampaignInfluencer[];
    responded: CampaignInfluencer[];
    accepted: CampaignInfluencer[];
    rejected: CampaignInfluencer[];
    needsFollowUp: CampaignInfluencer[];
  } {
    const now = new Date();
    const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
    
    const pending = campaignInfluencers.filter(ci => ci.status === '전송');
    const responded = campaignInfluencers.filter(ci => ci.status === '회신');
    const accepted = campaignInfluencers.filter(ci => ci.status === '수락');
    const rejected = campaignInfluencers.filter(ci => ci.status === '거절');
    
    // 3일 이상 응답이 없는 경우 후속 조치 필요
    const needsFollowUp = campaignInfluencers.filter(ci => 
      ci.status === '전송' && 
      ci.sentDate && 
      ci.sentDate < threeDaysAgo
    );
    
    return {
      pending,
      responded,
      accepted,
      rejected,
      needsFollowUp
    };
  }
  
  // 자동 후속 연락 생성
  static generateFollowUpMessage(
    influencer: Influencer,
    originalMessage: string,
    daysSinceContact: number
  ): string {
    const templates = [
      `안녕하세요 ${influencer.name}님! 
      
이전에 보내드린 협업 제안에 대해 확인해보고 싶어서 연락드립니다.
혹시 메시지를 확인하셨나요? 

궁금한 점이나 추가로 필요한 정보가 있으시면 언제든 말씀해주세요! 😊`,
      
      `안녕하세요 ${influencer.name}님!
      
협업 제안에 대한 답변을 기다리고 있습니다.
혹시 다른 제안이나 조건이 있으시면 언제든 연락주세요!`,
      
      `안녕하세요 ${influencer.name}님!
      
협업 제안에 대한 마지막 확인 메시지입니다.
관심이 없으시다면 답변 없이도 괜찮습니다.
앞으로도 좋은 기회가 있으면 다시 연락드리겠습니다!`
    ];
    
    if (daysSinceContact <= 3) {
      return templates[0];
    } else if (daysSinceContact <= 7) {
      return templates[1];
    } else {
      return templates[2];
    }
  }
} 