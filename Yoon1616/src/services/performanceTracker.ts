import { Campaign, CampaignInfluencer, CampaignPerformance, BlogPost } from '../types';

// 성과 관리 서비스
export class PerformanceTracker {
  
  // 캠페인 성과 계산
  static calculateCampaignPerformance(
    campaign: Campaign,
    campaignInfluencers: CampaignInfluencer[]
  ): CampaignPerformance {
    const totalViews = campaignInfluencers.reduce((sum, ci) => sum + ci.performance.views, 0);
    const totalClicks = campaignInfluencers.reduce((sum, ci) => sum + ci.performance.clicks, 0);
    const totalConversions = campaignInfluencers.reduce((sum, ci) => sum + ci.performance.conversions, 0);
    const totalRevenue = campaignInfluencers.reduce((sum, ci) => sum + ci.performance.revenue, 0);
    const totalCost = campaignInfluencers.reduce((sum, ci) => sum + ci.influencer.price, 0);
    
    const roi = totalCost > 0 ? ((totalRevenue - totalCost) / totalCost) * 100 : 0;
    const ctr = totalViews > 0 ? (totalClicks / totalViews) * 100 : 0;
    const conversionRate = totalClicks > 0 ? (totalConversions / totalClicks) * 100 : 0;
    
    // 상위 성과자 선별
    const topPerformers = campaignInfluencers
      .filter(ci => ci.performance.views > 0)
      .sort((a, b) => {
        const aScore = a.performance.views + a.performance.clicks * 10 + a.performance.conversions * 100;
        const bScore = b.performance.views + b.performance.clicks * 10 + b.performance.conversions * 100;
        return bScore - aScore;
      })
      .slice(0, 5);
    
    return {
      totalViews,
      totalClicks,
      totalConversions,
      totalRevenue,
      totalCost,
      roi: Math.round(roi * 100) / 100,
      ctr: Math.round(ctr * 100) / 100,
      conversionRate: Math.round(conversionRate * 100) / 100,
      topPerformers
    };
  }
  
  // 인플루언서별 성과 업데이트
  static updateInfluencerPerformance(
    influencerId: string,
    performance: {
      views: number;
      clicks: number;
      conversions: number;
      revenue: number;
      comments: number;
      likes: number;
    },
    campaignInfluencers: CampaignInfluencer[]
  ): CampaignInfluencer[] {
    return campaignInfluencers.map(ci => {
      if (ci.influencerId === influencerId) {
        return {
          ...ci,
          performance: {
            ...ci.performance,
            ...performance
          }
        };
      }
      return ci;
    });
  }
  
  // 성과 데이터 수집 (시뮬레이션)
  static async collectPerformanceData(
    campaignInfluencer: CampaignInfluencer
  ): Promise<{
    views: number;
    clicks: number;
    conversions: number;
    revenue: number;
    comments: number;
    likes: number;
  }> {
    // 실제 구현에서는 각 플랫폼의 API를 통해 데이터 수집
    return new Promise((resolve) => {
      setTimeout(() => {
        const baseViews = campaignInfluencer.influencer.averageViews;
        const baseLikes = campaignInfluencer.influencer.averageLikes;
        const baseComments = campaignInfluencer.influencer.averageComments;
        
        // 랜덤 변동성 추가 (실제 데이터와 유사하게)
        const views = Math.round(baseViews * (0.8 + Math.random() * 0.4));
        const likes = Math.round(baseLikes * (0.7 + Math.random() * 0.6));
        const comments = Math.round(baseComments * (0.6 + Math.random() * 0.8));
        
        // 클릭률과 전환률 계산
        const ctr = 0.02 + Math.random() * 0.03; // 2-5%
        const conversionRate = 0.01 + Math.random() * 0.02; // 1-3%
        
        const clicks = Math.round(views * ctr);
        const conversions = Math.round(clicks * conversionRate);
        
        // 수익 계산 (평균 주문 가치 50,000원 가정)
        const averageOrderValue = 50000;
        const revenue = conversions * averageOrderValue;
        
        resolve({
          views,
          clicks,
          conversions,
          revenue,
          comments,
          likes
        });
      }, 2000);
    });
  }
  
