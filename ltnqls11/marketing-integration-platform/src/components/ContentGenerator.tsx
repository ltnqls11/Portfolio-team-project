import React, { useState, useEffect } from 'react';
import { GeneratedContent, Influencer, Channel } from '../types';
import { generateContent, getGeneratedContent, approveContent } from '../services/api';

interface ContentGeneratorProps {
  campaignId: string;
  selectedInfluencers: Influencer[];
  selectedChannels: Channel[];
}

const ContentGenerator: React.FC<ContentGeneratorProps> = ({ 
  campaignId, 
  selectedInfluencers, 
  selectedChannels 
}) => {
  const [contents, setContents] = useState<GeneratedContent[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedInfluencerIds, setSelectedInfluencerIds] = useState<string[]>([]);
  const [contentSettings, setContentSettings] = useState({
    contentType: 'instagram_post' as 'instagram_post' | 'youtube_script' | 'tiktok_video' | 'blog_post',
    tone: 'friendly' as 'professional' | 'casual' | 'friendly' | 'trendy',
    targetAudience: '20-30대 여성',
    productName: '',
    keyMessage: '',
    callToAction: ''
  });

  useEffect(() => {
    fetchGeneratedContent();
  }, [campaignId]);

  const fetchGeneratedContent = async () => {
    try {
      const data = await getGeneratedContent(campaignId);
      setContents(data);
    } catch (error) {
      console.error('생성된 콘텐츠 조회 실패:', error);
    }
  };

  const handleGenerate = async () => {
    if (selectedInfluencerIds.length === 0) {
      alert('콘텐츠를 생성할 인플루언서를 선택해주세요.');
      return;
    }

    if (!contentSettings.productName || !contentSettings.keyMessage) {
      alert('제품명과 핵심 메시지를 입력해주세요.');
      return;
    }

    setGenerating(true);
    try {
      // 선택된 인플루언서별로 맞춤형 콘텐츠 생성
      const newContents = await Promise.all(
        selectedInfluencerIds.map(async (influencerId) => {
          const influencer = selectedInfluencers.find(i => i.id === influencerId);
          return await generateContent({
            campaignId,
            ...contentSettings,
            influencerId,
            influencerStyle: influencer?.tags || [],
            platform: influencer?.platform || 'instagram'
          });
        })
      );
      
      setContents(prev => [...newContents, ...prev]);
      alert(`${newContents.length}개의 맞춤형 콘텐츠가 생성되었습니다!`);
    } catch (error) {
      console.error('콘텐츠 생성 실패:', error);
      alert('콘텐츠 생성에 실패했습니다.');
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async (contentId: string) => {
    try {
      const approvedContent = await approveContent(contentId);
      setContents(prev => 
        prev.map(content => 
          content.id === contentId ? approvedContent : content
        )
      );
    } catch (error) {
      console.error('콘텐츠 승인 실패:', error);
      alert('콘텐츠 승인에 실패했습니다.');
    }
  };

  const getContentTypeText = (type: GeneratedContent['contentType']) => {
    switch (type) {
      case 'instagram_post': return 'Instagram 포스트';
      case 'youtube_script': return 'YouTube 스크립트';
      case 'tiktok_video': return 'TikTok 비디오';
      case 'blog_post': return '블로그 포스트';
    }
  };

  const getToneText = (tone: GeneratedContent['tone']) => {
    switch (tone) {
      case 'professional': return '전문적';
      case 'casual': return '캐주얼';
      case 'friendly': return '친근한';
      case 'trendy': return '트렌디';
    }
  };

  const getStatusColor = (status: GeneratedContent['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'published': return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusText = (status: GeneratedContent['status']) => {
    switch (status) {
      case 'draft': return '초안';
      case 'approved': return '승인됨';
      case 'published': return '발행됨';
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-bold text-white">AI 맞춤형 콘텐츠 생성기</h2>
          <p className="text-white/80 text-sm mt-1">인플루언서별 맞춤형 홍보 콘텐츠를 자동 생성합니다</p>
        </div>
        <div className="card-body">
          {/* 기본 설정 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">제품명</label>
              <input
                type="text"
                value={contentSettings.productName}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  productName: e.target.value
                })}
                className="form-input"
                placeholder="예: 프리미엄 비타민 C 세럼"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">콘텐츠 타입</label>
              <select
                value={contentSettings.contentType}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  contentType: e.target.value as any
                })}
                className="form-select"
              >
                <option value="instagram_post">Instagram 포스트</option>
                <option value="youtube_script">YouTube 스크립트</option>
                <option value="tiktok_video">TikTok 비디오</option>
                <option value="blog_post">블로그 포스트</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">톤앤매너</label>
              <select
                value={contentSettings.tone}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  tone: e.target.value as any
                })}
                className="form-select"
              >
                <option value="professional">전문적</option>
                <option value="casual">캐주얼</option>
                <option value="friendly">친근한</option>
                <option value="trendy">트렌디</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">타겟 고객</label>
              <input
                type="text"
                value={contentSettings.targetAudience}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  targetAudience: e.target.value
                })}
                className="form-input"
                placeholder="예: 20-30대 여성"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">핵심 메시지</label>
              <textarea
                value={contentSettings.keyMessage}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  keyMessage: e.target.value
                })}
                className="form-textarea h-24"
                placeholder="예: 피부 트러블 개선과 브라이트닝 효과"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">행동 유도 문구</label>
              <textarea
                value={contentSettings.callToAction}
                onChange={(e) => setContentSettings({
                  ...contentSettings, 
                  callToAction: e.target.value
                })}
                className="form-textarea h-24"
                placeholder="예: 지금 구매하면 30% 할인!"
              />
            </div>
          </div>

          {/* 인플루언서 선택 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              콘텐츠를 생성할 인플루언서 선택 ({selectedInfluencerIds.length}/{selectedInfluencers.length})
            </label>
            {selectedInfluencers.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-xl">
                <span className="text-4xl mb-2 block">👥</span>
                <p className="text-gray-600">먼저 인플루언서 탭에서 인플루언서를 선택해주세요.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-60 overflow-y-auto">
                {selectedInfluencers.map(influencer => (
                  <label key={influencer.id} className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl cursor-pointer hover:bg-gray-50">
                    <input
                      type="checkbox"
                      checked={selectedInfluencerIds.includes(influencer.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedInfluencerIds(prev => [...prev, influencer.id]);
                        } else {
                          setSelectedInfluencerIds(prev => prev.filter(id => id !== influencer.id));
                        }
                      }}
                    />
                    <div className="text-2xl">{influencer.avatar}</div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{influencer.name}</p>
                      <p className="text-sm text-gray-600">{influencer.username}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{influencer.followers.toLocaleString()} 팔로워</span>
                        <span>•</span>
                        <span>{influencer.engagement}% 참여율</span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || selectedInfluencerIds.length === 0 || !contentSettings.productName || !contentSettings.keyMessage}
            className="btn-primary w-full py-4 text-lg"
          >
            {generating ? (
              <div className="flex items-center justify-center gap-2">
                <div className="loading-spinner w-5 h-5"></div>
                AI가 맞춤형 콘텐츠를 생성하고 있습니다...
              </div>
            ) : (
              <div className="flex items-center justify-center gap-2">
                <span>✨</span>
                {selectedInfluencerIds.length}명의 인플루언서용 콘텐츠 생성하기
              </div>
            )}
          </button>
        </div>
      </div>

      {/* 생성된 콘텐츠 목록 */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-bold text-white">생성된 콘텐츠</h3>
          <p className="text-white/80 text-sm mt-1">AI가 생성한 맞춤형 홍보 콘텐츠를 확인하고 관리하세요</p>
        </div>
        <div className="card-body">
          {contents.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-6xl mb-4 block">✨</span>
              <h3 className="text-lg font-medium text-gray-900 mb-2">아직 생성된 콘텐츠가 없습니다</h3>
              <p className="text-gray-600">위에서 설정을 완료하고 콘텐츠를 생성해보세요.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {contents.map(content => {
                const influencer = selectedInfluencers.find(i => i.id === content.influencerId);
                
                return (
                  <div key={content.id} className="card">
                    <div className="card-body">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="text-2xl">{influencer?.avatar || '👤'}</div>
                          <div>
                            <h4 className="font-bold text-gray-900">{content.title}</h4>
                            <p className="text-sm text-gray-600">{influencer?.name || '알 수 없음'}</p>
                            <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                              <span>{getContentTypeText(content.contentType)}</span>
                              <span>•</span>
                              <span>{getToneText(content.tone)}</span>
                              <span>•</span>
                              <span>{content.generatedAt.toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`status-badge ${
                            content.status === 'draft' ? 'status-draft' :
                            content.status === 'approved' ? 'status-active' : 'status-completed'
                          }`}>
                            {getStatusText(content.status)}
                          </span>
                          {content.status === 'draft' && (
                            <button
                              onClick={() => handleApprove(content.id)}
                              className="btn-success text-xs px-3 py-1"
                            >
                              승인
                            </button>
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-gray-50 to-purple-50 rounded-xl p-4 mb-4">
                        <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                          {content.content.length > 200 
                            ? `${content.content.substring(0, 200)}...` 
                            : content.content
                          }
                        </p>
                      </div>
                      
                      {content.hashtags && content.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {content.hashtags.map(tag => (
                            <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
                        <div>타겟: {content.targetAudience}</div>
                        <div>플랫폼: {influencer?.platform || '알 수 없음'}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContentGenerator;