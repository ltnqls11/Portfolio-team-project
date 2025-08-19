# n8n 워크플로우 설계

## 워크플로우 개요

n8n을 사용하여 마케팅 플랫폼의 자동화 파이프라인을 구축합니다. 주요 워크플로우는 다음과 같습니다:

1. **캠페인 생성 → 문구 생성 → 승인 대기**
2. **인플루언서 발굴 및 연락 자동화**
3. **성과 데이터 수집 및 리포트 생성**
4. **이메일 마케팅 자동화**

## 1. 캠페인 문구 생성 워크플로우

### 트리거
- **Webhook**: 캠페인 생성 시 FastAPI에서 호출
- **URL**: `https://n8n.yourdomain.com/webhook/campaign-copy-generation`

### 노드 구성

#### 1. Webhook 노드
```json
{
  "name": "Campaign Created",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "campaign-copy-generation",
    "responseMode": "responseNode"
  }
}
```

#### 2. HTTP Request - 캠페인 데이터 조회
```json
{
  "name": "Get Campaign Data",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/campaigns/{{ $json.campaign_id }}",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{ $env.API_TOKEN }}"
    }
  }
}
```

#### 3. OpenAI 노드 - 문구 생성
```json
{
  "name": "Generate Copy Variants",
  "type": "n8n-nodes-base.openAi",
  "parameters": {
    "resource": "chat",
    "operation": "message",
    "model": "gpt-4",
    "messages": {
      "values": [
        {
          "role": "system",
          "content": "당신은 한국의 마케팅 카피라이터입니다. 주어진 정보를 바탕으로 채널별 맞춤 홍보 문구를 생성해주세요."
        },
        {
          "role": "user",
          "content": "제품: {{ $node['Get Campaign Data'].json.title }}\n목표: {{ $node['Get Campaign Data'].json.objective }}\n키워드: {{ $node['Get Campaign Data'].json.keywords.join(', ') }}\n채널: {{ $json.channel }}\n\n위 정보를 바탕으로 {{ $json.channel }}용 홍보 문구 3개를 생성해주세요."
        }
      ]
    }
  }
}
```

#### 4. Function 노드 - 문구 파싱 및 점수 계산
```javascript
// 생성된 문구를 파싱하고 점수를 계산
const response = $input.first().json.choices[0].message.content;
const variants = response.split('\n\n').filter(v => v.trim());

const processedVariants = variants.map((variant, index) => {
  const lines = variant.split('\n');
  const title = lines.find(l => l.startsWith('제목:'))?.replace('제목:', '').trim();
  const content = lines.find(l => l.startsWith('내용:'))?.replace('내용:', '').trim();
  const hashtags = lines.find(l => l.startsWith('해시태그:'))?.replace('해시태그:', '').trim().split(' ');
  
  // 간단한 점수 계산 (키워드 포함도, 길이 적절성 등)
  const keywordCount = $node['Get Campaign Data'].json.keywords.filter(k => 
    content?.toLowerCase().includes(k.toLowerCase())
  ).length;
  const score = Math.min(0.5 + (keywordCount * 0.1) + (Math.random() * 0.3), 1.0);
  
  return {
    campaign_id: $node['Get Campaign Data'].json.id,
    channel: $json.channel,
    title,
    content,
    hashtags,
    length: content?.length || 0,
    score: Math.round(score * 100) / 100,
    approved: false
  };
});

return processedVariants.map(variant => ({ json: variant }));
```

#### 5. HTTP Request - 문구 저장
```json
{
  "name": "Save Copy Variants",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/copy-variants",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{ $env.API_TOKEN }}",
      "Content-Type": "application/json"
    },
    "body": "={{ JSON.stringify($json) }}"
  }
}
```

#### 6. Slack 노드 - 알림 발송
```json
{
  "name": "Notify Team",
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "#marketing-alerts",
    "text": "새로운 캠페인 '{{ $node['Get Campaign Data'].json.title }}'의 문구가 생성되었습니다. 승인을 기다리고 있습니다."
  }
}
```

