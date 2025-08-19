import React, { useState, useEffect } from 'react';
import { Channel } from '../types';

interface ChannelExplorerProps {
  onSelectChannels: (channels: Channel[]) => void;
  selectedCategory?: string;
}

const ChannelExplorer: React.FC<ChannelExplorerProps> = ({
  onSelectChannels,
  selectedCategory
}) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannels, setSelectedChannels] = useState<Channel[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlatform, setFilterPlatform] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  // 예시 채널 데이터
  const mockChannels: Channel[] = [
    {
      id: '1',
      name: 'Instagram',
      platform: 'instagram',
      description: '시각적 콘텐츠 중심의 소셜 미디어 플랫폼',
      audience: 2000000000,
      engagement: 4.2,
      costPerPost: 500000,
      demographics: { age: '18-34', gender: '여성 60%' },
      categories: ['beauty', 'fashion', 'lifestyle'],
      icon: '📸'
    },
    {
      id: '2',
      name: 'YouTube',
      platform: 'youtube',
      description: '동영상 콘텐츠 플랫폼',
      audience: 2700000000,
      engagement: 3.8,
      costPerPost: 1200000,
      demographics: { age: '25-44', gender: '남성 55%' },
      categories: ['tech', 'gaming', 'education'],
      icon: '📺'
    },
    {
      id: '3',
      name: 'TikTok',
      platform: 'tiktok',
      description: '숏폼 비디오 플랫폼',
      audience: 1000000000,
      engagement: 5.9,
      costPerPost: 300000,
      demographics: { age: '16-24', gender: '여성 57%' },
      categories: ['entertainment', 'dance', 'comedy'],
      icon: '🎵'
    },
    {
      id: '4',
      name: 'Naver Blog',
      platform: 'naver',
      description: '네이버 블로그 플랫폼',
      audience: 45000000,
      engagement: 3.2,
      costPerPost: 200000,
      demographics: { age: '30-50', gender: '여성 65%' },
      categories: ['beauty', 'food', 'travel'],
      icon: '📝'
    }
  ];

  useEffect(() => {
    setLoading(true);
    // 실제로는 API 호출
    setTimeout(() => {
      setChannels(mockChannels);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredChannels = channels.filter(channel => {
    const matchesSearch = channel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         channel.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPlatform = filterPlatform === 'all' || channel.platform === filterPlatform;
    const matchesCategory = !selectedCategory || channel.categories.includes(selectedCategory);
    
    return matchesSearch && matchesPlatform && matchesCategory;
  });

  const handleChannelSelect = (channel: Channel) => {
    const isSelected = selectedChannels.find(c => c.id === channel.id);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedChannels.filter(c => c.id !== channel.id);
    } else {
      newSelection = [...selectedChannels, channel];
    }
    
    setSelectedChannels(newSelection);
    onSelectChannels(newSelection);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="loading-spinner"></div>
        <span className="ml-3 text-lg">채널 정보를 불러오는 중...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-bold text-white">채널 탐색기</h2>
          <p className="text-white/80 text-sm mt-1">마케팅에 적합한 채널을 선택하세요</p>
        </div>
        <div className="card-body">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="채널 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input"
              />
            </div>
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="form-select md:w-48"
            >
              <option value="all">모든 플랫폼</option>
              <option value="instagram">Instagram</option>
              <option value="youtube">YouTube</option>
              <option value="tiktok">TikTok</option>
              <option value="naver">Naver Blog</option>
            </select>
          </div>
          
          {selectedChannels.length > 0 && (
            <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
              <h3 className="font-medium text-gray-900 mb-2">선택된 채널 ({selectedChannels.length}개)</h3>
              <div className="flex flex-wrap gap-2">
                {selectedChannels.map(channel => (
                  <span
                    key={channel.id}
                    className="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-sm flex items-center gap-1"
                  >
                    <span>{channel.icon}</span>
                    {channel.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 채널 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredChannels.map(channel => {
          const isSelected = selectedChannels.find(c => c.id === channel.id);
          
          return (
            <div
              key={channel.id}
              className={`card cursor-pointer transition-all duration-300 ${
                isSelected ? 'ring-2 ring-purple-500 bg-gradient-to-br from-purple-50 to-pink-50' : ''
              }`}
              onClick={() => handleChannelSelect(channel)}
            >
              <div className="card-body">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{channel.icon}</div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{channel.name}</h3>
                      <p className="text-sm text-gray-600">{channel.description}</p>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="text-purple-500">
                      <span className="text-xl">✓</span>
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">월간 활성 사용자</span>
                    <span className="font-medium">{(channel.audience / 1000000).toFixed(1)}억명</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">평균 참여율</span>
                    <span className="font-medium text-green-600">{channel.engagement}%</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">게시물당 비용</span>
                    <span className="font-medium">₩{channel.costPerPost.toLocaleString()}</span>
                  </div>
                  
                  <div className="pt-2 border-t border-gray-100">
                    <div className="text-sm text-gray-600 mb-1">주요 타겟층</div>
                    <div className="text-sm">
                      <span className="text-purple-600">{channel.demographics.age}</span>
                      <span className="mx-2">•</span>
                      <span className="text-pink-600">{channel.demographics.gender}</span>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mt-2">
                    {channel.categories.map(category => (
                      <span
                        key={category}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredChannels.length === 0 && (
        <div className="text-center py-12">
          <span className="text-6xl mb-4 block">🔍</span>
          <h3 className="text-lg font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
          <p className="text-gray-600">다른 검색어나 필터를 시도해보세요.</p>
        </div>
      )}
    </div>
  );
};

export default ChannelExplorer;