import { Influencer, ProductCategory, FilterOptions, BlogPost } from '../types';
import { mockInfluencers, mockBlogPosts } from '../data/mockData';

// 인플루언서 추천 서비스
export class InfluencerRecommender {
  
  // 카테고리 기반 인플루언서 추천
  static recommendByCategory(
    category: ProductCategory,
    options: {
      minFollowers?: number;
      maxFollowers?: number;
      minEngagementRate?: number;
      maxPrice?: number;
      limit?: number;
    } = {}
  ): Influencer[] {
    const {
      minFollowers = 0,
      maxFollowers = Infinity,
      minEngagementRate = 0,
      maxPrice = Infinity,
      limit = 10
    } = options;
    
    // 카테고리 매칭 및 필터링
    let recommendations = mockInfluencers.filter(influencer => {
      const categoryMatch = influencer.categories.includes(category);
      const followerMatch = influencer.followers >= minFollowers && influencer.followers <= maxFollowers;
      const engagementMatch = influencer.engagementRate >= minEngagementRate;
      const priceMatch = influencer.price <= maxPrice;
      
      return categoryMatch && followerMatch && engagementMatch && priceMatch;
    });
    
    // 성과 점수 계산 및 정렬
    recommendations = recommendations.map(influencer => ({
      ...influencer,
      score: this.calculatePerformanceScore(influencer, category)
    }));
    
    // 점수 기준 내림차순 정렬
    recommendations.sort((a, b) => (b as any).score - (a as any).score);
    
    return recommendations.slice(0, limit);
  }
  
  // 성과 점수 계산
  static calculatePerformanceScore(influencer: Influencer, category: ProductCategory): number {
    let score = 0;
    
    // 팔로워 수 점수 (30%)
    const followerScore = Math.min(influencer.followers / 100000, 1) * 30;
    score += followerScore;
    
    // 참여율 점수 (25%)
    const engagementScore = Math.min(influencer.engagementRate / 10, 1) * 25;
    score += engagementScore;
    
    // 평균 조회수 점수 (20%)
    const viewScore = Math.min(influencer.averageViews / 50000, 1) * 20;
    score += viewScore;
    
    // 최근 업로드 점수 (15%)
    const daysSinceLastUpload = (Date.now() - influencer.lastUpload.getTime()) / (1000 * 60 * 60 * 24);
    const recencyScore = Math.max(0, (30 - daysSinceLastUpload) / 30) * 15;
    score += recencyScore;
    
    // 카테고리 전문성 점수 (10%)
    const categoryExpertise = influencer.categories.length === 1 ? 10 : 5;
    score += categoryExpertise;
    
    return Math.round(score);
  }
  
  // 블로그 글 성과 기반 추천
  static recommendByBlogPerformance(
    category: ProductCategory,
    options: {
      minViews?: number;
      minLikes?: number;
      minConversions?: number;
      limit?: number;
    } = {}
  ): Influencer[] {
    const {
      minViews = 0,
      minLikes = 0,
      minConversions = 0,
      limit = 10
    } = options;
    
    // 해당 카테고리의 블로그 글 필터링
    const categoryPosts = mockBlogPosts.filter(post => post.category === category);
    
    // 성과 기준 필터링
    const highPerformancePosts = categoryPosts.filter(post => 
      post.views >= minViews &&
      post.likes >= minLikes &&
      post.performance.conversions >= minConversions
    );
    
    // 인플루언서별 성과 집계
    const influencerPerformance = new Map<string, {
      influencer: Influencer;
      totalViews: number;
      totalLikes: number;
      totalConversions: number;
      postCount: number;
      averagePerformance: number;
    }>();
    
    highPerformancePosts.forEach(post => {
      const influencer = mockInfluencers.find(inf => inf.id === post.authorId);
      if (!influencer) return;
      
      const existing = influencerPerformance.get(influencer.id);
      if (existing) {
        existing.totalViews += post.views;
        existing.totalLikes += post.likes;
        existing.totalConversions += post.performance.conversions;
        existing.postCount += 1;
        existing.averagePerformance = (existing.totalViews + existing.totalLikes * 10 + existing.totalConversions * 100) / existing.postCount;
      } else {
        influencerPerformance.set(influencer.id, {
          influencer,
          totalViews: post.views,
          totalLikes: post.likes,
          totalConversions: post.performance.conversions,
          postCount: 1,
          averagePerformance: post.views + post.likes * 10 + post.performance.conversions * 100
        });
      }
    });
    
    // 성과 기준 정렬
    const recommendations = Array.from(influencerPerformance.values())
      .sort((a, b) => b.averagePerformance - a.averagePerformance)
      .slice(0, limit)
      .map(item => item.influencer);
    
    return recommendations;
  }

  // 제품명/키워드 기반 추천 (로컬 폴백)
  static recommendByProductQuery(
    query: string,
    options: { limit?: number } = {}
  ): Influencer[] {
    const limit = options.limit ?? 10;
    const category = this.inferCategoryFromQuery(query);

    // 1) 해당 쿼리와 유사한 블로그 글의 저자 우선
    const q = query.toLowerCase();
    const matchedPosts = mockBlogPosts.filter(p =>
      p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q) || p.tags.some(t => t.toLowerCase().includes(q))
    );

    const byPosts = new Map<string, { influencer: Influencer; weight: number }>();
    matchedPosts.forEach(p => {
      const inf = mockInfluencers.find(i => i.id === p.authorId);
      if (!inf) return;
      const w = p.views + p.likes * 10 + p.performance.conversions * 100;
      const prev = byPosts.get(inf.id)?.weight ?? 0;
      byPosts.set(inf.id, { influencer: inf, weight: prev + w });
    });

