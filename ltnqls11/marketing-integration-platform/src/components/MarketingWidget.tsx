import React, { useState } from 'react';
import { Campaign, Channel } from '../types';
import { updateCampaign } from '../services/api';

interface MarketingWidgetProps {
  campaignData: Campaign;
  onUpdate?: () => void;
}

const MarketingWidget: React.FC<MarketingWidgetProps> = ({ campaignData, onUpdate }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(campaignData);

  const getStatusColor = (status: Campaign['status']) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: Campaign['status']) => {
    switch (status) {
      case 'active': return '진행중';
      case 'draft': return '초안';
      case 'paused': return '일시정지';
      case 'completed': return '완료';
      default: return '알 수 없음';
    }
  };

  const getChannelText = (channel: Channel) => {
    switch (channel) {
      case 'naver_blog': return '네이버 블로그';
      case 'blogspot': return '블로그스팟';
      case 'tistory': return '티스토리';
      case 'kakao_channel': return '카카오채널';
      case 'instagram_feed': return '인스타 피드';
      case 'instagram_story': return '인스타 스토리';
      case 'instagram_reel': return '인스타 릴스';
      default: return channel;
    }
  };

  const handleSave = async () => {
    try {
      await updateCampaign(campaignData.id, editData);
      setIsEditing(false);
      onUpdate?.();
    } catch (error) {
      console.error('Error updating campaign:', error);
      alert('캠페인 업데이트 중 오류가 발생했습니다.');
    }
  };

  const handleCancel = () => {
    setEditData(campaignData);
    setIsEditing(false);
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('ko-KR');
  };

  const calculateProgress = () => {
    const now = new Date();
    const start = new Date(campaignData.startAt);
    const end = new Date(campaignData.endAt);
    
    if (now < start) return 0;
    if (now > end) return 100;
    
    const total = end.getTime() - start.getTime();
    const elapsed = now.getTime() - start.getTime();
    return Math.round((elapsed / total) * 100);
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
      {/* 캠페인 헤더 */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {isEditing ? (
              <input
                type="text"
                value={editData.title}
                onChange={(e) => setEditData({...editData, title: e.target.value})}
                className="text-lg font-semibold border border-gray-300 rounded px-2 py-1 w-full"
              />
            ) : (
              <h3 className="text-lg font-semibold text-gray-900">{campaignData.title}</h3>
            )}
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(campaignData.status)}`}>
                {getStatusText(campaignData.status)}
              </span>
              <span>예산: ₩{campaignData.budget.toLocaleString()}</span>
              <span>{formatDate(campaignData.startAt)} ~ {formatDate(campaignData.endAt)}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                >
                  저장
                </button>
                <button
                  onClick={handleCancel}
                  className="px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                >
                  취소
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
              >
                수정
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
            >
              {isExpanded ? '접기' : '자세히'}
            </button>
          </div>
        </div>

        {/* 진행률 바 */}
        {campaignData.status === 'active' && (
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>진행률</span>
              <span>{calculateProgress()}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${calculateProgress()}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* 확장된 내용 */}
      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* 목표 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">캠페인 목표</h4>
            {isEditing ? (
              <textarea
                value={editData.objective}
                onChange={(e) => setEditData({...editData, objective: e.target.value})}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                rows={2}
              />
            ) : (
              <p className="text-sm text-gray-600">{campaignData.objective}</p>
            )}
          </div>

          {/* 채널 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">타겟 채널</h4>
            <div className="flex flex-wrap gap-2">
              {campaignData.channels.map((channel, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                >
                  {getChannelText(channel)}
                </span>
              ))}
            </div>
          </div>

          {/* 키워드 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">핵심 키워드</h4>
            <div className="flex flex-wrap gap-2">
              {campaignData.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                >
                  #{keyword}
                </span>
              ))}
            </div>
          </div>

          {/* 참고 링크 */}
          {campaignData.referenceUrls.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">참고 링크</h4>
              <div className="space-y-1">
                {campaignData.referenceUrls.map((url, index) => (
                  <a
                    key={index}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-blue-600 hover:text-blue-800 truncate"
                  >
                    {url}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* 액션 버튼 */}
          <div className="flex gap-2 pt-2 border-t border-gray-100">
            <button className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
              문구 생성
            </button>
            <button className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700">
              인플루언서 찾기
            </button>
            <button className="px-4 py-2 bg-purple-600 text-white rounded text-sm hover:bg-purple-700">
              성과 보기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketingWidget;