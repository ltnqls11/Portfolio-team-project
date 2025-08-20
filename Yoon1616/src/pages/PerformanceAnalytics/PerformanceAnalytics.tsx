import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Visibility,
  Click,
  ShoppingCart,
  AttachMoney,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const PerformanceAnalytics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  // 샘플 데이터
  const performanceData = [
    { name: '1주', views: 12000, clicks: 300, conversions: 18, revenue: 900000 },
    { name: '2주', views: 15000, clicks: 380, conversions: 22, revenue: 1100000 },
    { name: '3주', views: 18000, clicks: 450, conversions: 25, revenue: 1250000 },
    { name: '4주', views: 22000, clicks: 550, conversions: 32, revenue: 1600000 },
  ];

  const influencerPerformance = [
    { name: '김뷰티', views: 25000, clicks: 1200, conversions: 45, revenue: 2250000 },
    { name: '리빙마스터', views: 18000, clicks: 950, conversions: 38, revenue: 1900000 },
    { name: '커피러버', views: 22000, clicks: 1100, conversions: 42, revenue: 2100000 },
    { name: '테크리뷰어', views: 35000, clicks: 1800, conversions: 55, revenue: 2750000 },
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          성과 분석
        </Typography>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>기간</InputLabel>
          <Select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            label="기간"
          >
            <MenuItem value="7">7일</MenuItem>
            <MenuItem value="30">30일</MenuItem>
            <MenuItem value="90">90일</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* 주요 지표 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 노출"
            value="125,000"
            icon={<Visibility sx={{ color: 'white' }} />}
            color="#1976d2"
            trend={18}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 클릭"
            value="3,200"
            icon={<Click sx={{ color: 'white' }} />}
            color="#2e7d32"
            trend={22}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 전환"
            value="180"
            icon={<ShoppingCart sx={{ color: 'white' }} />}
            color="#ed6c02"
            trend={25}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 수익"
            value="4.5M"
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
                성과 추이
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
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

      {/* 인플루언서별 성과 */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                인플루언서별 성과
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>인플루언서</TableCell>
                      <TableCell align="right">노출</TableCell>
                      <TableCell align="right">클릭</TableCell>
                      <TableCell align="right">전환</TableCell>
                      <TableCell align="right">수익</TableCell>
                      <TableCell align="right">CTR</TableCell>
                      <TableCell align="right">전환율</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {influencerPerformance.map((row) => {
                      const ctr = ((row.clicks / row.views) * 100).toFixed(2);
                      const conversionRate = ((row.conversions / row.clicks) * 100).toFixed(2);
                      return (
                        <TableRow key={row.name}>
                          <TableCell component="th" scope="row">
                            {row.name}
                          </TableCell>
                          <TableCell align="right">{row.views.toLocaleString()}</TableCell>
                          <TableCell align="right">{row.clicks.toLocaleString()}</TableCell>
                          <TableCell align="right">{row.conversions.toLocaleString()}</TableCell>
                          <TableCell align="right">{row.revenue.toLocaleString()}원</TableCell>
                          <TableCell align="right">{ctr}%</TableCell>
                          <TableCell align="right">{conversionRate}%</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                인플루언서별 수익 비교
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={influencerPerformance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="revenue" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PerformanceAnalytics; 