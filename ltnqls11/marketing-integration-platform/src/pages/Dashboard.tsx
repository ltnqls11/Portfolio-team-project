import React, { useEffect, useState } from 'react';
import PowerBloggerExplorer from '../components/PowerBloggerExplorer';
import ReviewCrawler from '../components/ReviewCrawler';
import ContentGenerator from '../components/ContentGenerator';
import BloggerOutreach from '../components/BloggerOutreach';
import { getCampaigns } from '../services/api';
import { Campaign, PowerBlogger, ReviewData, BlogCategory } from '../types';

interface DashboardStats {
  activeCampaigns: number;
  totalBloggers: number;
  sentEmails: number;
  generatedContent: number;
}

const Dashboard: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedBloggers, setSelectedBloggers] = useState<PowerBlogger[]>([]);
  const [reviews, setReviews] = useState<ReviewData[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'bloggers' | 'reviews' | 'content' | 'outreach'>('overview');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [stats, setStats] = useState<DashboardStats>({
    activeCampaigns: 0,
    totalBloggers: 0,
    sentEmails: 0,
    generatedContent: 0
  });
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const campaignsData = await getCampaigns();
      setCampaigns(campaignsData);

      setStats({
        activeCampaigns: campaignsData.filter(c => c.status === 'active').length,
        totalBloggers: selectedBloggers.length,
        sentEmails: 0, // 실제 API에서 가져와야 함
        generatedContent: 0 // 실제 API에서 가져와야 함
      });
    } catch (error) {
      console.error('대시보드 데이터 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNewCampaign = () => {
    // 새 캠페인 생성 로직
    const newCampaign: Campaign = {
      id: Date.now().toString(),
      clientId: 'default-client',
      title: '새 마케팅 캠페인',
      objective: '브랜드 인지도 향상 및 매출 증대',
      budget: 1000000,
      startAt: new Date(),
      endAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30일 후
      channels: ['naver_blog'],
      keywords: [],
      referenceUrls: [],
      status: 'draft',
      targetCategory: 'beauty',
      crawlingKeywords: []
    };
    
    setCampaigns(prev => [newCampaign, ...prev]);
    setSelectedCampaign(newCampaign);
    setActiveTab('bloggers');
  };

  const tabs = [
    { id: 'overview', label: '개요', icon: '📊' },
    { id: 'bloggers', label: '파워블로거', icon: '👥' },
    { id: 'reviews', label: '후기 크롤링', icon: '🔍' },
    { id: 'content', label: '콘텐츠 생성', icon: '✍️' },
    { id: 'outreach', label: '블로거 컨택', icon: '📧' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="loading-spinner"></div>
        <span className="ml-3 text-lg">로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">네이버 블로그 마케팅 자동화 플랫폼</h1>
              <p className="text-gray-600 mt-1">체험단 후기 기반 파워블로거 대행 서비스</p>
            </div>
            <button
              onClick={handleCreateNewCampaign}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              + 새 캠페인 생성
            </button>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex space-x-8">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* 통계 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-2xl">📈</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">활성 캠페인</h3>
                    <p className="text-2xl font-bold text-gray-900">{stats.activeCampaigns}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-2xl">👥</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">선택된 블로거</h3>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalBloggers}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <span className="text-2xl">📧</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">발송된 이메일</h3>
                    <p className="text-2xl font-bold text-gray-900">{stats.sentEmails}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <span className="text-2xl">✍️</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">생성된 콘텐츠</h3>
                    <p className="text-2xl font-bold text-gray-900">{stats.generatedContent}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 캠페인 목록 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">최근 캠페인</h2>
              </div>
              <div className="p-6">
                {campaigns.length === 0 ? (
                  <div className="text-center py-12">
                    <span className="text-6xl mb-4 block">🚀</span>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">첫 번째 캠페인을 시작해보세요!</h3>
                    <p className="text-gray-600 mb-6">파워블로거를 찾고, 후기를 분석하여 자동으로 마케팅 콘텐츠를 생성합니다.</p>
                    <button
                      onClick={handleCreateNewCampaign}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      캠페인 생성하기
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {campaigns.map(campaign => (
                      <div
                        key={campaign.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 cursor-pointer"
                        onClick={() => {
                          setSelectedCampaign(campaign);
                          setActiveTab('bloggers');
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-gray-900">{campaign.title}</h3>
                            <p className="text-sm text-gray-600 mt-1">{campaign.objective}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                              <span>예산: ₩{campaign.budget.toLocaleString()}</span>
                              <span>카테고리: {campaign.targetCategory}</span>
                              <span>키워드: {campaign.keywords.length}개</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                              campaign.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {campaign.status === 'active' ? '진행중' :
                               campaign.status === 'draft' ? '초안' : '완료'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'bloggers' && (
          <PowerBloggerExplorer
            onSelectBloggers={setSelectedBloggers}
            selectedCategory={selectedCampaign?.targetCategory}
          />
        )}

        {activeTab === 'reviews' && selectedCampaign && (
          <ReviewCrawler
            campaignId={selectedCampaign.id}
            category={selectedCampaign.targetCategory}
            onReviewsUpdate={setReviews}
          />
        )}

        {activeTab === 'content' && selectedCampaign && (
          <ContentGenerator
            campaignId={selectedCampaign.id}
            reviews={reviews}
          />
        )}

        {activeTab === 'outreach' && selectedCampaign && (
          <BloggerOutreach
            campaignId={selectedCampaign.id}
            selectedBloggers={selectedBloggers}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;