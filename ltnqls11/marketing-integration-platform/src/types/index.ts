// 클라이언트 (광고주)
export interface Client {
  id: string;
  name: string;
  industry: string;
  contactEmail: string;
  createdAt: Date;
}

// 캠페인
export interface Campaign {
  id: string;
  clientId: string;
  title: string;
  objective: string;
  budget: number;
  startAt: Date;
  endAt: Date;
  channels: string[];
  keywords: string[];
  referenceUrls: string[];
  status: 'draft' | 'active' | 'paused' | 'completed';
  targetCategory: string;
  crawlingKeywords: string[];
}

// 채널 정보
export interface Channel {
  id: string;
  name: string;
  platform: 'instagram' | 'youtube' | 'tiktok' | 'naver' | 'facebook' | 'twitter';
  description: string;
  audience: number;
  engagement: number;
  costPerPost: number;
  demographics: {
    age: string;
    gender: string;
  };
  categories: string[];
  icon: string;
}

// 블로그 카테고리
export type BlogCategory = 
  | 'beauty' | 'fashion' | 'food' | 'travel' | 'lifestyle' 
  | 'tech' | 'health' | 'parenting' | 'home' | 'pet' 
  | 'book' | 'movie' | 'game' | 'finance' | 'education';

// 인플루언서 정보
export interface Influencer {
  id: string;
  name: string;
  username: string;
  platform: 'instagram' | 'youtube' | 'tiktok' | 'naver' | 'facebook' | 'twitter';
  followers: number;
  engagement: number;
  category: string;
  bio: string;
  avatar: string;
  verified: boolean;
  costPerPost: number;
  recentPosts: number;
  avgLikes: number;
  avgComments: number;
  demographics: {
    age: string;
    gender: string;
  };
  tags: string[];
  contactEmail?: string;
  lastActive?: Date;
}

// 블로그 포스트
export interface BlogPost {
  id: string;
  title: string;
  url: string;
  content: string;
  publishedAt: Date;
  views: number;
  likes: number;
  comments: number;
  category: string;
  tags: string[];
  isSponsored: boolean;
}

// 크롤링된 체험단 후기
export interface ReviewData {
  id: string;
  productName: string;
  blogUrl: string;
  bloggerName: string;
  title: string;
  content: string;
  rating: number;
  pros: string[];
  cons: string[];
  images: string[];
  publishedAt: Date;
  category: BlogCategory;
  sentiment: 'positive' | 'negative' | 'neutral';
  keywords: string[];
}

// 자동 생성된 마케팅 콘텐츠
export interface GeneratedContent {
  id: string;
  campaignId: string;
  influencerId?: string;
  contentType: 'instagram_post' | 'youtube_script' | 'tiktok_video' | 'blog_post';
  title: string;
  content: string;
  hashtags?: string[];
  targetAudience: string;
  tone: 'professional' | 'casual' | 'friendly' | 'trendy';
  generatedAt: Date;
  status: 'draft' | 'approved' | 'published';
}

// 블로거 컨택 정보
export interface BloggerOutreach {
  id: string;
  campaignId: string;
  bloggerId: string;
  contactMethod: 'email' | 'blog_message' | 'sns_dm';
  subject: string;
  message: string;
  proposedRate: number;
  sentAt: Date;
  status: 'sent' | 'opened' | 'replied' | 'accepted' | 'rejected';
  response?: string;
  responseAt?: Date;
}

// 문구 변형
export interface CopyVariant {
  id: string;
  campaignId: string;
  channel: Channel;
  tone: string;
  length: number;
  text: string;
  score: number;
  approved: boolean;
  createdAt: Date;
}

// 크리에이터 (인플루언서)
export interface Creator {
  id: string;
  platform: string;
  handle: string;
  category: string;
  followers: number;
  engagementRate: number;
  email?: string;
  dmUrl?: string;
  activeAt: Date;
  notes?: string;
}

// 아웃리치 (연락)
export interface Outreach {
  id: string;
  campaignId: string;
  creatorId: string;
  channel: Channel;
  method: 'email' | 'dm';
  status: 'pending' | 'sent' | 'replied' | 'accepted' | 'rejected';
  lastEventAt: Date;
  messageTemplateId?: string;
}

// 결과물
export interface Deliverable {
  id: string;
  campaignId: string;
  creatorId: string;
  url: string;
  postedAt: Date;
  metrics: {
    views?: number;
    likes?: number;
    comments?: number;
    shares?: number;
    clicks?: number;
  };
}

// 이벤트 로그
export interface Event {
  id: string;
  type: string;
  payload: Record<string, any>;
  createdAt: Date;
}

// 문구 생성 요청
export interface CopyGenerationRequest {
  productDescription: string;
  benefits: string[];
  target: {
    age: string;
    interests: string[];
  };
  keywords: string[];
  referenceLinks?: string[];
  channel: Channel;
}

// 문구 생성 응답
export interface CopyGenerationResponse {
  variants: {
    title?: string;
    content: string;
    hashtags?: string[];
    cta?: string;
    length: number;
    score: number;
  }[];
}