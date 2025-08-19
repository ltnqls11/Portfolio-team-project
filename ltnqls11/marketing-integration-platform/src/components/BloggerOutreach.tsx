import React, { useState, useEffect } from 'react';
import { PowerBlogger, BloggerOutreach as BloggerOutreachType } from '../types';
import { createBloggerOutreach, getBloggerOutreach, sendBulkEmails } from '../services/api';

interface BloggerOutreachProps {
  campaignId: string;
  selectedBloggers: PowerBlogger[];
}

const BloggerOutreach: React.FC<BloggerOutreachProps> = ({ campaignId, selectedBloggers }) => {
  const [outreachList, setOutreachList] = useState<BloggerOutreachType[]>([]);
  const [emailTemplate, setEmailTemplate] = useState({
    subject: '[협업 제안] 브랜드 체험단 모집',
    message: `안녕하세요, {blogger_name}님!

저희는 {product_name} 브랜드 마케팅을 담당하고 있습니다.

{blogger_name}님의 {category} 관련 콘텐츠를 보고 연락드리게 되었습니다.
현재 {subscriber_count}명의 구독자를 보유하고 계시며, 높은 참여율을 보이고 계시는 것을 확인했습니다.

📋 협업 내용:
- 제품: {product_name}
- 협업 형태: 체험 후기 포스팅
- 제공 혜택: 제품 무료 제공 + 협업비 {collaboration_rate}원
- 포스팅 기간: 제품 수령 후 1주일 이내

관심이 있으시다면 회신 부탁드립니다.
자세한 내용은 추가로 안내해드리겠습니다.

감사합니다.

---
마케팅 자동화 플랫폼
이메일: contact@marketing-platform.com`
  });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchOutreachList();
  }, [campaignId]);

  const fetchOutreachList = async () => {
    try {
      const data = await getBloggerOutreach(campaignId);
      setOutreachList(data);
    } catch (error) {
      console.error('아웃리치 목록 조회 실패:', error);
    }
  };

  const handleSendBulkEmails = async () => {
    const bloggersWithEmail = selectedBloggers.filter(blogger => blogger.contactEmail);
    
    if (bloggersWithEmail.length === 0) {
      alert('이메일 주소가 있는 블로거가 없습니다.');
      return;
    }

    if (!emailTemplate.subject.trim() || !emailTemplate.message.trim()) {
      alert('이메일 제목과 내용을 입력해주세요.');
      return;
    }

    setSending(true);
    try {
      const result = await sendBulkEmails(
        campaignId,
        bloggersWithEmail.map(b => b.id),
        JSON.stringify(emailTemplate)
      );
      
      alert(`${result.sent}개의 이메일이 성공적으로 발송되었습니다. (실패: ${result.failed}개)`);
      fetchOutreachList(); // 목록 새로고침
    } catch (error) {
      console.error('대량 이메일 발송 실패:', error);
      alert('이메일 발송에 실패했습니다.');
    } finally {
      setSending(false);
    }
  };

  const handleIndividualOutreach = async (blogger: PowerBlogger) => {
    try {
      const personalizedMessage = emailTemplate.message
        .replace(/{blogger_name}/g, blogger.bloggerName)
        .replace(/{category}/g, blogger.category)
        .replace(/{subscriber_count}/g, blogger.subscriberCount.toLocaleString())
        .replace(/{collaboration_rate}/g, blogger.collaborationRate?.toLocaleString() || '협의');

      await createBloggerOutreach({
        campaignId,
        bloggerId: blogger.id,
        contactMethod: 'email',
        subject: emailTemplate.subject,
        message: personalizedMessage,
        proposedRate: blogger.collaborationRate || 0,
        status: 'sent'
      });

      alert(`${blogger.bloggerName}님에게 개별 연락이 발송되었습니다.`);
      fetchOutreachList();
    } catch (error) {
      console.error('개별 아웃리치 실패:', error);
      alert('개별 연락 발송에 실패했습니다.');
    }
  };

  const getStatusColor = (status: BloggerOutreachType['status']) => {
    switch (status) {
      case 'sent': return 'bg-blue-100 text-blue-800';
      case 'opened': return 'bg-yellow-100 text-yellow-800';
      case 'replied': return 'bg-purple-100 text-purple-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: BloggerOutreachType['status']) => {
    switch (status) {
      case 'sent': return '발송됨';
      case 'opened': return '열람됨';
      case 'replied': return '답장받음';
      case 'accepted': return '수락됨';
      case 'rejected': return '거절됨';
      default: return '알 수 없음';
    }
  };

  const bloggersWithEmail = selectedBloggers.filter(blogger => blogger.contactEmail);
  const bloggersWithoutEmail = selectedBloggers.filter(blogger => !blogger.contactEmail);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">블로거 컨택 관리</h2>
        
        {/* 통계 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-700">선택된 블로거</h3>
            <p className="text-2xl font-bold text-blue-900">{selectedBloggers.length}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-green-700">이메일 보유</h3>
            <p className="text-2xl font-bold text-green-900">{bloggersWithEmail.length}</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-yellow-700">발송 완료</h3>
            <p className="text-2xl font-bold text-yellow-900">
              {outreachList.filter(o => o.status === 'sent').length}
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-purple-700">응답률</h3>
            <p className="text-2xl font-bold text-purple-900">
              {outreachList.length > 0 
                ? Math.round((outreachList.filter(o => ['replied', 'accepted'].includes(o.status)).length / outreachList.length) * 100)
                : 0}%
            </p>
          </div>
        </div>

        {/* 이메일 템플릿 */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">이메일 제목</label>
            <input
              type="text"
              value={emailTemplate.subject}
              onChange={(e) => setEmailTemplate({...emailTemplate, subject: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              이메일 내용
              <span className="text-xs text-gray-500 ml-2">
                (사용 가능한 변수: {'{blogger_name}'}, {'{category}'}, {'{subscriber_count}'}, {'{collaboration_rate}'})
              </span>
            </label>
            <textarea
              value={emailTemplate.message}
              onChange={(e) => setEmailTemplate({...emailTemplate, message: e.target.value})}
              rows={12}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
        </div>

        {/* 발송 버튼 */}
        <div className="flex gap-4 mt-6">
          <button
            onClick={handleSendBulkEmails}
            disabled={sending || bloggersWithEmail.length === 0}
            className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {sending ? '발송 중...' : `${bloggersWithEmail.length}명에게 일괄 발송`}
          </button>
        </div>

        {bloggersWithoutEmail.length > 0 && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ {bloggersWithoutEmail.length}명의 블로거는 이메일 주소가 없어 발송할 수 없습니다.
              개별적으로 블로그 메시지나 SNS DM을 통해 연락해보세요.
            </p>
          </div>
        )}
      </div>

      {/* 선택된 블로거 목록 */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">선택된 블로거 목록</h3>
        
        <div className="space-y-3">
          {selectedBloggers.map(blogger => {
            const outreach = outreachList.find(o => o.bloggerId === blogger.id);
            
            return (
              <div key={blogger.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{blogger.bloggerName}</h4>
                  <p className="text-sm text-gray-600">
                    {blogger.blogTitle} | {blogger.subscriberCount.toLocaleString()}명 구독
                  </p>
                  <p className="text-xs text-gray-500">
                    {blogger.contactEmail || '이메일 없음'} | 
                    참여율: {(blogger.engagementRate * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  {outreach ? (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(outreach.status)}`}>
                      {getStatusText(outreach.status)}
                    </span>
                  ) : blogger.contactEmail ? (
                    <button
                      onClick={() => handleIndividualOutreach(blogger)}
                      className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                      개별 발송
                    </button>
                  ) : (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                      연락처 없음
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 발송 내역 */}
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">발송 내역</h3>
        
        {outreachList.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            아직 발송된 연락이 없습니다.
          </div>
        ) : (
          <div className="space-y-3">
            {outreachList.map(outreach => {
              const blogger = selectedBloggers.find(b => b.id === outreach.bloggerId);
              
              return (
                <div key={outreach.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {blogger?.bloggerName || '알 수 없는 블로거'}
                      </h4>
                      <p className="text-sm text-gray-600">{outreach.subject}</p>
                      <p className="text-xs text-gray-500">
                        {outreach.sentAt.toLocaleDateString()} {outreach.sentAt.toLocaleTimeString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(outreach.status)}`}>
                      {getStatusText(outreach.status)}
                    </span>
                  </div>
                  
                  {outreach.response && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700">{outreach.response}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {outreach.responseAt?.toLocaleDateString()} 답장
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default BloggerOutreach;