## 2. 인플루언서 아웃리치 워크플로우

### 트리거
- **Cron**: 매일 오전 9시 실행
- **Schedule**: `0 9 * * *`

### 노드 구성

#### 1. Schedule Trigger
```json
{
  "name": "Daily Outreach Check",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * *"
        }
      ]
    }
  }
}
```

#### 2. HTTP Request - 승인된 캠페인 조회
```json
{
  "name": "Get Approved Campaigns",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/campaigns?status=active&has_approved_copy=true",
    "method": "GET"
  }
}
```

#### 3. Split In Batches - 캠페인별 처리
```json
{
  "name": "Process Each Campaign",
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 1
  }
}
```

#### 4. HTTP Request - 적합한 크리에이터 검색
```json
{
  "name": "Find Matching Creators",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/creators/search",
    "method": "GET",
    "qs": {
      "category": "={{ $json.category }}",
      "min_followers": "1000",
      "max_followers": "100000",
      "min_engagement_rate": "0.02"
    }
  }
}
```

#### 5. Function 노드 - 이메일 템플릿 생성
```javascript
const campaign = $json;
const creators = $node['Find Matching Creators'].json.creators;

const emailTemplates = creators.map(creator => {
  const template = `
안녕하세요 ${creator.handle}님,

저희는 ${campaign.title} 캠페인을 진행하고 있는 마케팅 팀입니다.

귀하의 ${creator.category} 분야 콘텐츠를 보고 연락드리게 되었습니다.
현재 ${creator.followers.toLocaleString()}명의 팔로워를 보유하고 계시며,
${(creator.engagement_rate * 100).toFixed(2)}%의 높은 참여율을 보이고 계시네요.

캠페인 상세 내용:
- 제품/서비스: ${campaign.title}
- 캠페인 목표: ${campaign.objective}
- 예상 기간: ${new Date(campaign.start_at).toLocaleDateString()} ~ ${new Date(campaign.end_at).toLocaleDateString()}
- 채널: ${campaign.channels.join(', ')}

관심이 있으시다면 회신 부탁드립니다.

감사합니다.
`;

  return {
    creator_id: creator.id,
    campaign_id: campaign.id,
    email: creator.email,
    subject: `[협업 제안] ${campaign.title} 캠페인 참여 문의`,
    content: template,
    method: 'email',
    channel: campaign.channels[0]
  };
});

return emailTemplates.map(template => ({ json: template }));
```

#### 6. Gmail 노드 - 이메일 발송
```json
{
  "name": "Send Outreach Email",
  "type": "n8n-nodes-base.gmail",
  "parameters": {
    "resource": "message",
    "operation": "send",
    "to": "={{ $json.email }}",
    "subject": "={{ $json.subject }}",
    "message": "={{ $json.content }}"
  }
}
```

#### 7. HTTP Request - 아웃리치 기록 저장
```json
{
  "name": "Log Outreach",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/outreach",
    "method": "POST",
    "body": {
      "campaign_id": "={{ $json.campaign_id }}",
      "creator_id": "={{ $json.creator_id }}",
      "method": "email",
      "status": "sent",
      "channel": "={{ $json.channel }}"
    }
  }
}
```

## 3. 성과 데이터 수집 워크플로우

### 트리거
- **Cron**: 매일 오후 6시 실행
- **Schedule**: `0 18 * * *`

### 노드 구성

#### 1. Schedule Trigger
```json
{
  "name": "Daily Metrics Collection",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 18 * * *"
        }
      ]
    }
  }
}
```

#### 2. HTTP Request - 활성 결과물 조회
```json
{
  "name": "Get Active Deliverables",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/deliverables?status=active",
    "method": "GET"
  }
}
```

