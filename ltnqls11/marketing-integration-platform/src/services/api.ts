import axios from 'axios';
import { 
  Campaign, 
  Influencer,
  ReviewData,
  GeneratedContent,
  BloggerOutreach,
  Client 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// 캠페인 관련 API
export const getCampaigns = async (): Promise<Campaign[]> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns`);
  return response.data;
};

export const createCampaign = async (campaignData: Omit<Campaign, 'id'>): Promise<Campaign> => {
  const response = await axios.post(`${API_BASE_URL}/campaigns`, campaignData);
  return response.data;
};

export const updateCampaign = async (campaignId: string, campaignData: Partial<Campaign>): Promise<Campaign> => {
  const response = await axios.put(`${API_BASE_URL}/campaigns/${campaignId}`, campaignData);
  return response.data;
};

export const getCampaign = async (campaignId: string): Promise<Campaign> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}`);
  return response.data;
};

// 인플루언서 관련 API
export const getInfluencers = async (filters?: {
  category?: string;
  platform?: string;
  minFollowers?: number;
  maxFollowers?: number;
  minEngagementRate?: number;
}): Promise<Influencer[]> => {
  const response = await axios.get(`${API_BASE_URL}/influencers`, { params: filters });
  return response.data;
};

export const getInfluencer = async (influencerId: string): Promise<Influencer> => {
  const response = await axios.get(`${API_BASE_URL}/influencers/${influencerId}`);
  return response.data;
};

export const crawlInfluencerData = async (profileUrl: string): Promise<Influencer> => {
  const response = await axios.post(`${API_BASE_URL}/crawl/influencer`, { profileUrl });
  return response.data;
};

// 체험단 후기 크롤링 API
export const crawlReviews = async (keywords: string[], category: string): Promise<ReviewData[]> => {
  const response = await axios.post(`${API_BASE_URL}/crawl/reviews`, { keywords, category });
  return response.data;
};

export const getReviews = async (campaignId: string): Promise<ReviewData[]> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}/reviews`);
  return response.data;
};

// 콘텐츠 자동 생성 API
export const generateContent = async (request: {
  campaignId: string;
  contentType: 'naver_blog_post' | 'blogspot_post' | 'tistory_post' | 'kakao_channel_post' | 'instagram_post';
  tone: string;
  targetAudience: string;
  productName: string;
  keyMessage: string;
  callToAction: string;
  influencerId?: string;
  influencerStyle?: string[];
  platform?: string;
}): Promise<GeneratedContent> => {
  const response = await axios.post(`${API_BASE_URL}/content/generate`, request);
  return response.data;
};

export const getGeneratedContent = async (campaignId: string): Promise<GeneratedContent[]> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}/content`);
  return response.data;
};

export const approveContent = async (contentId: string): Promise<GeneratedContent> => {
  const response = await axios.patch(`${API_BASE_URL}/content/${contentId}/approve`);
  return response.data;
};

// 블로거 컨택 관련 API
export const createBloggerOutreach = async (outreachData: Omit<BloggerOutreach, 'id' | 'sentAt'>): Promise<BloggerOutreach> => {
  const response = await axios.post(`${API_BASE_URL}/blogger-outreach`, outreachData);
  return response.data;
};

export const getBloggerOutreach = async (campaignId: string): Promise<BloggerOutreach[]> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}/blogger-outreach`);
  return response.data;
};

export const sendBulkEmails = async (campaignId: string, bloggerIds: string[], template: string): Promise<{ sent: number; failed: number }> => {
  const response = await axios.post(`${API_BASE_URL}/blogger-outreach/bulk-send`, {
    campaignId,
    bloggerIds,
    template
  });
  return response.data;
};

export const updateOutreachStatus = async (outreachId: string, status: BloggerOutreach['status'], response?: string): Promise<BloggerOutreach> => {
  const response_data = await axios.patch(`${API_BASE_URL}/blogger-outreach/${outreachId}/status`, { 
    status, 
    response 
  });
  return response_data.data;
};

// 결과물 관련 API (추후 구현)
// export const getDeliverables = async (campaignId: string) => {
//   const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}/deliverables`);
//   return response.data;
// };

// 클라이언트 관련 API
export const getClients = async (): Promise<Client[]> => {
  const response = await axios.get(`${API_BASE_URL}/clients`);
  return response.data;
};

export const createClient = async (clientData: Omit<Client, 'id' | 'createdAt'>): Promise<Client> => {
  const response = await axios.post(`${API_BASE_URL}/clients`, clientData);
  return response.data;
};