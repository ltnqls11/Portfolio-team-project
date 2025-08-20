import { 
  Influencer, 
  BlogPost, 
  PromotionTemplate, 
  Campaign, 
  ProductCategory 
} from '../types';

// 더미 인플루언서 데이터
export const mockInfluencers: Influencer[] = [
  {
    id: '1',
    name: '김뷰티',
    email: 'kimbeauty@email.com',
    socialMedia: {
      instagram: '@kimbeauty_official',
      youtube: '김뷰티 채널',
      blog: 'beautyblog.kr'
    },
    categories: ['화장품', '패션'],
    followers: 150000,
    engagementRate: 4.2,
    lastUpload: new Date('2024-01-15'),
    averageViews: 25000,
    averageLikes: 1200,
    averageComments: 180,
    contactStatus: '대기',
    price: 500000,
    description: '화장품 리뷰 전문 인플루언서',
    profileImage: 'https://via.placeholder.com/150'
  },
  {
    id: '2',
    name: '리빙마스터',
    email: 'livingmaster@email.com',
    socialMedia: {
      instagram: '@living_master',
      blog: 'livingmaster.blog'
    },
    categories: ['리빙제품', '청소기'],
    followers: 89000,
    engagementRate: 5.8,
    lastUpload: new Date('2024-01-14'),
    averageViews: 18000,
    averageLikes: 950,
    averageComments: 120,
    contactStatus: '수락',
    price: 350000,
    description: '리빙 제품 리뷰 및 라이프스타일',
    profileImage: 'https://via.placeholder.com/150'
  },
  {
    id: '3',
    name: '커피러버',
    email: 'coffeelover@email.com',
    socialMedia: {
      instagram: '@coffee_lover_daily',
      youtube: '커피러버의 일상'
    },
    categories: ['커피머신', '식품'],
    followers: 120000,
    engagementRate: 3.9,
    lastUpload: new Date('2024-01-13'),
    averageViews: 22000,
    averageLikes: 1100,
    averageComments: 150,
    contactStatus: '회신',
    price: 400000,
    description: '커피 머신 리뷰 및 바리스타 팁',
    profileImage: 'https://via.placeholder.com/150'
  },
  {
    id: '4',
    name: '테크리뷰어',
    email: 'techreviewer@email.com',
    socialMedia: {
      instagram: '@tech_reviewer',
      youtube: '테크리뷰어',
      blog: 'techreviewer.co.kr'
    },
    categories: ['전자제품', '청소기'],
    followers: 200000,
    engagementRate: 4.5,
    lastUpload: new Date('2024-01-12'),
    averageViews: 35000,
    averageLikes: 1800,
    averageComments: 250,
    contactStatus: '대기',
    price: 600000,
    description: '전자제품 전문 리뷰어',
    profileImage: 'https://via.placeholder.com/150'
  },
  {
    id: '5',
    name: '헬시푸드',
    email: 'healthyfood@email.com',
    socialMedia: {
      instagram: '@healthy_food_life',
      blog: 'healthyfood.blog'
    },
    categories: ['건강식품', '식품'],
    followers: 75000,
    engagementRate: 6.2,
    lastUpload: new Date('2024-01-11'),
    averageViews: 15000,
    averageLikes: 900,
    averageComments: 100,
    contactStatus: '거절',
    price: 300000,
    description: '건강식품 및 다이어트 전문',
    profileImage: 'https://via.placeholder.com/150'
  }
];

// 더미 블로그 글 데이터
export const mockBlogPosts: BlogPost[] = [
  {
    id: '1',
    title: '2024년 최고의 화장품 TOP 10',
    content: '올해 가장 인기 있는 화장품들을 소개합니다...',
    author: '김뷰티',
    authorId: '1',
    category: '화장품',
    publishedDate: new Date('2024-01-10'),
    views: 25000,
    likes: 1200,
    comments: 180,
    tags: ['화장품', '뷰티', '리뷰', '2024'],
    url: 'https://beautyblog.kr/post/1',
    performance: {
      clicks: 1500,
      conversions: 45,
      revenue: 225000
    }
  },
  {
    id: '2',
    title: '집 정리의 모든 것 - 청소기 비교 리뷰',
    content: '다양한 청소기들의 성능을 비교해보았습니다...',
    author: '리빙마스터',
    authorId: '2',
    category: '청소기',
    publishedDate: new Date('2024-01-09'),
    views: 18000,
    likes: 950,
    comments: 120,
    tags: ['청소기', '리빙', '비교', '리뷰'],
    url: 'https://livingmaster.blog/post/2',
    performance: {
      clicks: 1200,
      conversions: 38,
      revenue: 190000
    }
  },
  {
    id: '3',
    title: '집에서 카페급 커피 만드는 방법',
    content: '커피머신 선택부터 추출까지 완벽 가이드...',
    author: '커피러버',
    authorId: '3',
    category: '커피머신',
    publishedDate: new Date('2024-01-08'),
    views: 22000,
    likes: 1100,
    comments: 150,
    tags: ['커피', '커피머신', '바리스타', '가이드'],
    url: 'https://coffeelover.blog/post/3',
    performance: {
      clicks: 1400,
      conversions: 42,
      revenue: 210000
    }
  }
];