    // 2) 카테고리 추천과 병합
    const byCategory = this.recommendByCategory(category, { limit: 20 });
    byCategory.forEach(inf => {
      const base = (byPosts.get(inf.id)?.weight ?? 0);
      byPosts.set(inf.id, { influencer: inf, weight: base + this.calculatePerformanceScore(inf, category) * 1000 });
    });

    return Array.from(byPosts.values())
      .sort((a, b) => b.weight - a.weight)
      .slice(0, limit)
      .map(v => v.influencer);
  }

  // 쿼리에서 카테고리 추론 (간단 키워드 매핑)
  static inferCategoryFromQuery(query: string): ProductCategory {
    const q = query.toLowerCase();
    const map: Array<{ keys: string[]; cat: ProductCategory }> = [
      { keys: ['립스틱','파운데이션','스킨케어','에센스','토너','화장품','쿠션','마스카라','뷰티'], cat: '화장품' },
      { keys: ['수납','정리','리빙','홈데코','인테리어'], cat: '리빙제품' },
      { keys: ['무선청소기','로봇청소기','청소기','흡입력'], cat: '청소기' },
      { keys: ['에스프레소','커피머신','캡슐커피','그라인더','라떼'], cat: '커피머신' },
      { keys: ['스니커즈','셔츠','재킷','패션','가방'], cat: '패션' },
      { keys: ['노트북','스마트폰','이어폰','전자제품','가전','테크'], cat: '전자제품' },
      { keys: ['간편식','라면','과자','식품','간식'], cat: '식품' },
      { keys: ['단백질','비타민','오메가','건강','영양제','프로틴'], cat: '건강식품' },
    ];

    for (const m of map) {
      if (m.keys.some(k => q.includes(k))) return m.cat;
    }
    return '전자제품';
  }
  
  // 예산 기반 추천
  static recommendByBudget(
    budget: number,
    category: ProductCategory,
    options: {
      minInfluencers?: number;
      maxInfluencers?: number;
    } = {}
  ): {
    influencers: Influencer[];
    totalCost: number;
    estimatedReach: number;
    estimatedEngagement: number;
  } {
    const { minInfluencers = 3, maxInfluencers = 10 } = options;
    
    // 카테고리 매칭 인플루언서 필터링
    const categoryInfluencers = mockInfluencers.filter(inf => 
      inf.categories.includes(category)
    );
    
    // 예산 내에서 최적 조합 찾기
    const sortedInfluencers = categoryInfluencers
      .map(inf => ({
        ...inf,
        valueScore: this.calculateValueScore(inf)
      }))
      .sort((a, b) => (b as any).valueScore - (a as any).valueScore);
    
    let currentCost = 0;
    const selectedInfluencers: Influencer[] = [];
    
    for (const influencer of sortedInfluencers) {
      if (currentCost + influencer.price <= budget && 
          selectedInfluencers.length < maxInfluencers) {
        selectedInfluencers.push(influencer);
        currentCost += influencer.price;
      }
    }
    
    // 최소 인플루언서 수 확인 및 보충
    if (selectedInfluencers.length < minInfluencers) {
      const remainingBudget = budget - currentCost;
      const affordableInfluencers = categoryInfluencers
        .filter(inf => !selectedInfluencers.find(selected => selected.id === inf.id))
        .filter(inf => inf.price <= remainingBudget)
        .sort((a, b) => a.price - b.price);
      
      for (const influencer of affordableInfluencers) {
        if (selectedInfluencers.length >= minInfluencers) break;
        if (currentCost + influencer.price <= budget) {
          selectedInfluencers.push(influencer);
          currentCost += influencer.price;
        }
      }
    }
    
    const totalReach = selectedInfluencers.reduce((sum, inf) => sum + inf.followers, 0);
    const avgEngagement = selectedInfluencers.reduce((sum, inf) => sum + inf.engagementRate, 0) / Math.max(1, selectedInfluencers.length);
    const estimatedEngagement = totalReach * (avgEngagement / 100);
    
    return {
      influencers: selectedInfluencers,
      totalCost: currentCost,
      estimatedReach: totalReach,
      estimatedEngagement: Math.round(estimatedEngagement)
    };
  }
  
  // 가치 점수 계산 (성과 대비 가격)
  static calculateValueScore(influencer: Influencer): number {
    const performanceScore = this.calculatePerformanceScore(influencer, influencer.categories[0]);
    return performanceScore / (influencer.price / 100000); // 10만원 단위로 정규화
  }
  
  // 필터 옵션 적용
  static applyFilters(influencers: Influencer[], filters: FilterOptions): Influencer[] {
    return influencers.filter(influencer => {
      if (filters.categories.length > 0 && 
          !filters.categories.some(cat => influencer.categories.includes(cat))) {
        return false;
      }
      if (influencer.followers < filters.minFollowers || 
          influencer.followers > filters.maxFollowers) {
        return false;
      }
      if (influencer.engagementRate < filters.minEngagementRate || 
          influencer.engagementRate > filters.maxEngagementRate) {
        return false;
      }
      if (filters.contactStatus.length > 0 && 
          !filters.contactStatus.includes(influencer.contactStatus)) {
        return false;
      }
      if (influencer.price < filters.priceRange[0] || 
          influencer.price > filters.priceRange[1]) {
        return false;
      }
      return true;
    });
  }
} 