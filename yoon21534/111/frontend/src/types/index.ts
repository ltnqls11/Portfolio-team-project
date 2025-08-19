// 클라이언트 타입
export interface Client {
  id: number
  name: string
  email: string
  company?: string
  created_at: string
  updated_at: string
}

// 캠페인 타입
export interface Campaign {
  id: number
  name: string
  description?: string
  product_info?: string
  keywords?: string
  reference_links?: string
  status: 'draft' | 'active' | 'completed'
  client_id: number
  created_at: string
  updated_at: string
}

// 문구 변형 타입
export interface CopyVariant {
  id: number
  channel: 'naver_blog' | 'instagram_feed'
  content: string
  is_selected: boolean
  campaign_id: number
  created_at: string
}

// 크리에이터 타입
export interface Creator {
  id: number
  name: string
  email?: string
  platform: 'instagram' | 'youtube' | 'blog'
  username?: string
  followers_count?: number
  engagement_rate?: number
  category?: string
  contact_info?: Record<string, any>
  profile_data?: Record<string, any>
  created_at: string
  updated_at: string
}

// 연락 기록 타입
export interface OutreachRecord {
  id: number
  campaign_id: number
  creator_id: number
  email_subject?: string
  email_content?: string
  status: 'pending' | 'sent' | 'failed' | 'replied'
  sent_at?: string
  error_message?: string
  response_data?: Record<string, any>
  created_at: string
  updated_at: string
}

// API 응답 타입
export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}