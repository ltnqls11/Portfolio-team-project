import React, { useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, TextField, Button, Chip, Snackbar, Alert, Checkbox, FormControlLabel } from '@mui/material';
import { api, isN8nEnabled } from '../../lib/api';
import { NaverBlogPostSpec, GeneratedNaverBlogPost } from '../../types';

const tones = ['친근한', '전문적인', '유머러스한', '감성적인', '정보성'] as const;
const lengths = ['짧음', '보통', '길음'] as const;

const NaverBlogGenerator: React.FC = () => {
  const [spec, setSpec] = useState<NaverBlogPostSpec>({
    productQuery: '',
    tone: '친근한',
    length: '보통',
    keywords: [],
    hashtags: [],
    cta: '지금 바로 자세히 보기',
    includeSubheadings: true,
  });
  const [keywordsText, setKeywordsText] = useState('');
  const [hashtagsText, setHashtagsText] = useState('');
  const [result, setResult] = useState<GeneratedNaverBlogPost | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: any }>({ open: false, message: '', severity: 'info' });
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!spec.productQuery.trim()) {
      setSnackbar({ open: true, message: '제품명/키워드를 입력해주세요.', severity: 'warning' });
      return;
    }

    const payload: NaverBlogPostSpec = {
      ...spec,
      keywords: keywordsText.split(',').map(s => s.trim()).filter(Boolean),
      hashtags: hashtagsText.split(',').map(s => s.trim().replace(/^#?/, '#')).filter(Boolean),
    };

    if (!isN8nEnabled) {
      setSnackbar({ open: true, message: 'n8n 연동이 설정되어 있지 않습니다. VITE_N8N_BASE_URL을 설정해주세요.', severity: 'error' });
      return;
    }

    try {
      setLoading(true);
      const res = await api.post('/webhook/naver/generate-post', payload);
      const data = res.data as GeneratedNaverBlogPost;
      setResult({ ...data, generatedAt: data.generatedAt ? new Date(data.generatedAt) : new Date() });
      setSnackbar({ open: true, message: '네이버 블로그 포스트가 생성되었습니다.', severity: 'success' });
    } catch (e) {
      console.error(e);
      setSnackbar({ open: true, message: '생성 중 오류가 발생했습니다.', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>네이버 블로그 포스트 생성</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>작성 설정</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="제품명/키워드"
                    placeholder="예: 무선청소기, 립스틱, 커피머신"
                    value={spec.productQuery}
                    onChange={(e) => setSpec({ ...spec, productQuery: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="톤"
                    value={spec.tone}
                    onChange={(e) => setSpec({ ...spec, tone: e.target.value as any })}
                    select
                    SelectProps={{ native: true }}
                  >
                    {tones.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="길이"
                    value={spec.length}
                    onChange={(e) => setSpec({ ...spec, length: e.target.value as any })}
                    select
                    SelectProps={{ native: true }}
                  >
                    {lengths.map(l => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="핵심 키워드(쉼표 구분)"
                    placeholder="예: 강한 흡입력, 가벼운 무게"
                    value={keywordsText}
                    onChange={(e) => setKeywordsText(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="해시태그(쉼표 구분)"
                    placeholder="#무선청소기, #흡입력"
                    value={hashtagsText}
                    onChange={(e) => setHashtagsText(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="CTA"
                    placeholder="지금 바로 자세히 보기"
                    value={spec.cta}
                    onChange={(e) => setSpec({ ...spec, cta: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Checkbox checked={spec.includeSubheadings} onChange={(e) => setSpec({ ...spec, includeSubheadings: e.target.checked })} />}
                    label="소제목 포함"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button variant="contained" onClick={handleGenerate} disabled={loading} fullWidth>
                    {loading ? '생성 중...' : '네이버 블로그 문구 생성'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>결과</Typography>
              {!result ? (
                <Alert severity="info">설정을 입력하고 생성 버튼을 눌러주세요.</Alert>
              ) : (
                <Box>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    생성일: {result.generatedAt.toLocaleString()}
                  </Typography>
                  {result.outline?.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>소제목</Typography>
                      {result.outline.map((h, idx) => (
                        <Chip key={idx} label={h} sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </Box>
                  )}
                  <Box sx={{
                    backgroundColor: 'grey.50',
                    p: 2,
                    borderRadius: 1,
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace',
                    fontSize: '0.95rem',
                  }}>
                    {result.content}
                  </Box>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">키워드</Typography>
                    {result.keywords.map((k, i) => (<Chip key={i} label={k} sx={{ mr: 0.5, mb: 0.5 }} />))}
                  </Box>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">해시태그</Typography>
                    {result.hashtags.map((k, i) => (<Chip key={i} label={k} sx={{ mr: 0.5, mb: 0.5 }} />))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar open={snackbar.open} autoHideDuration={3000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default NaverBlogGenerator;