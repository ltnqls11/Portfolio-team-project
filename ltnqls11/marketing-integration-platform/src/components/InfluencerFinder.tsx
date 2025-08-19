import React, { useState, useEffect } from 'react';
import { Influencer, Channel } from '../types';

interface InfluencerFinderProps {
  onSelectInfluencers: (influencers: Influencer[]) => void;
  selectedChannels: Channel[];
  selectedCategory?: string;
}

const InfluencerFinder: React.FC<InfluencerFinderProps> = ({
  onSelectInfluencers,
  selectedChannels,
  selectedCategory
}) => {
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [selectedInfluencers, setSelectedInfluencers] = useState<Influencer[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFollowers, setFilterFollowers] = useState<string>('all');
  const [filterEngagement, setFilterEngagement] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  // 예시 인플루언서 데이터
  const mockInfluencers: Influencer[] = [
    {
      id: '1',
      name: '뷰티구루 김민지',
      username: '@beauty_minji',
      platform: 'instagram',
      followers: 850000,
      engagement: 4.8,
      category: 'beauty',
      bio: '뷰티 크리에이터 | 화장품 리뷰 전문 | 협업 문의 DM',
      avatar: '👩‍💄',
      verified: true,
      costPerPost: 1200000,
      recentPosts: 45,
      avgLikes: 35000,
      avgComments: 1200,
      demographics: { age: '20-35', gender: '여성 85%' },
      tags: ['뷰티', '화장품', '스킨케어', '메이크업']
    },
    {
      id: '2',
      name: '테크리뷰어 박준호',
      username: '@tech_junho',
      platform: 'youtube',
      followers: 1200000,
      engagement: 3.9,
      category: 'tech',
      bio: '최신 기술 리뷰 | 가젯 언박싱 | 매주 화요일 업로드',
      avatar: '👨‍💻',
      verified: true,
      costPerPost: 2500000,
      recentPosts: 12,
      avgLikes: 45000,
      avgComments: 2800,
      demographics: { age: '25-40', gender: '남성 70%' },
      tags: ['기술', '가젯', '리뷰', '언박싱']
    },
    {
      id: '3',
      name: '라이프스타일 이서연',
      username: '@lifestyle_seoyeon',
      platform: 'instagram',
      followers: 650000,
      engagement: 5.2,
      category: 'lifestyle',
      bio: '일상 공유 | 카페 투어 | 패션 코디 | 협업 환영',
      avatar: '👩‍🎨',
      verified: false,
      costPerPost: 800000,
      recentPosts: 78,
      avgLikes: 28000,
      avgComments: 950,
      demographics: { age: '20-30', gender: '여성 90%' },
      tags: ['라이프스타일', '카페', '패션', '일상']
    },
    {
      id: '4',
      name: '푸드블로거 최요리',
      username: '@food_yori',
      platform: 'naver',
      followers: 320000,
      engagement: 4.1,
      category: 'food',
      bio: '맛집 탐방 | 레시피 공유 | 요리 클래스 운영',
      avatar: '👩‍🍳',
      verified: true,
      costPerPost: 450000,
      recentPosts: 156,
      avgLikes: 12000,
      avgComments: 680,
      demographics: { age: '25-45', gender: '여성 75%' },
      tags: ['음식', '맛집', '레시피', '요리']
    }
  ];

  useEffect(() => {
    setLoading(true);
    // 실제로는 API 호출
    setTimeout(() => {
      setInfluencers(mockInfluencers);
      setLoading(false);
    }, 1000);
  }, [selectedChannels]);

  const filteredInfluencers = influencers.filter(influencer => {
    const matchesSearch = influencer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         influencer.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         influencer.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesChannel = selectedChannels.length === 0 || 
                          selectedChannels.some(channel => channel.platform === influencer.platform);
    
    const matchesFollowers = filterFollowers === 'all' ||
                           (filterFollowers === 'micro' && influencer.followers < 100000) ||
                           (filterFollowers === 'mid' && influencer.followers >= 100000 && influencer.followers < 1000000) ||
                           (filterFollowers === 'macro' && influencer.followers >= 1000000);
    
    const matchesEngagement = filterEngagement === 'all' ||
                            (filterEngagement === 'high' && influencer.engagement >= 4.0) ||
                            (filterEngagement === 'medium' && influencer.engagement >= 2.0 && influencer.engagement < 4.0) ||
                            (filterEngagement === 'low' && influencer.engagement < 2.0);
    
    const matchesCategory = !selectedCategory || influencer.category === selectedCategory;
    
    return matchesSearch && matchesChannel && matchesFollowers && matchesEngagement && matchesCategory;
  });

  const handleInfluencerSelect = (influencer: Influencer) => {
    const isSelected = selectedInfluencers.find(i => i.id === influencer.id);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedInfluencers.filter(i => i.id !== influencer.id);
    } else {
      newSelection = [...selectedInfluencers, influencer];
    }
    
    setSelectedInfluencers(newSelection);
    onSelectInfluencers(newSelection);
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'instagram': return '📸';
      case 'youtube': return '📺';
      case 'tiktok': return '🎵';
      case 'naver': return '📝';
      default: return '📱';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="loading-spinner"></div>
        <span className="ml-3 text-lg">인플루언서 정보를 불러오는 중...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-bold text-white">인플루언서 탐색기</h2>
          <p className="text-white/80 text-sm mt-1">브랜드에 적합한 인플루언서를 찾아보세요</p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <input
                type="text"
                placeholder="인플루언서 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input"
              />
            </div>
            <select
              value={filterFollowers}
              onChange={(e) => setFilterFollowers(e.target.value)}
              className="form-select"
            >
              <option value="all">모든 팔로워 수</option>
              <option value="micro">마이크로 (10만 미만)</option>
              <option value="mid">미드티어 (10만-100만)</option>
              <option value="macro">매크로 (100만 이상)</option>
            </select>
            <select
              value={filterEngagement}
              onChange={(e) => setFilterEngagement(e.target.value)}
              className="form-select"
            >
              <option value="all">모든 참여율</option>
              <option value="high">높음 (4% 이상)</option>
              <option value="medium">보통 (2-4%)</option>
              <option value="low">낮음 (2% 미만)</option>
            </select>
          </div>
          
          {selectedInfluencers.length > 0 && (
            <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
              <h3 className="font-medium text-gray-900 mb-2">선택된 인플루언서 ({selectedInfluencers.length}명)</h3>
              <div className="flex flex-wrap gap-2">
                {selectedInfluencers.map(influencer => (
                  <span
                    key={influencer.id}
                    className="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-sm flex items-center gap-1"
                  >
                    <span>{influencer.avatar}</span>
                    {influencer.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 인플루언서 목록 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredInfluencers.map(influencer => {
          const isSelected = selectedInfluencers.find(i => i.id === influencer.id);
          
          return (
            <div
              key={influencer.id}
              className={`card cursor-pointer transition-all duration-300 ${
                isSelected ? 'ring-2 ring-purple-500 bg-gradient-to-br from-purple-50 to-pink-50' : ''
              }`}
              onClick={() => handleInfluencerSelect(influencer)}
            >
              <div className="card-body">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{influencer.avatar}</div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-gray-900">{influencer.name}</h3>
                        {influencer.verified && (
                          <span className="text-blue-500 text-sm">✓</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{influencer.username}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-sm">{getPlatformIcon(influencer.platform)}</span>
                        <span className="text-xs text-gray-500 capitalize">{influencer.platform}</span>
                      </div>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="text-purple-500">
                      <span className="text-xl">✓</span>
                    </div>
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-4">{influencer.bio}</p>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center p-3 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl">
                    <div className="text-lg font-bold text-blue-600">
                      {influencer.followers >= 1000000 
                        ? `${(influencer.followers / 1000000).toFixed(1)}M`
                        : `${(influencer.followers / 1000).toFixed(0)}K`
                      }
                    </div>
                    <div className="text-xs text-gray-600">팔로워</div>
                  </div>
                  <div className="text-center p-3 bg-gradient-to-br from-green-50 to-blue-50 rounded-xl">
                    <div className="text-lg font-bold text-green-600">{influencer.engagement}%</div>
                    <div className="text-xs text-gray-600">참여율</div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">게시물당 비용</span>
                    <span className="font-medium">₩{influencer.costPerPost.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">최근 게시물</span>
                    <span className="font-medium">{influencer.recentPosts}개</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">평균 좋아요</span>
                    <span className="font-medium">{influencer.avgLikes.toLocaleString()}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100">
                  <div className="text-sm text-gray-600 mb-2">주요 타겟층</div>
                  <div className="text-sm mb-3">
                    <span className="text-purple-600">{influencer.demographics.age}</span>
                    <span className="mx-2">•</span>
                    <span className="text-pink-600">{influencer.demographics.gender}</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {influencer.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredInfluencers.length === 0 && (
        <div className="text-center py-12">
          <span className="text-6xl mb-4 block">🔍</span>
          <h3 className="text-lg font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
          <p className="text-gray-600">다른 검색어나 필터를 시도해보세요.</p>
        </div>
      )}
    </div>
  );
};

export default InfluencerFinder;