#### 3. Function 노드 - URL별 메트릭 수집
```javascript
// 각 플랫폼별 메트릭 수집 로직
const deliverables = $json.deliverables;
const results = [];

for (const deliverable of deliverables) {
  const url = deliverable.url;
  let metrics = {};
  
  if (url.includes('instagram.com')) {
    // Instagram 메트릭 수집 (API 또는 스크래핑)
    metrics = await collectInstagramMetrics(url);
  } else if (url.includes('blog.naver.com')) {
    // 네이버 블로그 메트릭 수집
    metrics = await collectNaverBlogMetrics(url);
  }
  
  results.push({
    deliverable_id: deliverable.id,
    metrics: metrics,
    collected_at: new Date().toISOString()
  });
}

return results.map(result => ({ json: result }));
```

#### 4. HTTP Request - 메트릭 업데이트
```json
{
  "name": "Update Metrics",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/deliverables/{{ $json.deliverable_id }}/metrics",
    "method": "PATCH",
    "body": "={{ JSON.stringify($json.metrics) }}"
  }
}
```

## 4. 주간 리포트 생성 워크플로우

### 트리거
- **Cron**: 매주 월요일 오전 8시
- **Schedule**: `0 8 * * 1`

### 노드 구성

#### 1. Schedule Trigger
```json
{
  "name": "Weekly Report Generation",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 8 * * 1"
        }
      ]
    }
  }
}
```

#### 2. HTTP Request - 주간 데이터 조회
```json
{
  "name": "Get Weekly Data",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://api:8000/api/analytics/weekly-report",
    "method": "GET",
    "qs": {
      "start_date": "={{ $now.minus({days: 7}).toISODate() }}",
      "end_date": "={{ $now.toISODate() }}"
    }
  }
}
```

#### 3. Function 노드 - 리포트 생성
```javascript
const data = $json;

const report = `
# 주간 마케팅 성과 리포트
생성일: ${new Date().toLocaleDateString('ko-KR')}

## 📊 주요 지표
- 활성 캠페인: ${data.active_campaigns}개
- 새로운 아웃리치: ${data.new_outreach}건
- 응답률: ${(data.response_rate * 100).toFixed(1)}%
- 총 노출수: ${data.total_impressions.toLocaleString()}회
- 총 참여수: ${data.total_engagements.toLocaleString()}회

## 📈 채널별 성과
${data.channel_performance.map(channel => 
  `- ${channel.name}: 노출 ${channel.impressions.toLocaleString()}회, 참여 ${channel.engagements.toLocaleString()}회`
).join('\n')}

## 🎯 상위 성과 캠페인
${data.top_campaigns.map((campaign, index) => 
  `${index + 1}. ${campaign.title} - 참여율 ${(campaign.engagement_rate * 100).toFixed(2)}%`
).join('\n')}

## 📝 주요 인사이트
${data.insights.join('\n- ')}
`;

return [{ json: { report, data } }];
```

#### 4. Gmail 노드 - 리포트 발송
```json
{
  "name": "Send Weekly Report",
  "type": "n8n-nodes-base.gmail",
  "parameters": {
    "resource": "message",
    "operation": "send",
    "to": "team@company.com",
    "subject": "주간 마케팅 성과 리포트 - {{ $now.toFormat('yyyy년 MM월 dd일') }}",
    "message": "={{ $json.report }}"
  }
}
```

## 환경 변수 설정

n8n에서 사용할 환경 변수들:

```env
# API 인증
API_TOKEN=your_api_token_here
API_BASE_URL=http://api:8000

# OpenAI
OPENAI_API_KEY=your_openai_key

# Gmail
GMAIL_USER=your_gmail@gmail.com
GMAIL_PASSWORD=your_app_password

# Slack
SLACK_TOKEN=your_slack_token

# Instagram API (향후)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# 네이버 API
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

## 워크플로우 모니터링

### 로그 및 알림
- 각 워크플로우 실행 결과를 Slack으로 알림
- 실패한 작업에 대한 재시도 로직 구현
- 중요한 메트릭 변화 시 즉시 알림

### 성능 최적화
- 배치 처리를 통한 API 호출 최소화
- 캐싱을 통한 중복 요청 방지
- 워크플로우 실행 시간 모니터링

이러한 n8n 워크플로우를 통해 마케팅 플랫폼의 주요 프로세스를 자동화하고, 효율적인 캠페인 관리를 실현할 수 있습니다.