// 더미 홍보 템플릿 데이터
export const mockTemplates: PromotionTemplate[] = [
  {
    id: '1',
    name: '화장품 인스타그램 템플릿',
    channel: 'instagram',
    category: '화장품',
    tone: '친근한',
    structure: {
      title: '💄 오늘의 뷰티 아이템',
      subtitle: '실제 사용 후기',
      keywordRepetition: 3,
      cta: '지금 바로 구매하세요!',
      hashtags: ['#뷰티', '#화장품', '#리뷰', '#추천'],
      length: '보통'
    },
    content: '안녕하세요! 오늘은 정말 좋은 화장품을 소개해드릴게요 💕\n\n{제품명}을 사용해보니 정말 만족스러워서 여러분께도 추천드려요!\n\n✨ 주요 장점:\n- {장점1}\n- {장점2}\n- {장점3}\n\n실제로 사용해보니 {효과}가 정말 좋았어요!\n\n지금 구매하시면 특별 할인도 받으실 수 있답니다 😊\n\n{CTA}\n\n{해시태그}'
  },
  {
    id: '2',
    name: '청소기 유튜브 템플릿',
    channel: 'youtube',
    category: '청소기',
    tone: '전문적인',
    structure: {
      title: '청소기 성능 비교 테스트',
      subtitle: '실제 사용 후기 및 성능 분석',
      keywordRepetition: 4,
      cta: '링크에서 자세한 정보 확인하세요',
      hashtags: ['#청소기', '#리뷰', '#비교', '#테스트'],
      length: '길음'
    },
    content: '안녕하세요! 오늘은 {제품명} 청소기의 성능을 자세히 테스트해보았습니다.\n\n📊 성능 테스트 결과:\n- 흡입력: {흡입력점수}/10\n- 소음: {소음점수}/10\n- 배터리: {배터리점수}/10\n- 편의성: {편의성점수}/10\n\n실제 사용 후기와 함께 성능을 분석해보았으니 영상 끝까지 시청해주세요!\n\n{CTA}\n\n{해시태그}'
  },
  {
    id: '3',
    name: '커피머신 블로그 템플릿',
    channel: 'blog',
    category: '커피머신',
    tone: '정보성',
    structure: {
      title: '커피머신 선택 가이드',
      subtitle: '초보자를 위한 완벽 가이드',
      keywordRepetition: 2,
      cta: '더 자세한 정보는 링크를 클릭하세요',
      hashtags: ['#커피머신', '#가이드', '#추천', '#커피'],
      length: '길음'
    },
    content: '커피머신을 구매하려고 하시나요? 오늘은 {제품명}에 대해 자세히 알아보겠습니다.\n\n☕ {제품명}의 특징:\n\n1. 추출 방식: {추출방식}\n2. 용량: {용량}\n3. 가격대: {가격대}\n4. 관리 난이도: {관리난이도}\n\n실제 사용 경험을 바탕으로 장단점을 정리해보았습니다.\n\n{CTA}\n\n{해시태그}'
  }
];

// 더미 캠페인 데이터
export const mockCampaigns: Campaign[] = [
  {
    id: '1',
    name: '2024 뷰티 캠페인',
    productName: '프리미엄 화장품 세트',
    category: '화장품',
    description: '새로운 화장품 라인업 홍보 캠페인',
    budget: 2000000,
    startDate: new Date('2024-01-01'),
    endDate: new Date('2024-02-01'),
    status: '진행중',
    influencers: [],
    templates: [mockTemplates[0]],
    performance: {
      totalViews: 0,
      totalClicks: 0,
      totalConversions: 0,
      totalRevenue: 0,
      totalCost: 0,
      roi: 0,
      ctr: 0,
      conversionRate: 0,
      topPerformers: []
    }
  },
  {
    id: '2',
    name: '스마트 청소기 캠페인',
    productName: 'AI 청소기',
    category: '청소기',
    description: '최신 AI 기술이 적용된 청소기 홍보',
    budget: 1500000,
    startDate: new Date('2024-01-15'),
    endDate: new Date('2024-02-15'),
    status: '준비중',
    influencers: [],
    templates: [mockTemplates[1]],
    performance: {
      totalViews: 0,
      totalClicks: 0,
      totalConversions: 0,
      totalRevenue: 0,
      totalCost: 0,
      roi: 0,
      ctr: 0,
      conversionRate: 0,
      topPerformers: []
    }
  }
]; 