  // 성과 리포트 생성
  static generatePerformanceReport(
    campaign: Campaign,
    performance: CampaignPerformance
  ): {
    summary: string;
    insights: string[];
    recommendations: string[];
    charts: Array<{
      type: 'bar' | 'line' | 'pie';
      title: string;
      data: any;
    }>;
  } {
    const summary = `
캠페인 성과 요약:
• 총 노출: ${performance.totalViews.toLocaleString()}회
• 총 클릭: ${performance.totalClicks.toLocaleString()}회
• 총 전환: ${performance.totalConversions.toLocaleString()}건
• 총 수익: ${performance.totalRevenue.toLocaleString()}원
• 총 비용: ${performance.totalCost.toLocaleString()}원
• ROI: ${performance.roi}%
• CTR: ${performance.ctr}%
• 전환율: ${performance.conversionRate}%
    `.trim();
    
    const insights: string[] = [];
    
    if (performance.roi > 200) {
      insights.push('매우 높은 ROI를 달성했습니다!');
    } else if (performance.roi > 100) {
      insights.push('양호한 ROI를 달성했습니다.');
    } else if (performance.roi > 0) {
      insights.push('수익을 창출했지만 개선 여지가 있습니다.');
    } else {
      insights.push('ROI가 음수입니다. 전략 재검토가 필요합니다.');
    }
    
    if (performance.ctr > 3) {
      insights.push('높은 클릭률을 보여주고 있습니다.');
    } else if (performance.ctr < 1) {
      insights.push('클릭률이 낮습니다. 콘텐츠 개선이 필요합니다.');
    }
    
    if (performance.conversionRate > 2) {
      insights.push('전환율이 우수합니다.');
    } else if (performance.conversionRate < 0.5) {
      insights.push('전환율이 낮습니다. 랜딩페이지 최적화가 필요합니다.');
    }
    
    const recommendations: string[] = [];
    
    if (performance.topPerformers.length > 0) {
      recommendations.push('상위 성과자와의 지속적인 협업을 권장합니다.');
    }
    
    if (performance.ctr < 2) {
      recommendations.push('콘텐츠 품질과 호기심을 자극하는 제목 개선이 필요합니다.');
    }
    
    if (performance.conversionRate < 1) {
      recommendations.push('랜딩페이지 UX 개선 및 CTA 최적화가 필요합니다.');
    }
    
    // 차트 데이터 생성
    const charts = [
      {
        type: 'bar' as const,
        title: '인플루언서별 성과 비교',
        data: performance.topPerformers.map(ci => ({
          name: ci.influencer.name,
          views: ci.performance.views,
          clicks: ci.performance.clicks,
          conversions: ci.performance.conversions
        }))
      },
      {
        type: 'line' as const,
        title: '일별 성과 추이',
        data: this.generateDailyPerformanceData()
      },
      {
        type: 'pie' as const,
        title: '캠페인 비용 대비 수익 분포',
        data: [
          { name: '비용', value: performance.totalCost },
          { name: '순익', value: Math.max(0, performance.totalRevenue - performance.totalCost) }
        ]
      }
    ];
    
    return {
      summary,
      insights,
      recommendations,
      charts
    };
  }
  
  // 일별 성과 데이터 생성 (시뮬레이션)
  private static generateDailyPerformanceData(): Array<{
    date: string;
    views: number;
    clicks: number;
    conversions: number;
  }> {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    for (let i = 0; i < 30; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      
      const baseViews = 1000 + Math.random() * 2000;
      const ctr = 0.02 + Math.random() * 0.03;
      const conversionRate = 0.01 + Math.random() * 0.02;
      
      data.push({
        date: date.toISOString().split('T')[0],
        views: Math.round(baseViews),
        clicks: Math.round(baseViews * ctr),
        conversions: Math.round(baseViews * ctr * conversionRate)
      });
    }
    
    return data;
  }
  
  // 키워드 순위 추적
  static async trackKeywordRankings(
    keywords: string[],
    productUrl: string
  ): Promise<Array<{
    keyword: string;
    rank: number;
    change: number;
    searchVolume: number;
  }>> {
    // 실제 구현에서는 SEO 도구 API 사용
    return new Promise((resolve) => {
      setTimeout(() => {
        const results = keywords.map(keyword => ({
          keyword,
          rank: Math.floor(Math.random() * 50) + 1,
          change: Math.floor(Math.random() * 10) - 5,
          searchVolume: Math.floor(Math.random() * 10000) + 1000
        }));
        
        resolve(results);
      }, 1000);
    });
  }
  
  // 경쟁사 분석
  static async analyzeCompetitors(
    productCategory: string,
    competitors: string[]
  ): Promise<Array<{
    competitor: string;
    marketShare: number;
    socialMediaPresence: number;
    influencerCollaborations: number;
    estimatedBudget: number;
  }>> {
    // 실제 구현에서는 시장 조사 도구 API 사용
    return new Promise((resolve) => {
      setTimeout(() => {
        const results = competitors.map(competitor => ({
          competitor,
          marketShare: Math.random() * 30,
          socialMediaPresence: Math.floor(Math.random() * 1000000) + 100000,
          influencerCollaborations: Math.floor(Math.random() * 100) + 10,
          estimatedBudget: Math.floor(Math.random() * 10000000) + 1000000
        }));
        
        resolve(results);
      }, 1500);
    });
  }
  
  // 성과 예측
  static predictPerformance(
    historicalData: Array<{
      views: number;
      clicks: number;
      conversions: number;
      revenue: number;
    }>,
    budget: number,
    influencerCount: number
  ): {
    predictedViews: number;
    predictedClicks: number;
    predictedConversions: number;
    predictedRevenue: number;
    confidence: number;
  } {
    // 간단한 선형 회귀 기반 예측
    const avgViews = historicalData.reduce((sum, d) => sum + d.views, 0) / historicalData.length;
    const avgCtr = historicalData.reduce((sum, d) => sum + (d.clicks / d.views), 0) / historicalData.length;
    const avgConversionRate = historicalData.reduce((sum, d) => sum + (d.conversions / d.clicks), 0) / historicalData.length;
    const avgRevenuePerConversion = historicalData.reduce((sum, d) => sum + (d.revenue / d.conversions), 0) / historicalData.length;
    
    const predictedViews = avgViews * influencerCount * (budget / 1000000); // 예산 비례
    const predictedClicks = predictedViews * avgCtr;
    const predictedConversions = predictedClicks * avgConversionRate;
    const predictedRevenue = predictedConversions * avgRevenuePerConversion;
    
    // 신뢰도 계산 (데이터 양과 변동성 기반)
    const confidence = Math.min(0.95, 0.5 + (historicalData.length * 0.05));
    
    return {
      predictedViews: Math.round(predictedViews),
      predictedClicks: Math.round(predictedClicks),
      predictedConversions: Math.round(predictedConversions),
      predictedRevenue: Math.round(predictedRevenue),
      confidence: Math.round(confidence * 100) / 100
    };
  }
} 