import React, { useState } from 'react';
import { Campaign, Influencer, Channel } from '../types';

interface CampaignManagerProps {
  campaigns: Campaign[];
  onCampaignUpdate: (campaigns: Campaign[]) => void;
  selectedInfluencers: Influencer[];
  selectedChannels: Channel[];
}

const CampaignManager: React.FC<CampaignManagerProps> = ({
  campaigns,
  onCampaignUpdate,
  selectedInfluencers,
  selectedChannels
}) => {
  const [activeView, setActiveView] = useState<'list' | 'create' | 'analytics'>('list');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [newCampaign, setNewCampaign] = useState({
    title: '',
    objective: '',
    budget: 0,
    targetCategory: 'beauty',
    startDate: '',
    endDate: '',
    description: ''
  });

  const handleCreateCampaign = () => {
    const campaign: Campaign = {
      id: Date.now().toString(),
      clientId: 'default-client',
      title: newCampaign.title,
      objective: newCampaign.objective,
      budget: newCampaign.budget,
      startAt: new Date(newCampaign.startDate),
      endAt: new Date(newCampaign.endDate),
      channels: selectedChannels.map(c => c.platform),
      keywords: [],
      referenceUrls: [],
      status: 'draft',
      targetCategory: newCampaign.targetCategory,
      crawlingKeywords: []
    };

    onCampaignUpdate([campaign, ...campaigns]);
    setNewCampaign({
      title: '',
      objective: '',
      budget: 0,
      targetCategory: 'beauty',
      startDate: '',
      endDate: '',
      description: ''
    });
    setActiveView('list');
  };

  const handleStatusChange = (campaignId: string, newStatus: string) => {
    const updatedCampaigns = campaigns.map(campaign =>
      campaign.id === campaignId ? { ...campaign, status: newStatus as 'draft' | 'active' | 'paused' | 'completed' } : campaign
    );
    onCampaignUpdate(updatedCampaigns);
  };

  const getCampaignProgress = (campaign: Campaign) => {
    const now = new Date();
    const start = new Date(campaign.startAt);
    const end = new Date(campaign.endAt);
    
    if (now < start) return 0;
    if (now > end) return 100;
    
    const total = end.getTime() - start.getTime();
    const elapsed = now.getTime() - start.getTime();
    return Math.round((elapsed / total) * 100);
  };

  if (activeView === 'create') {
    return (
      <div className="space-y-6">
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">새 캠페인 생성</h2>
                <p className="text-white/80 text-sm mt-1">마케팅 캠페인의 세부 정보를 입력하세요</p>
              </div>
              <button
                onClick={() => setActiveView('list')}
                className="btn-secondary"
              >
                ← 목록으로
              </button>
            </div>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  캠페인 제목
                </label>
                <input
                  type="text"
                  value={newCampaign.title}
                  onChange={(e) => setNewCampaign({...newCampaign, title: e.target.value})}
                  className="form-input"
                  placeholder="예: 신제품 런칭 캠페인"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  카테고리
                </label>
                <select
                  value={newCampaign.targetCategory}
                  onChange={(e) => setNewCampaign({...newCampaign, targetCategory: e.target.value})}
                  className="form-select"
                >
                  <option value="beauty">뷰티</option>
                  <option value="fashion">패션</option>
                  <option value="tech">기술</option>
                  <option value="food">음식</option>
                  <option value="lifestyle">라이프스타일</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  캠페인 목표
                </label>
                <textarea
                  value={newCampaign.objective}
                  onChange={(e) => setNewCampaign({...newCampaign, objective: e.target.value})}
                  className="form-textarea h-24"
                  placeholder="예: 브랜드 인지도 향상 및 신제품 홍보를 통한 매출 증대"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  예산 (원)
                </label>
                <input
                  type="number"
                  value={newCampaign.budget}
                  onChange={(e) => setNewCampaign({...newCampaign, budget: Number(e.target.value)})}
                  className="form-input"
                  placeholder="5000000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  시작일
                </label>
                <input
                  type="date"
                  value={newCampaign.startDate}
                  onChange={(e) => setNewCampaign({...newCampaign, startDate: e.target.value})}
                  className="form-input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  종료일
                </label>
                <input
                  type="date"
                  value={newCampaign.endDate}
                  onChange={(e) => setNewCampaign({...newCampaign, endDate: e.target.value})}
                  className="form-input"
                />
              </div>
            </div>

            {selectedChannels.length > 0 && (
              <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                <h3 className="font-medium text-gray-900 mb-2">선택된 채널</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedChannels.map(channel => (
                    <span
                      key={channel.id}
                      className="px-3 py-1 bg-blue-500 text-white rounded-full text-sm"
                    >
                      {channel.icon} {channel.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedInfluencers.length > 0 && (
              <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
                <h3 className="font-medium text-gray-900 mb-2">선택된 인플루언서</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedInfluencers.map(influencer => (
                    <span
                      key={influencer.id}
                      className="px-3 py-1 bg-purple-500 text-white rounded-full text-sm"
                    >
                      {influencer.avatar} {influencer.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setActiveView('list')}
                className="btn-secondary"
              >
                취소
              </button>
              <button
                onClick={handleCreateCampaign}
                className="btn-primary"
                disabled={!newCampaign.title || !newCampaign.objective}
              >
                캠페인 생성
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">캠페인 관리</h2>
              <p className="text-white/80 text-sm mt-1">마케팅 캠페인을 생성하고 관리하세요</p>
            </div>
            <button
              onClick={() => setActiveView('create')}
              className="btn-primary"
            >
              <span className="mr-2">✨</span>
              새 캠페인 생성
            </button>
          </div>
        </div>
      </div>

      {/* 캠페인 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body text-center">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-2xl font-bold text-purple-600">{campaigns.length}</div>
            <div className="text-sm text-gray-600">총 캠페인</div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body text-center">
            <div className="text-3xl mb-2">🚀</div>
            <div className="text-2xl font-bold text-green-600">
              {campaigns.filter(c => c.status === 'active').length}
            </div>
            <div className="text-sm text-gray-600">활성 캠페인</div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body text-center">
            <div className="text-3xl mb-2">💰</div>
            <div className="text-2xl font-bold text-blue-600">
              ₩{campaigns.reduce((sum, c) => sum + c.budget, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">총 예산</div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body text-center">
            <div className="text-3xl mb-2">✅</div>
            <div className="text-2xl font-bold text-orange-600">
              {campaigns.filter(c => c.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600">완료된 캠페인</div>
          </div>
        </div>
      </div>

      {/* 캠페인 목록 */}
      <div className="space-y-4">
        {campaigns.map(campaign => {
          const progress = getCampaignProgress(campaign);
          
          return (
            <div key={campaign.id} className="card">
              <div className="card-body">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-1">{campaign.title}</h3>
                    <p className="text-gray-600 mb-3">{campaign.objective}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">예산:</span>
                        <div className="font-medium">₩{campaign.budget.toLocaleString()}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">카테고리:</span>
                        <div className="font-medium">{campaign.targetCategory}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">시작일:</span>
                        <div className="font-medium">{new Date(campaign.startAt).toLocaleDateString()}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">종료일:</span>
                        <div className="font-medium">{new Date(campaign.endAt).toLocaleDateString()}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <select
                      value={campaign.status}
                      onChange={(e) => handleStatusChange(campaign.id, e.target.value)}
                      className={`px-3 py-1 rounded-full text-sm font-medium border-0 ${
                        campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                        campaign.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                        campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}
                    >
                      <option value="draft">초안</option>
                      <option value="active">활성</option>
                      <option value="paused">일시정지</option>
                      <option value="completed">완료</option>
                    </select>
                  </div>
                </div>
                
                {/* 진행률 바 */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>캠페인 진행률</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
                
                {/* 채널 정보 */}
                <div className="flex flex-wrap gap-2">
                  {campaign.channels.map(channel => (
                    <span
                      key={channel}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                    >
                      {channel}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {campaigns.length === 0 && (
        <div className="text-center py-16">
          <span className="text-8xl mb-6 block">🎯</span>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">캠페인이 없습니다</h3>
          <p className="text-gray-600 mb-8 text-lg">첫 번째 마케팅 캠페인을 생성해보세요!</p>
          <button
            onClick={() => setActiveView('create')}
            className="btn-primary text-lg px-8 py-4"
          >
            <span className="mr-2">✨</span>
            캠페인 생성하기
          </button>
        </div>
      )}
    </div>
  );
};

export default CampaignManager;