import React, { useState, useEffect } from 'react';
import { GeneratedContent, ReviewData } from '../types';
import { generateContent, getGeneratedContent, approveContent } from '../services/api';

interface ContentGeneratorProps {
  campaignId: string;
  reviews: ReviewData[];
}

const ContentGenerator: React.FC<ContentGeneratorProps> = ({ campaignId, reviews }) => {
  const [contents, setContents] = useState<GeneratedContent[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedReviews, setSelectedReviews] = useState<string[]>([]);
  const [contentSettings, setContentSettings] = useState({
    contentType: 'blog_post' as 'blog_post' | 'sns_post' | 'email_template',
    tone: 'friendly' as 'professional' | 'casual' | 'friendly' | 'trendy',
    targetAudience: '20-30대 여성'
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
    if (selectedReviews.length === 0) {
      alert('콘텐츠 생성에 사용할 리뷰를 선택해주세요.');
      return;
    }

    setGenerating(true);
    try {
      const newContent = await generateContent({
        campaignId,
        ...contentSettings,
        basedOnReviews: selectedReviews
      });
      
      setContents(prev => [newContent, ...prev]);
      alert('새로운 콘텐츠가 생성되었습니다!');
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
      case 'blog_post': return '블로그 포스트';
      case 'sns_post': return 'SNS 포스트';
      case 'email_template': return '이메일 템플릿';
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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">AI 콘텐츠 자동 생성</h2>
        
        {/* 생성 설정 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">콘텐츠 타입</label>
            <select
              value={contentSettings.contentType}
              onChange={(e) => setContentSettings({
                ...contentSettings, 
                contentType: e.target.value as any
              })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="blog_post">블로그 포스트</option>
              <option value="sns_post">SNS 포스트</option>
              <option value="email_template">이메일 템플릿</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">톤앤매너</label>
            <select
              value={contentSettings.tone}
              onChange={(e) => setContentSettings({
                ...contentSettings, 
                tone: e.target.value as any
              })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="professional">전문적</option>
              <option value="casual">캐주얼</option>
              <option value="friendly">친근한</option>
              <option value="trendy">트렌디</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">타겟 고객</label>
            <input
              type="text"
              value={contentSettings.targetAudience}
              onChange={(e) => setContentSettings({
                ...contentSettings, 
                targetAudience: e.target.value
              })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              placeholder="예: 20-30대 여성"
            />
          </div>
        </div>

        {/* 리뷰 선택 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            참고할 리뷰 선택 ({selectedReviews.length}/{reviews.length})
          </label>
          <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
            {reviews.map(review => (
              <label key={review.id} className="flex items-start gap-2 mb-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedReviews.includes(review.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedReviews(prev => [...prev, review.id]);
                    } else {
                      setSelectedReviews(prev => prev.filter(id => id !== review.id));
                    }
                  }}
                  className="mt-1"
                />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{review.title}</p>
                  <p className="text-xs text-gray-600">{review.bloggerName} | ★ {review.rating}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating || selectedReviews.length === 0}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
        >
          {generating ? 'AI가 콘텐츠를 생성하고 있습니다...' : '콘텐츠 생성하기'}
        </button>
      </div>

      {/* 생성된 콘텐츠 목록 */}
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">생성된 콘텐츠</h3>
        
        {contents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            아직 생성된 콘텐츠가 없습니다.
          </div>
        ) : (
          <div className="space-y-4">
            {contents.map(content => (
              <div key={content.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{content.title}</h4>
                    <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
                      <span>{getContentTypeText(content.contentType)}</span>
                      <span>•</span>
                      <span>{getToneText(content.tone)}</span>
                      <span>•</span>
                      <span>{content.generatedAt.toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(content.status)}`}>
                      {getStatusText(content.status)}
                    </span>
                    {content.status === 'draft' && (
                      <button
                        onClick={() => handleApprove(content.id)}
                        className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                      >
                        승인
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {content.content.length > 300 
                      ? `${content.content.substring(0, 300)}...` 
                      : content.content
                    }
                  </p>
                </div>
                
                {content.hashtags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {content.hashtags.map(tag => (
                      <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  타겟: {content.targetAudience} | 참고 리뷰: {content.basedOnReviews.length}개
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentGenerator;