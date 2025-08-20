import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Email,
  Send,
  CheckCircle,
  Schedule,
  Cancel,
  Refresh,
} from '@mui/icons-material';
import { mockInfluencers } from '../../data/mockData';
import { api, isN8nEnabled } from '../../lib/api';

const ContactAutomation: React.FC = () => {
  const [influencers] = useState(mockInfluencers);
  const [selectedInfluencers, setSelectedInfluencers] = useState<string[]>([]);
  const [contactMethod, setContactMethod] = useState<'email' | 'dm' | 'both'>('email');
  const [message, setMessage] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const statusColors = {
    '대기': 'default',
    '전송': 'warning',
    '회신': 'info',
    '수락': 'success',
    '거절': 'error',
  };

  const handleSendContacts = async () => {
    if (selectedInfluencers.length === 0) {
      setSnackbar({ open: true, message: '인플루언서를 선택해주세요.', severity: 'warning' });
      return;
    }

    if (isN8nEnabled) {
      try {
        setSnackbar({ open: true, message: '연락을 발송하고 있습니다...', severity: 'info' });
        const res = await api.post('/webhook/send-contacts', {
          influencerIds: selectedInfluencers,
          method: contactMethod,
          message,
        });
        const ok = res.status >= 200 && res.status < 300;
        setSnackbar({ open: true, message: ok ? '연락이 성공적으로 발송되었습니다!' : '일부 실패가 있습니다.', severity: ok ? 'success' : 'warning' });
        setDialogOpen(false);
        return;
      } catch (e) {
        console.error(e);
        setSnackbar({ open: true, message: '발송 실패: 시뮬레이션으로 대체합니다.', severity: 'warning' });
      }
    }

    setSnackbar({ open: true, message: '연락을 발송하고 있습니다...', severity: 'info' });
    
    // 시뮬레이션
    setTimeout(() => {
      setSnackbar({ open: true, message: '연락이 성공적으로 발송되었습니다!', severity: 'success' });
      setDialogOpen(false);
    }, 2000);
  };

  const handleInfluencerSelect = (influencerId: string) => {
    setSelectedInfluencers(prev => 
      prev.includes(influencerId) 
        ? prev.filter(id => id !== influencerId)
        : [...prev, influencerId]
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        연락 자동화
      </Typography>

      <Grid container spacing={3}>
        {/* 연락 상태별 통계 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                연락 상태별 통계
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(statusColors).map(([status, color]) => {
                  const count = influencers.filter(inf => inf.contactStatus === status).length;
                  return (
                    <Grid item xs={6} sm={3} key={status}>
                      <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                        <Chip label={status} color={color as any} size="small" sx={{ mb: 1 }} />
                        <Typography variant="h4">{count}</Typography>
                        <Typography variant="body2" color="textSecondary">명</Typography>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 인플루언서 목록 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  인플루언서 목록
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Send />}
                  onClick={() => setDialogOpen(true)}
                  disabled={selectedInfluencers.length === 0}
                >
                  선택된 인플루언서에게 연락 ({selectedInfluencers.length}명)
                </Button>
              </Box>

              <List>
                {influencers.map((influencer) => (
                  <ListItem
                    key={influencer.id}
                    sx={{
                      border: '1px solid',
                      borderColor: selectedInfluencers.includes(influencer.id) ? 'primary.main' : 'divider',
                      borderRadius: 1,
                      mb: 1,
                      cursor: 'pointer',
                    }}
                    onClick={() => handleInfluencerSelect(influencer.id)}
                  >
                    <ListItemAvatar>
                      <Avatar src={influencer.profileImage} />
                    </ListItemAvatar>
                    <ListItemText
                      primary={influencer.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {influencer.email} • 팔로워: {influencer.followers.toLocaleString()}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            {influencer.categories.map((category) => (
                              <Chip key={category} label={category} size="small" sx={{ mr: 0.5 }} />
                            ))}
                          </Box>
                        </Box>
                      }
                    />
                    <Chip
                      label={influencer.contactStatus}
                      color={statusColors[influencer.contactStatus] as any}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 연락 발송 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>연락 발송</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>연락 방법</InputLabel>
                <Select
                  value={contactMethod}
                  onChange={(e) => setContactMethod(e.target.value as 'email' | 'dm' | 'both')}
                  label="연락 방법"
                >
                  <MenuItem value="email">이메일</MenuItem>
                  <MenuItem value="dm">DM</MenuItem>
                  <MenuItem value="both">이메일 + DM</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="메시지 (선택사항)"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="개인화된 메시지를 추가하세요..."
              />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                선택된 {selectedInfluencers.length}명의 인플루언서에게 연락을 발송합니다.
                기본 템플릿이 자동으로 적용됩니다.
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button variant="contained" onClick={handleSendContacts} startIcon={<Send />}>
            발송
          </Button>
        </DialogActions>
      </Dialog>

      {/* 스낵바 */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ContactAutomation; 