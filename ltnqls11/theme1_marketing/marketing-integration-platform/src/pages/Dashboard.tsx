import React, { useEffect, useState } from 'react';
import ChannelExplorer from '../components/ChannelExplorer';
import InfluencerFinder from '../components/InfluencerFinder';
import ContentGenerator from '../components/ContentGenerator';
import CampaignManager from '../components/CampaignManager';
import { getCampaigns } from '../services/api';
import { Campaign, Influencer, Channel } from '../types';

interface DashboardStats {
  activeCampaigns: number;
  totalInfluencers: number;
  activeChannels: number;
  generatedContent: number;
  totalReach: number;
  engagementRate: number;
}

const Dashboard: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedInfluencers, setSelectedInfluencers] = useState<Influencer[]>([]);
  const [selectedChannels, setSelectedChannels] = useState<Channel[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'channels' | 'influencers' | 'content' | 'campaigns'>('overview');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [stats, setStats] = useState<DashboardStats>({
    activeCampaigns: 0,
    totalInfluencers: 0,
    activeChannels: 0,
    generatedContent: 0,
    totalReach: 0,
    engagementRate: 0
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
        totalInfluencers: selectedInfluencers.length,
        activeChannels: selectedChannels.length,
        generatedContent: 0, // 실제 API에서 가져와야 함
        totalReach: 1250000, // 예시 데이터
        engagementRate: 4.2 // 예시 데이터
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
      budget: 5000000,
      startAt: new Date(),
      endAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30일 후
      channels: ['naver_blog', 'blogspot', 'tistory', 'kakao_channel', 'instagram'],
      keywords: [],
      referenceUrls: [],
      status: 'draft',
      targetCategory: 'beauty',
      crawlingKeywords: []
    };
    
    setCampaigns(prev => [newCampaign, ...prev]);
    setSelectedCampaign(newCampaign);
    setActiveTab('channels');
  };

  const tabs = [
    { id: 'overview', label: '대시보드', icon: '📊' },
    { id: 'channels', label: '채널 관리', icon: '📱' },
    { id: 'influencers', label: '인플루언서', icon: '⭐' },
    { id: 'content', label: '콘텐츠 생성', icon: '✨' },
    { id: 'campaigns', label: '캠페인 관리', icon: '🚀' }
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
    <div className="min-h-screen">
      {/* 헤더 */}
      <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                마케팅 통합 플랫폼
              </h1>
              <p className="text-gray-600 mt-2 text-lg">기업이 채널/인플루언서를 고르고, 맞춤형 홍보 문구를 자동 생성·배포·관리하는 올인원 플랫폼</p>
            </div>
            <button
              onClick={handleCreateNewCampaign}
              className="btn-primary flex items-center gap-2"
            >
              <span>✨</span>
              새 캠페인 생성
            </button>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="bg-white/60 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex space-x-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-6 font-medium text-sm rounded-t-xl transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                    : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                }`}
              >
                <span className="mr-2 text-lg">{tab.icon}</span>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">활성 캠페인</h3>
                      <p className="text-3xl font-bold text-purple-600">{stats.activeCampaigns}</p>
                      <p className="text-xs text-green-600 mt-1">↗ +12% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl">
                      <span className="text-3xl">🚀</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">협력 인플루언서</h3>
                      <p className="text-3xl font-bold text-pink-600">{stats.totalInfluencers}</p>
                      <p className="text-xs text-green-600 mt-1">↗ +8% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-pink-100 to-orange-100 rounded-2xl">
                      <span className="text-3xl">⭐</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">활성 채널</h3>
                      <p className="text-3xl font-bold text-blue-600">{stats.activeChannels}</p>
                      <p className="text-xs text-green-600 mt-1">↗ +5% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl">
                      <span className="text-3xl">📱</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">총 도달률</h3>
                      <p className="text-3xl font-bold text-green-600">{stats.totalReach.toLocaleString()}</p>
                      <p className="text-xs text-green-600 mt-1">↗ +25% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-green-100 to-blue-100 rounded-2xl">
                      <span className="text-3xl">📊</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">참여율</h3>
                      <p className="text-3xl font-bold text-orange-600">{stats.engagementRate}%</p>
                      <p className="text-xs text-green-600 mt-1">↗ +0.8% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-orange-100 to-yellow-100 rounded-2xl">
                      <span className="text-3xl">💫</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-600 mb-1">생성된 콘텐츠</h3>
                      <p className="text-3xl font-bold text-indigo-600">{stats.generatedContent}</p>
                      <p className="text-xs text-green-600 mt-1">↗ +15% 이번 달</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl">
                      <span className="text-3xl">✨</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 캠페인 목록 */}
            <div className="card slide-up">
              <div className="card-header">
                <h2 className="text-xl font-bold text-white">최근 캠페인</h2>
                <p className="text-white/80 text-sm mt-1">진행 중인 마케팅 캠페인을 관리하세요</p>
              </div>
              <div className="card-body">
                {campaigns.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="mb-6">
                      <span className="text-8xl block mb-4">🎯</span>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">첫 번째 캠페인을 시작해보세요!</h3>
                    <p className="text-gray-600 mb-8 text-lg max-w-md mx-auto">
                      인플루언서를 찾고, 채널을 선택하여 자동으로 맞춤형 마케팅 콘텐츠를 생성합니다.
                    </p>
                    <button
                      onClick={handleCreateNewCampaign}
                      className="btn-primary text-lg px-8 py-4"
                    >
                      <span className="mr-2">✨</span>
                      캠페인 생성하기
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {campaigns.map(campaign => (
                      <div
                        key={campaign.id}
                        className="card campaign-card cursor-pointer"
                        onClick={() => {
                          setSelectedCampaign(campaign);
                          setActiveTab('channels');
                        }}
                      >
                        <div className="card-body">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-bold text-gray-900 mb-2">{campaign.title}</h3>
                              <p className="text-gray-600 mb-3">{campaign.objective}</p>
                              <div className="flex items-center gap-6 text-sm text-gray-500">
                                <span className="flex items-center gap-1">
                                  <span>💰</span>
                                  예산: ₩{campaign.budget.toLocaleString()}
                                </span>
                                <span className="flex items-center gap-1">
                                  <span>🎯</span>
                                  카테고리: {campaign.targetCategory}
                                </span>
                                <span className="flex items-center gap-1">
                                  <span>🔑</span>
                                  키워드: {campaign.keywords.length}개
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className={`status-badge ${
                                campaign.status === 'active' ? 'status-active' :
                                campaign.status === 'draft' ? 'status-draft' : 'status-completed'
                              }`}>
                                {campaign.status === 'active' ? '진행중' :
                                 campaign.status === 'draft' ? '초안' : '완료'}
                              </span>
                            </div>
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

        {activeTab === 'channels' && (
          <ChannelExplorer
            onSelectChannels={setSelectedChannels}
            selectedCategory={selectedCampaign?.targetCategory}
          />
        )}

        {activeTab === 'influencers' && (
          <InfluencerFinder
            onSelectInfluencers={setSelectedInfluencers}
            selectedChannels={selectedChannels}
            selectedCategory={selectedCampaign?.targetCategory}
          />
        )}

        {activeTab === 'content' && selectedCampaign && (
          <ContentGenerator
            campaignId={selectedCampaign.id}
            selectedInfluencers={selectedInfluencers}
            selectedChannels={selectedChannels}
          />
        )}

        {activeTab === 'campaigns' && (
          <CampaignManager
            campaigns={campaigns}
            onCampaignUpdate={setCampaigns}
            selectedInfluencers={selectedInfluencers}
            selectedChannels={selectedChannels}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;