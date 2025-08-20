import { PromotionTemplate, GeneratedPromotion, ProductCategory } from '../types';

// 홍보 문구 자동 생성 서비스
export class PromotionGenerator {
  
  // 템플릿 기반 홍보 문구 생성
  static generateFromTemplate(
    template: PromotionTemplate,
    productInfo: {
      name: string;
      category: ProductCategory;
      features: string[];
      benefits: string[];
      price: number;
      discount?: number;
      url: string;
    },
    influencerInfo: {
      name: string;
      tone: string;
    }
  ): GeneratedPromotion {
    
    let content = template.content;
    
    // 제품 정보로 템플릿 변수 치환
    content = content.replace(/{제품명}/g, productInfo.name);
    content = content.replace(/{장점1}/g, productInfo.features[0] || '뛰어난 품질');
    content = content.replace(/{장점2}/g, productInfo.features[1] || '합리적인 가격');
    content = content.replace(/{장점3}/g, productInfo.features[2] || '편리한 사용법');
    content = content.replace(/{효과}/g, productInfo.benefits[0] || '만족도');
    
    // 성능 점수 (랜덤 생성)
    content = content.replace(/{흡입력점수}/g, Math.floor(Math.random() * 3) + 8 + '');
    content = content.replace(/{소음점수}/g, Math.floor(Math.random() * 3) + 7 + '');
    content = content.replace(/{배터리점수}/g, Math.floor(Math.random() * 3) + 8 + '');
    content = content.replace(/{편의성점수}/g, Math.floor(Math.random() * 3) + 8 + '');
    
    // 커피머신 관련 정보
    content = content.replace(/{추출방식}/g, '에스프레소');
    content = content.replace(/{용량}/g, '1.5L');
    content = content.replace(/{가격대}/g, '20-30만원');
    content = content.replace(/{관리난이도}/g, '보통');
    
    // CTA 및 해시태그
    content = content.replace(/{CTA}/g, template.structure.cta);
    content = content.replace(/{해시태그}/g, template.structure.hashtags.join(' '));
    
    // 인플루언서 톤에 맞게 조정
    if (influencerInfo.tone === '친근한') {
      content = content.replace(/안녕하세요!/g, '안녕하세요 여러분! 😊');
    } else if (influencerInfo.tone === '전문적인') {
      content = content.replace(/안녕하세요!/g, '안녕하세요. 오늘은');
    }
    
    // 할인 정보 추가
    if (productInfo.discount) {
      const discountText = `\n\n🔥 특별 할인: ${productInfo.discount}% 할인 중!\n원가: ${productInfo.price.toLocaleString()}원 → 할인가: ${(productInfo.price * (1 - productInfo.discount / 100)).toLocaleString()}원`;
      content = content.replace(/\n\n{CTA}/, discountText + '\n\n{CTA}');
    }
    
    // 링크 추가
    content = content.replace(/{CTA}/g, `${template.structure.cta}\n${productInfo.url}`);
    
    return {
      id: `gen_${Date.now()}`,
      templateId: template.id,
      influencerId: 'temp',
      content: content,
      channel: template.channel,
      generatedDate: new Date(),
      status: '생성됨'
    };
  }
  
  // 카테고리별 키워드 추천
  static getCategoryKeywords(category: ProductCategory): string[] {
    const keywordMap: Record<ProductCategory, string[]> = {
      '화장품': ['뷰티', '스킨케어', '메이크업', '안티에이징', '모이스처', '선케어'],
      '리빙제품': ['인테리어', '정리정돈', '홈데코', '수납', '가구', '조명'],
      '청소기': ['청소', '진공청소기', '로봇청소기', '무선청소기', '흡입력', '배터리'],
      '커피머신': ['커피', '에스프레소', '드립', '바리스타', '원두', '추출'],
      '패션': ['스타일', '코디', '트렌드', '패션', '의류', '신발'],
      '전자제품': ['테크', '가전', '스마트홈', 'IoT', '디지털', '기술'],
      '식품': ['요리', '레시피', '맛집', '음식', '재료', '조리법'],
      '건강식품': ['건강', '영양', '다이어트', '보조식품', '비타민', '프로틴']
    };
    
    return keywordMap[category] || [];
  }
  
  // 해시태그 자동 생성
  static generateHashtags(category: ProductCategory, productName: string): string[] {
    const categoryKeywords = this.getCategoryKeywords(category);
    const productKeywords = productName.split(' ').filter(word => word.length > 1);
    
    const hashtags = [
      ...categoryKeywords.map(keyword => `#${keyword}`),
      ...productKeywords.map(keyword => `#${keyword}`),
      '#추천',
      '#리뷰',
      '#인플루언서'
    ];
    
    return hashtags.slice(0, 8); // 최대 8개 해시태그
  }
  
  // 톤별 문구 스타일 조정
  static adjustTone(content: string, tone: string): string {
    switch (tone) {
      case '친근한':
        return content
          .replace(/입니다/g, '이에요')
          .replace(/합니다/g, '해요')
          .replace(/습니다/g, '어요');
      case '전문적인':
        return content
          .replace(/이에요/g, '입니다')
          .replace(/해요/g, '합니다')
          .replace(/어요/g, '습니다');
      case '유머러스한':
        return content + '\n\n😄 재미있게 읽어주셨나요?';
      case '감성적인':
        return content + '\n\n💕 여러분의 일상에 작은 행복을 더해드리고 싶어요.';
      case '정보성':
        return content + '\n\n📚 더 자세한 정보는 링크를 확인해주세요.';
      default:
        return content;
    }
  }
  
  // 채널별 최적화
  static optimizeForChannel(content: string, channel: string): string {
    switch (channel) {
      case 'instagram':
        // 인스타그램은 이모지와 해시태그가 중요
        return content + '\n\n' + '💫✨🌟';
      case 'youtube':
        // 유튜브는 설명이 중요
        return content + '\n\n영상에서 더 자세한 내용을 확인하세요!';
      case 'blog':
        // 블로그는 상세한 정보
        return content + '\n\n더 자세한 리뷰는 블로그에서 확인하세요.';
      case 'facebook':
        // 페이스북은 커뮤니티 느낌
        return content + '\n\n여러분의 생각은 어떠신가요? 댓글로 의견을 남겨주세요!';
      case 'twitter':
        // 트위터는 간결함
        return content.substring(0, 200) + (content.length > 200 ? '...' : '');
      default:
        return content;
    }
  }
} 