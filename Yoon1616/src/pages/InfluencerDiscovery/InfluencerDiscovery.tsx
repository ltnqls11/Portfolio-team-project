import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Tooltip,
  Snackbar,
  Alert,
} from '@mui/material';
import { Search, Star, OpenInNew } from '@mui/icons-material';
import { api, isN8nEnabled } from '../../lib/api';
import { BloggerRecommendation } from '../../types';

const InfluencerDiscovery: React.FC = () => {
  const [productQuery, setProductQuery] = useState('');
  const [bloggers, setBloggers] = useState<BloggerRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: any }>({ open: false, message: '', severity: 'info' });

  const handleProductQueryRecommendation = async () => {
    if (!productQuery.trim()) {
      setSnackbar({ open: true, message: '제품명/키워드를 입력해주세요.', severity: 'warning' });
      return;
    }
    if (!isN8nEnabled) {
      setSnackbar({ open: true, message: 'n8n 연동이 필요합니다. .env에 VITE_N8N_BASE_URL을 설정해주세요.', severity: 'error' });
      return;
    }
    try {
      setLoading(true);
      const res = await api.get('/webhook/naver/blogger-recommendations', {
        params: { q: productQuery, limit: 20 },
      });
      const list: BloggerRecommendation[] = res.data?.bloggers ?? res.data ?? [];
      setBloggers(list);
      if (list.length === 0) {
        setSnackbar({ open: true, message: '추천 결과가 없습니다. 키워드를 변경해보세요.', severity: 'info' });
      }
    } catch (e) {
      console.error(e);
      setSnackbar({ open: true, message: '추천 조회 중 오류가 발생했습니다.', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        블로거 추천 (네이버 키워드 기반)
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                placeholder="제품명/키워드로 블로거 추천 (예: 무선청소기, 립스틱, 커피머신)"
                value={productQuery}
                onChange={(e) => setProductQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button fullWidth variant="contained" onClick={handleProductQueryRecommendation} disabled={loading}>
                {loading ? '분석 중...' : '키워드로 추천'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box sx={{ mb: 2 }}>
        <Typography variant="h6">검색 결과: {bloggers.length}명의 블로거</Typography>
      </Box>

      <Card>
        <CardContent>
          {bloggers.length === 0 ? (
            <Alert severity="info">키워드를 입력하고 추천을 실행하세요. n8n에서 크롤링/AI 분석을 수행한 뒤 결과를 반환합니다.</Alert>
          ) : (
            <List>
              {bloggers.map((b) => (
                <ListItem key={b.id} divider secondaryAction={
                  b.blogUrl ? (
                    <Tooltip title="블로그 열기">
                      <Button size="small" href={b.blogUrl} target="_blank" rel="noreferrer" startIcon={<OpenInNew />}>열기</Button>
                    </Tooltip>
                  ) : null
                }>
                  <ListItemAvatar>
                    <Avatar>{b.name.charAt(0)}</Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{b.name}</Typography>
                        <Chip label={`점수 ${Math.round(b.score)}`} size="small" icon={<Star sx={{ fontSize: 16 }} />} />
                      </Box>
                    }
                    secondary={
                      <Box>
                        {b.recentPost && (
                          <Typography variant="body2" color="textSecondary">
                            최근글: <a href={b.recentPost.url} target="_blank" rel="noreferrer">{b.recentPost.title}</a>
                          </Typography>
                        )}
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
                          {typeof b.estimatedReach === 'number' && (
                            <Chip label={`도달 추정 ${b.estimatedReach.toLocaleString()}`} size="small" />
                          )}
                          {typeof b.engagementScore === 'number' && (
                            <Chip label={`참여 점수 ${Math.round(b.engagementScore)}`} size="small" />
                          )}
                          {b.lastUpload && (
                            <Chip label={`최근 업로드 ${new Date(b.lastUpload).toLocaleDateString()}`} size="small" />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default InfluencerDiscovery; 