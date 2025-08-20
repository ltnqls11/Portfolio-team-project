// 제품 카테고리 타입
export type ProductCategory = 
  | '화장품' 
  | '리빙제품' 
  | '청소기' 
  | '커피머신' 
  | '패션' 
  | '전자제품' 
  | '식품' 
  | '건강식품';

// 블로거/인플루언서 타입
export interface Influencer {
  id: string;
  name: string;
  email: string;
  socialMedia: {
    instagram?: string;
    youtube?: string;
    blog?: string;
  };
  categories: ProductCategory[];
  followers: number;
  engagementRate: number;
  lastUpload: Date;
  averageViews: number;
  averageLikes: number;
  averageComments: number;
  contactStatus: '대기' | '전송' | '회신' | '수락' | '거절';
  price: number;
  description: string;
  profileImage: string;
}

// 블로그 글 타입
export interface BlogPost {
  id: string;
  title: string;
  content: string;
  author: string;
  authorId: string;
  category: ProductCategory;
  publishedDate: Date;
  views: number;
  likes: number;
  comments: number;
  tags: string[];
  url: string;
  performance: {
    clicks: number;
    conversions: number;
    revenue: number;
  };
}

// 홍보 문구 템플릿 타입
export interface PromotionTemplate {
  id: string;
  name: string;
  channel: 'instagram' | 'youtube' | 'blog' | 'facebook' | 'twitter';
  category: ProductCategory;
  tone: '친근한' | '전문적인' | '유머러스한' | '감성적인' | '정보성';
  structure: {
    title: string;
    subtitle: string;
    keywordRepetition: number;
    cta: string;
    hashtags: string[];
    length: '짧음' | '보통' | '길음';
  };
  content: string;
}

// 캠페인 타입
export interface Campaign {
  id: string;
  name: string;
  productName: string;
  category: ProductCategory;
  description: string;
  budget: number;
  startDate: Date;
  endDate: Date;
  status: '준비중' | '진행중' | '완료' | '중단';
  influencers: CampaignInfluencer[];
  templates: PromotionTemplate[];
  performance: CampaignPerformance;
}

// 캠페인 인플루언서 타입
export interface CampaignInfluencer {
  influencerId: string;
  influencer: Influencer;
  assignedTemplate: PromotionTemplate;
  status: '선택됨' | '연락됨' | '수락' | '거절' | '완료';
  sentDate?: Date;
  responseDate?: Date;
  deliveryLink?: string;
  screenshots?: string[];
  performance: {
    views: number;
    clicks: number;
    conversions: number;
    revenue: number;
    comments: number;
    likes: number;
  };
}

// 캠페인 성과 타입
export interface CampaignPerformance {
  totalViews: number;
  totalClicks: number;
  totalConversions: number;
  totalRevenue: number;
  totalCost: number;
  roi: number;
  ctr: number;
  conversionRate: number;
  topPerformers: CampaignInfluencer[];
}

// 자동 생성된 홍보 문구 타입
export interface GeneratedPromotion {
  id: string;
  templateId: string;
  influencerId: string;
  content: string;
  channel: string;
  generatedDate: Date;
  status: '생성됨' | '검토됨' | '승인됨' | '발송됨';
  performance?: {
    views: number;
    clicks: number;
    conversions: number;
  };
}

// 필터 옵션 타입
export interface FilterOptions {
  categories: ProductCategory[];
  minFollowers: number;
  maxFollowers: number;
  minEngagementRate: number;
  maxEngagementRate: number;
  contactStatus: string[];
  priceRange: [number, number];
} 

// 기존 타입은 유지하되, 네이버 블로거 추천 타입 추가
export interface BloggerRecommendation {
	id: string;
	name: string;
	blogUrl: string;
	authorId?: string;
	score: number; // AI 또는 규칙 기반 점수
	estimatedReach?: number;
	engagementScore?: number; // 댓글/공감 등 추정
	lastUpload?: Date;
	recentPost?: {
		title: string;
		url: string;
		publishedAt?: Date;
		tags?: string[];
	};
	contact?: {
		email?: string;
		social?: string;
	};
}

export interface NaverBlogPostSpec {
	productQuery: string; // 제품명/키워드
	tone: '친근한' | '전문적인' | '유머러스한' | '감성적인' | '정보성';
	length: '짧음' | '보통' | '길음';
	keywords: string[];
	hashtags?: string[];
	cta: string;
	includeSubheadings: boolean; // 소제목 포함 여부
}

export interface GeneratedNaverBlogPost {
	id: string;
	content: string; // 최종 본문 (마크다운/텍스트)
	outline: string[]; // 생성된 소제목 목록
	keywords: string[];
	hashtags: string[];
	cta: string;
	generatedAt: Date;
} 