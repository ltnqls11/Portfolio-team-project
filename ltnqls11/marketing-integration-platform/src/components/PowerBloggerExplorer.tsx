import React, { useState, useEffect } from 'react';
import { PowerBlogger, BlogCategory } from '../types';
import { getPowerBloggers, crawlBloggerData } from '../services/api';

interface PowerBloggerExplorerProps {
  onSelectBloggers: (bloggers: PowerBlogger[]) => void;
  selectedCategory?: BlogCategory;
}

const PowerBloggerExplorer: React.FC<PowerBloggerExplorerProps> = ({ 
  onSelectBloggers, 
  selectedCategory 
}) => {
  const [bloggers, setBloggers] = useState<PowerBlogger[]>([]);
  const [selectedBloggers, setSelectedBloggers] = useState<PowerBlogger[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    category: selectedCategory || 'beauty' as BlogCategory,
    minSubscribers: 1000,
    maxSubscribers: 100000,
    minEngagementRate: 0.02
  });
  const [newBlogUrl, setNewBlogUrl] = useState('');
  const [crawling, setCrawling] = useState(false);

  const categories: { value: BlogCategory; label: string }[] = [
    { value: 'beauty', label: '뷰티' },
    { value: 'fashion', label: '패션' },
    { value: 'food', label: '맛집/요리' },
    { value: 'travel', label: '여행' },
    { value: 'lifestyle', label: '라이프스타일' },
    { value: 'tech', label: '기술/IT' },
    { value: 'health', label: '건강/운동' },
    { value: 'parenting', label: '육아' },
    { value: 'home', label: '인테리어' },
    { value: 'pet', label: '반려동물' }
  ];

  useEffect(() => {
    fetchBloggers();
  }, [filters]);

  const fetchBloggers = async () => {
    setLoading(true);
    try {
      const data = await getPowerBloggers(filters);
      setBloggers(data);
    } catch (error) {
      console.error('파워블로거 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBloggerSelect = (blogger: PowerBlogger) => {
    const isSelected = selectedBloggers.find(b => b.id === blogger.id);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedBloggers.filter(b => b.id !== blogger.id);
    } else {
      newSelection = [...selectedBloggers, blogger];
    }
    
    setSelectedBloggers(newSelection);
    onSelectBloggers(newSelection);
  };

  const handleCrawlNewBlogger = async () => {
    if (!newBlogUrl.trim()) return;
    
    setCrawling(true);
    try {
      const newBlogger = await crawlBloggerData(newBlogUrl);
      setBloggers(prev => [newBlogger, ...prev]);
      setNewBlogUrl('');
      alert('새로운 블로거가 추가되었습니다!');
    } catch (error) {
      console.error('블로거 크롤링 실패:', error);
      alert('블로거 정보를 가져오는데 실패했습니다.');
    } finally {
      setCrawling(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 10000) return `${(num / 10000).toFixed(1)}만`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}천`;
    return num.toString();
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">파워블로거 탐색</h2>
        
        {/* 필터 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value as BlogCategory})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">최소 구독자</label>
            <input
              type="number"
              value={filters.minSubscribers}
              onChange={(e) => setFilters({...filters, minSubscribers: Number(e.target.value)})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">최대 구독자</label>
            <input
              type="number"
              value={filters.maxSubscribers}
              onChange={(e) => setFilters({...filters, maxSubscribers: Number(e.target.value)})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">최소 참여율</label>
            <input
              type="number"
              step="0.01"
              value={filters.minEngagementRate}
              onChange={(e) => setFilters({...filters, minEngagementRate: Number(e.target.value)})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
        </div>

        {/* 새 블로거 추가 */}
        <div className="flex gap-2 mb-4">
          <input
            type="url"
            placeholder="네이버 블로그 URL을 입력하세요"
            value={newBlogUrl}
            onChange={(e) => setNewBlogUrl(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
          />
          <button
            onClick={handleCrawlNewBlogger}
            disabled={crawling || !newBlogUrl.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {crawling ? '분석중...' : '블로거 추가'}
          </button>
        </div>

        {/* 선택된 블로거 수 */}
        <div className="text-sm text-gray-600">
          선택된 블로거: {selectedBloggers.length}명
        </div>
      </div>

      {/* 블로거 목록 */}
      <div className="p-6">
        {loading ? (
          <div className="text-center py-8">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-600">파워블로거를 검색하고 있습니다...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {bloggers.map(blogger => (
              <div
                key={blogger.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedBloggers.find(b => b.id === blogger.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleBloggerSelect(blogger)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 truncate">{blogger.blogTitle}</h3>
                    <p className="text-sm text-gray-600">{blogger.bloggerName}</p>
                  </div>
                  {blogger.isVerified && (
                    <span className="text-blue-500 text-xs">✓ 인증</span>
                  )}
                </div>
                
                <div className="space-y-1 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>구독자</span>
                    <span className="font-medium">{formatNumber(blogger.subscriberCount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>평균 조회수</span>
                    <span className="font-medium">{formatNumber(blogger.avgViews)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>참여율</span>
                    <span className="font-medium">{(blogger.engagementRate * 100).toFixed(1)}%</span>
                  </div>
                  {blogger.collaborationRate && (
                    <div className="flex justify-between">
                      <span>협업 단가</span>
                      <span className="font-medium text-green-600">
                        {blogger.collaborationRate.toLocaleString()}원
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="mt-2 flex flex-wrap gap-1">
                  {blogger.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {!loading && bloggers.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            조건에 맞는 파워블로거를 찾을 수 없습니다.
          </div>
        )}
      </div>
    </div>
  );
};

export default PowerBloggerExplorer;