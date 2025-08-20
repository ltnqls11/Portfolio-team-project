import React, { useState } from 'react';

const App = () => {
  const [bloggers, setBloggers] = useState([]);
  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // AI 분석을 위한 함수
  const analyzeProductWithAI = async (name, description) => {
    // API 호출을 위한 프롬프트
    const prompt = `
      You are an expert marketing analyst.
      Analyze the following product and generate a list of 5 hypothetical bloggers suitable for promotion.
      The output must be a JSON array. Each object in the array should have the following properties:
      - name: A fictional blogger name (e.g., "뷰티블로거A")
      - category: A category relevant to the product.
      - reach: A fictional reach number (e.g., 50000)
      - engagementRate: A fictional engagement rate (e.g., 0.08)
      - recentUploadDaysAgo: A fictional number of days since their last upload
      - score: A score from 70 to 100, representing their promotional suitability, based on your analysis.

      Product Name: ${name}
      Product Description: ${description}

      Ensure the JSON is well-formed and valid, with no extra text or explanations outside the array.
    `;

    const payload = {
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              name: { type: "STRING" },
              category: { type: "STRING" },
              reach: { type: "NUMBER" },
              engagementRate: { type: "NUMBER" },
              recentUploadDaysAgo: { type: "NUMBER" },
              score: { type: "NUMBER" }
            },
            "propertyOrdering": ["name", "category", "reach", "engagementRate", "recentUploadDaysAgo", "score"]
          }
        }
      }
    };
    
    // API 키는 Canvas 환경에서 자동으로 제공됩니다.
    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    let attempts = 0;
    const maxAttempts = 5;
    while (attempts < maxAttempts) {
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          if (response.status === 429) {
            const delay = Math.pow(2, attempts) * 1000 + Math.random() * 1000;
            console.log(`Rate limit exceeded. Retrying in ${delay / 1000}s...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            attempts++;
            continue;
          }
          throw new Error(`API request failed with status: ${response.status}`);
        }

        const result = await response.json();
        const jsonText = result.candidates[0].content.parts[0].text;
        const parsedData = JSON.parse(jsonText);

        return parsedData;
      } catch (e) {
        console.error('Error during API call:', e);
        throw e;
      }
    }
    throw new Error('Failed to fetch data after multiple retries.');
  };

  const handleSearch = async () => {
    if (!productName || !productDescription) {
      setError('제품명과 설명을 모두 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const bloggerData = await analyzeProductWithAI(productName, productDescription);
      // AI 점수를 기준으로 내림차순 정렬
      const sortedBloggers = [...bloggerData].sort((a, b) => b.score - a.score);
      setBloggers(sortedBloggers);
    } catch (e) {
      setError('추천 목록을 가져오는 데 실패했습니다.');
      console.error(e);
      setBloggers([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen py-10 font-sans">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">AI 기반 블로거 추천</h1>
        <p className="text-center text-gray-500 mb-8">제품 정보를 입력하면 AI가 추천 블로거를 찾아줍니다.</p>

        {/* 입력 섹션 */}
        <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
          <div className="flex flex-col space-y-4">
            <div className="flex flex-col">
              <label htmlFor="productName" className="text-sm font-medium text-gray-600 mb-1">제품명</label>
              <input
                type="text"
                id="productName"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
                placeholder="예: AI 화장품"
              />
            </div>
            <div className="flex flex-col">
              <label htmlFor="productDescription" className="text-sm font-medium text-gray-600 mb-1">제품 설명</label>
              <textarea
                id="productDescription"
                value={productDescription}
                onChange={(e) => setProductDescription(e.target.value)}
                className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors h-32 resize-none"
                placeholder="제품의 특징, 주요 기능, 타겟 고객 등을 상세하게 입력하세요."
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className={`p-3 rounded-lg text-white font-semibold transition-all duration-300 ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800'}`}
            >
              {isLoading ? '분석 중...' : 'AI로 추천 블로거 찾기'}
            </button>
          </div>
        </div>

        {/* 결과 섹션 */}
        {error && (
          <div className="text-center text-red-500 p-4 bg-red-100 rounded-xl mb-8">
            <p>{error}</p>
          </div>
        )}
        
        {bloggers.length > 0 && (
          <div className="space-y-4">
            {bloggers.map(blogger => (
              <div key={blogger.name} className="bg-white p-6 rounded-xl shadow-lg flex flex-col md:flex-row items-center justify-between">
                <div className="flex-grow">
                  <h3 className="text-lg font-bold text-gray-800">{blogger.name}</h3>
                  <div className="flex flex-wrap items-center text-sm text-gray-500 mt-1 space-x-4">
                    <span>카테고리: <span className="font-semibold text-gray-700">{blogger.category}</span></span>
                    <span>도달: <span className="font-semibold text-gray-700">{blogger.reach.toLocaleString()}명</span></span>
                    <span>참여율: <span className="font-semibold text-gray-700">{(blogger.engagementRate * 100).toFixed(1)}%</span></span>
                    <span>업로드: <span className="font-semibold text-gray-700">{blogger.recentUploadDaysAgo}일 전</span></span>
                  </div>
                </div>
                <div className="mt-4 md:mt-0 flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold text-white shadow-md" style={{ backgroundColor: `hsl(${blogger.score}, 80%, 50%)` }}>
                    {blogger.score}
                  </div>
                  <span className="text-xs text-gray-500 mt-1">AI 추천 점수</span>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default App;
