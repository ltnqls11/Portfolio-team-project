import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Campaign,
  AttachMoney,
  Visibility,
  Click,
  ShoppingCart,
  TrendingDown,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { mockCampaigns, mockInfluencers } from '../../data/mockData';

const Dashboard: React.FC = () => {
  const [campaignStats, setCampaignStats] = useState({
    totalCampaigns: 0,
    activeCampaigns: 0,
    totalInfluencers: 0,
    totalBudget: 0,
    totalViews: 0,
    totalClicks: 0,
    totalConversions: 0,
    totalRevenue: 0,
  });

  useEffect(() => {
    // 통계 계산
    const activeCampaigns = mockCampaigns.filter(c => c.status === '진행중').length;
    const totalBudget = mockCampaigns.reduce((sum, c) => sum + c.budget, 0);
    
    setCampaignStats({
      totalCampaigns: mockCampaigns.length,
      activeCampaigns,
      totalInfluencers: mockInfluencers.length,
      totalBudget,
      totalViews: 125000,
      totalClicks: 3200,
      totalConversions: 180,
      totalRevenue: 4500000,
    });
  }, []);

  // 차트 데이터
  const weeklyData = [
    { name: '월', views: 12000, clicks: 300, conversions: 18 },
    { name: '화', views: 15000, clicks: 380, conversions: 22 },
    { name: '수', views: 18000, clicks: 450, conversions: 25 },
    { name: '목', views: 14000, clicks: 350, conversions: 20 },
    { name: '금', views: 20000, clicks: 500, conversions: 30 },
    { name: '토', views: 22000, clicks: 550, conversions: 32 },
    { name: '일', views: 24000, clicks: 600, conversions: 35 },
  ];

  const categoryData = [
    { name: '화장품', value: 35, color: '#8884d8' },
    { name: '리빙제품', value: 25, color: '#82ca9d' },
    { name: '전자제품', value: 20, color: '#ffc658' },
    { name: '식품', value: 15, color: '#ff7300' },
    { name: '기타', value: 5, color: '#8dd1e1' },
  ];

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    trend?: number;
  }> = ({ title, value, icon, color, trend }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            {trend !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {trend > 0 ? (
                  <TrendingUp sx={{ color: 'success.main', fontSize: 16, mr: 0.5 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', fontSize: 16, mr: 0.5 }} />
                )}
                <Typography
                  variant="body2"
                  color={trend > 0 ? 'success.main' : 'error.main'}
                >
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        대시보드
      </Typography>

      {/* 통계 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 캠페인"
            value={campaignStats.totalCampaigns}
            icon={<Campaign sx={{ color: 'white' }} />}
            color="#1976d2"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="활성 캠페인"
            value={campaignStats.activeCampaigns}
            icon={<TrendingUp sx={{ color: 'white' }} />}
            color="#2e7d32"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 인플루언서"
            value={campaignStats.totalInfluencers}
            icon={<People sx={{ color: 'white' }} />}
            color="#ed6c02"
            trend={-3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 예산"
            value={`${(campaignStats.totalBudget / 1000000).toFixed(1)}M`}
            icon={<AttachMoney sx={{ color: 'white' }} />}
            color="#9c27b0"
            trend={15}
          />
        </Grid>
      </Grid>

      {/* 성과 지표 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 노출"
            value={campaignStats.totalViews.toLocaleString()}
            icon={<Visibility sx={{ color: 'white' }} />}
            color="#1976d2"
            trend={18}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 클릭"
            value={campaignStats.totalClicks.toLocaleString()}
            icon={<Click sx={{ color: 'white' }} />}
            color="#2e7d32"
            trend={22}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 전환"
            value={campaignStats.totalConversions.toLocaleString()}
            icon={<ShoppingCart sx={{ color: 'white' }} />}
            color="#ed6c02"
            trend={25}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 수익"
            value={`${(campaignStats.totalRevenue / 1000000).toFixed(1)}M`}
            icon={<AttachMoney sx={{ color: 'white' }} />}
            color="#9c27b0"
            trend={30}
          />
        </Grid>
      </Grid>

      {/* 차트 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                주간 성과 추이
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="views" stroke="#8884d8" name="노출" />
                  <Line type="monotone" dataKey="clicks" stroke="#82ca9d" name="클릭" />
                  <Line type="monotone" dataKey="conversions" stroke="#ffc658" name="전환" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                카테고리별 분포
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 최근 활동 */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                활성 캠페인
              </Typography>
              <List>
                {mockCampaigns.filter(c => c.status === '진행중').map((campaign) => (
                  <ListItem key={campaign.id} divider>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <Campaign />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={campaign.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {campaign.productName} • 예산: {campaign.budget.toLocaleString()}원
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Chip
                              label={campaign.status}
                              size="small"
                              color="success"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="body2" color="textSecondary">
                              {campaign.startDate.toLocaleDateString()} - {campaign.endDate.toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                상위 인플루언서
              </Typography>
              <List>
                {mockInfluencers
                  .sort((a, b) => b.followers - a.followers)
                  .slice(0, 5)
                  .map((influencer) => (
                    <ListItem key={influencer.id} divider>
                      <ListItemAvatar>
                        <Avatar src={influencer.profileImage} />
                      </ListItemAvatar>
                      <ListItemText
                        primary={influencer.name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              팔로워: {influencer.followers.toLocaleString()} • 참여율: {influencer.engagementRate}%
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                              {influencer.categories.map((category) => (
                                <Chip
                                  key={category}
                                  label={category}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mr: 0.5 }}
                                />
                              ))}
                            </Box>
                          </Box>
                        }
                      />
                      <Button size="small" variant="outlined">
                        연락하기
                      </Button>
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 