import axios from 'axios';
import { 
  Campaign, 
  PowerBlogger,
  ReviewData,
  GeneratedContent,
  BloggerOutreach,
  BlogCategory,
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

// 파워블로거 관련 API
export const getPowerBloggers = async (filters?: {
  category?: BlogCategory;
  minSubscribers?: number;
  maxSubscribers?: number;
  minEngagementRate?: number;
}): Promise<PowerBlogger[]> => {
  const response = await axios.get(`${API_BASE_URL}/power-bloggers`, { params: filters });
  return response.data;
};

export const getPowerBlogger = async (bloggerId: string): Promise<PowerBlogger> => {
  const response = await axios.get(`${API_BASE_URL}/power-bloggers/${bloggerId}`);
  return response.data;
};

export const crawlBloggerData = async (blogUrl: string): Promise<PowerBlogger> => {
  const response = await axios.post(`${API_BASE_URL}/crawl/blogger`, { blogUrl });
  return response.data;
};

// 체험단 후기 크롤링 API
export const crawlReviews = async (keywords: string[], category: BlogCategory): Promise<ReviewData[]> => {
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
  contentType: 'blog_post' | 'sns_post' | 'email_template';
  basedOnReviews: string[];
  tone: string;
  targetAudience: string;
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

// 결과물 관련 API
export const getDeliverables = async (campaignId: string): Promise<Deliverable[]> => {
  const response = await axios.get(`${API_BASE_URL}/campaigns/${campaignId}/deliverables`);
  return response.data;
};

export const createDeliverable = async (deliverableData: Omit<Deliverable, 'id'>): Promise<Deliverable> => {
  const response = await axios.post(`${API_BASE_URL}/deliverables`, deliverableData);
  return response.data;
};

// 클라이언트 관련 API
export const getClients = async (): Promise<Client[]> => {
  const response = await axios.get(`${API_BASE_URL}/clients`);
  return response.data;
};

export const createClient = async (clientData: Omit<Client, 'id' | 'createdAt'>): Promise<Client> => {
  const response = await axios.post(`${API_BASE_URL}/clients`, clientData);
  return response.data;
};