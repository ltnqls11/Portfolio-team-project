import React, { useState, useEffect } from 'react';
import { ReviewData, BlogCategory } from '../types';
import { crawlReviews, getReviews } from '../services/api';

interface ReviewCrawlerProps {
  campaignId: string;
  category: BlogCategory;
  onReviewsUpdate: (reviews: ReviewData[]) => void;
}

const ReviewCrawler: React.FC<ReviewCrawlerProps> = ({ 
  campaignId, 
  category, 
  onReviewsUpdate 
}) => {
  const [reviews, setReviews] = useState<ReviewData[]>([]);
  const [crawling, setCrawling] = useState(false);
  const [keywords, setKeywords] = useState<string>('');
  const [selectedReviews, setSelectedReviews] = useState<ReviewData[]>([]);

  useEffect(() => {
    fetchExistingReviews();
  }, [campaignId]);

  const fetchExistingReviews = async () => {
    try {
      const data = await getReviews(campaignId);
      setReviews(data);
      onReviewsUpdate(data);
    } catch (error) {
      console.error('기존 리뷰 조회 실패:', error);
    }
  };

  const handleCrawl = async () => {
    if (!keywords.trim()) {
      alert('크롤링할 키워드를 입력해주세요.');
      return;
    }

    setCrawling(true);
    try {
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
      const newReviews = await crawlReviews(keywordList, category);
      
      const updatedReviews = [...reviews, ...newReviews];
      setReviews(updatedReviews);
      onReviewsUpdate(updatedReviews);
      
      alert(`${newReviews.length}개의 새로운 리뷰를 찾았습니다!`);
    } catch (error) {
      console.error('리뷰 크롤링 실패:', error);
      alert('리뷰 크롤링에 실패했습니다.');
    } finally {
      setCrawling(false);
    }
  };

  const handleReviewSelect = (review: ReviewData) => {
    const isSelected = selectedReviews.find(r => r.id === review.id);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedReviews.filter(r => r.id !== review.id);
    } else {
      newSelection = [...selectedReviews, review];
    }
    
    setSelectedReviews(newSelection);
  };

  const getSentimentColor = (sentiment: ReviewData['sentiment']) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentText = (sentiment: ReviewData['sentiment']) => {
    switch (sentiment) {
      case 'positive': return '긍정';
      case 'negative': return '부정';
      default: return '중립';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">체험단 후기 크롤링</h2>
        
        {/* 크롤링 설정 */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              크롤링 키워드 (쉼표로 구분)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="예: 스킨케어, 화장품, 뷰티"
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
              />
              <button
                onClick={handleCrawl}
                disabled={crawling}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {crawling ? '크롤링 중...' : '크롤링 시작'}
              </button>
            </div>
          </div>
          
          <div className="text-sm text-gray-600">
            총 {reviews.length}개의 리뷰 | 선택된 리뷰: {selectedReviews.length}개
          </div>
        </div>
      </div>

      {/* 리뷰 목록 */}
      <div className="p-6">
        {crawling && (
          <div className="text-center py-8">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-600">네이버 블로그에서 체험단 후기를 수집하고 있습니다...</p>
            <p className="text-sm text-gray-500 mt-2">이 작업은 몇 분 정도 소요될 수 있습니다.</p>
          </div>
        )}

        <div className="space-y-4">
          {reviews.map(review => (
            <div
              key={review.id}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                selectedReviews.find(r => r.id === review.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => handleReviewSelect(review)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900 mb-1">{review.title}</h3>
                  <p className="text-sm text-gray-600">
                    {review.bloggerName} | {review.publishedAt.toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(review.sentiment)}`}>
                    {getSentimentText(review.sentiment)}
                  </span>
                  <span className="text-yellow-500">★ {review.rating}</span>
                </div>
              </div>
              
              <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                {review.content.substring(0, 200)}...
              </p>
              
              {/* 장단점 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                {review.pros.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-green-700 mb-1">장점</h4>
                    <ul className="text-xs text-green-600 space-y-1">
                      {review.pros.slice(0, 2).map((pro, index) => (
                        <li key={index}>• {pro}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {review.cons.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-red-700 mb-1">단점</h4>
                    <ul className="text-xs text-red-600 space-y-1">
                      {review.cons.slice(0, 2).map((con, index) => (
                        <li key={index}>• {con}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              {/* 키워드 태그 */}
              <div className="flex flex-wrap gap-1">
                {review.keywords.slice(0, 5).map(keyword => (
                  <span key={keyword} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                    #{keyword}
                  </span>
                ))}
              </div>
              
              {/* 블로그 링크 */}
              <div className="mt-2">
                <a
                  href={review.blogUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-800"
                  onClick={(e) => e.stopPropagation()}
                >
                  원문 보기 →
                </a>
              </div>
            </div>
          ))}
        </div>
        
        {!crawling && reviews.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            아직 크롤링된 리뷰가 없습니다. 키워드를 입력하고 크롤링을 시작해보세요.
          </div>
        )}
      </div>
      
      {/* 선택된 리뷰로 콘텐츠 생성 버튼 */}
      {selectedReviews.length > 0 && (
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <button className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
            선택된 {selectedReviews.length}개 리뷰로 마케팅 콘텐츠 생성하기
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewCrawler;