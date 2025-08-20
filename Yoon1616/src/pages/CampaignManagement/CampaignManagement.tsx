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
} from '@mui/material';
import {
  Add,
  Campaign,
  TrendingUp,
  People,
  AttachMoney,
} from '@mui/icons-material';
import { mockCampaigns } from '../../data/mockData';

const CampaignManagement: React.FC = () => {
  const [campaigns] = useState(mockCampaigns);
  const [dialogOpen, setDialogOpen] = useState(false);

  const statusColors = {
    '준비중': 'warning',
    '진행중': 'success',
    '완료': 'info',
    '중단': 'error',
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          캠페인 관리
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          새 캠페인 생성
        </Button>
      </Box>

      <Grid container spacing={3}>
        {campaigns.map((campaign) => (
          <Grid item xs={12} md={6} key={campaign.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6">{campaign.name}</Typography>
                  <Chip
                    label={campaign.status}
                    color={statusColors[campaign.status] as any}
                    size="small"
                  />
                </Box>
                
                <Typography color="textSecondary" gutterBottom>
                  {campaign.productName}
                </Typography>
                
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {campaign.description}
                </Typography>

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <AttachMoney sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">
                        예산: {campaign.budget.toLocaleString()}원
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <People sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">
                        인플루언서: {campaign.influencers.length}명
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {campaign.startDate.toLocaleDateString()} - {campaign.endDate.toLocaleDateString()}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button size="small" variant="outlined">
                    상세보기
                  </Button>
                  <Button size="small" variant="outlined">
                    성과보기
                  </Button>
                  <Button size="small" variant="contained">
                    관리하기
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>새 캠페인 생성</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="캠페인명" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="제품명" />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>카테고리</InputLabel>
                <Select label="카테고리">
                  <MenuItem value="화장품">화장품</MenuItem>
                  <MenuItem value="리빙제품">리빙제품</MenuItem>
                  <MenuItem value="전자제품">전자제품</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="설명" />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth type="number" label="예산" />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth type="date" label="시작일" InputLabelProps={{ shrink: true }} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button variant="contained">생성</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CampaignManagement; 