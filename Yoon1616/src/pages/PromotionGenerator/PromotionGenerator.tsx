import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  AutoAwesome,
  ExpandMore,
  ContentCopy,
  Edit,
  Preview,
  Save,
  Delete,
  Instagram,
  YouTube,
  Language,
  Facebook,
  Twitter,
} from '@mui/icons-material';
import { mockTemplates } from '../../data/mockData';
import { PromotionTemplate, ProductCategory, GeneratedPromotion } from '../../types';
import { PromotionGenerator } from '../../services/promotionGenerator';
import { api, isN8nEnabled } from '../../lib/api';

const PromotionGeneratorPage: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<PromotionTemplate | null>(null);
  const [productInfo, setProductInfo] = useState({
    name: '',
    category: '화장품' as ProductCategory,
    features: ['', '', ''],
    benefits: ['', '', ''],
    price: 0,
    discount: 0,
    url: '',
  });
  const [influencerInfo, setInfluencerInfo] = useState({
    name: '',
    tone: '친근한',
  });
  const [generatedPromotions, setGeneratedPromotions] = useState<GeneratedPromotion[]>([]);
  const [previewDialog, setPreviewDialog] = useState(false);
  const [selectedPromotion, setSelectedPromotion] = useState<GeneratedPromotion | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const categories: ProductCategory[] = [
    '화장품', '리빙제품', '청소기', '커피머신', '패션', '전자제품', '식품', '건강식품'
  ];

  const tones = ['친근한', '전문적인', '유머러스한', '감성적인', '정보성'];
  const channels = ['instagram', 'youtube', 'blog', 'facebook', 'twitter'];

  const channelIcons = {
    instagram: <Instagram />,
    youtube: <YouTube />,
    blog: <Language />,
    facebook: <Facebook />,
    twitter: <Twitter />,
  };

  const handleGeneratePromotion = async () => {
    if (!selectedTemplate) {
      setSnackbar({ open: true, message: '템플릿을 선택해주세요.', severity: 'warning' });
      return;
    }

    if (!productInfo.name || !productInfo.url) {
      setSnackbar({ open: true, message: '제품명과 URL을 입력해주세요.', severity: 'warning' });
      return;
    }

    if (isN8nEnabled) {
      try {
        const res = await api.post('/webhook/generate-promo', {
          templateId: selectedTemplate.id,
          product: productInfo,
          tone: influencerInfo.tone,
          channel: selectedTemplate.channel,
        });
        const content: string = res.data?.content ?? '';
        const newPromotion: GeneratedPromotion = {
          id: `gen_${Date.now()}`,
          templateId: selectedTemplate.id,
          influencerId: 'temp',
          content,
          channel: selectedTemplate.channel,
          generatedDate: new Date(),
          status: '생성됨',
        };
        setGeneratedPromotions([newPromotion, ...generatedPromotions]);
        setSnackbar({ open: true, message: '홍보 문구가 생성되었습니다!', severity: 'success' });
        return;
      } catch (e) {
        console.error(e);
        setSnackbar({ open: true, message: '생성 실패: 로컬 생성으로 대체합니다.', severity: 'warning' });
      }
    }

    const promotion = PromotionGenerator.generateFromTemplate(
      selectedTemplate,
      productInfo,
      influencerInfo
    );

    setGeneratedPromotions([promotion, ...generatedPromotions]);
    setSnackbar({ open: true, message: '홍보 문구가 생성되었습니다!', severity: 'success' });
  };

  const handleCopyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content);
    setSnackbar({ open: true, message: '클립보드에 복사되었습니다!', severity: 'success' });
  };

  const handlePreview = (promotion: GeneratedPromotion) => {
    setSelectedPromotion(promotion);
    setPreviewDialog(true);
  };

  const handleSaveTemplate = () => {
    // 템플릿 저장 로직
    setSnackbar({ open: true, message: '템플릿이 저장되었습니다!', severity: 'success' });
  };

  const handleOptimizeForChannel = (promotion: GeneratedPromotion) => {
    const optimizedContent = PromotionGenerator.optimizeForChannel(
      promotion.content,
      promotion.channel
    );
    
    const optimizedPromotion = {
      ...promotion,
      content: optimizedContent,
    };

    setGeneratedPromotions(generatedPromotions.map(p => 
      p.id === promotion.id ? optimizedPromotion : p
    ));
    
    setSnackbar({ open: true, message: '채널별 최적화가 완료되었습니다!', severity: 'success' });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        홍보 문구 생성
      </Typography>

      <Grid container spacing={3}>
        {/* 제품 정보 입력 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                제품 정보
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="제품명"
                    value={productInfo.name}
                    onChange={(e) => setProductInfo({ ...productInfo, name: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>카테고리</InputLabel>
                    <Select
                      value={productInfo.category}
                      onChange={(e) => setProductInfo({ ...productInfo, category: e.target.value as ProductCategory })}
                      label="카테고리"
                    >
                      {categories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {category}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="제품 URL"
                    value={productInfo.url}
                    onChange={(e) => setProductInfo({ ...productInfo, url: e.target.value })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="가격"
                    type="number"
                    value={productInfo.price}
                    onChange={(e) => setProductInfo({ ...productInfo, price: Number(e.target.value) })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="할인율 (%)"
                    type="number"
                    value={productInfo.discount}
                    onChange={(e) => setProductInfo({ ...productInfo, discount: Number(e.target.value) })}
                  />
                </Grid>
              </Grid>

              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>제품 특징 및 장점</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>주요 특징</Typography>
                      {productInfo.features.map((feature, index) => (
                        <TextField
                          key={index}
                          fullWidth
                          label={`특징 ${index + 1}`}
                          value={feature}
                          onChange={(e) => {
                            const newFeatures = [...productInfo.features];
                            newFeatures[index] = e.target.value;
                            setProductInfo({ ...productInfo, features: newFeatures });
                          }}
                          sx={{ mb: 1 }}
                        />
                      ))}
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>주요 장점</Typography>
                      {productInfo.benefits.map((benefit, index) => (
                        <TextField
                          key={index}
                          fullWidth
                          label={`장점 ${index + 1}`}
                          value={benefit}
                          onChange={(e) => {
                            const newBenefits = [...productInfo.benefits];
                            newBenefits[index] = e.target.value;
                            setProductInfo({ ...productInfo, benefits: newBenefits });
                          }}
                          sx={{ mb: 1 }}
                        />
                      ))}
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Grid>

        {/* 인플루언서 정보 및 템플릿 선택 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                인플루언서 정보
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="인플루언서 이름"
                    value={influencerInfo.name}
                    onChange={(e) => setInfluencerInfo({ ...influencerInfo, name: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>톤앤매너</InputLabel>
                    <Select
                      value={influencerInfo.tone}
                      onChange={(e) => setInfluencerInfo({ ...influencerInfo, tone: e.target.value })}
                      label="톤앤매너"
                    >
                      {tones.map((tone) => (
                        <MenuItem key={tone} value={tone}>
                          {tone}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                템플릿 선택
              </Typography>
              <List>
                {mockTemplates.map((template) => (
                  <ListItem
                    key={template.id}
                    button
                    selected={selectedTemplate?.id === template.id}
                    onClick={() => setSelectedTemplate(template)}
                    sx={{
                      border: '1px solid',
                      borderColor: selectedTemplate?.id === template.id ? 'primary.main' : 'divider',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <ListItemIcon>
                      {channelIcons[template.channel]}
                    </ListItemIcon>
                    <ListItemText
                      primary={template.name}
                      secondary={
                        <Box>
                          <Chip label={template.category} size="small" sx={{ mr: 1 }} />
                          <Chip label={template.tone} size="small" variant="outlined" />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>

              <Button
                fullWidth
                variant="contained"
                startIcon={<AutoAwesome />}
                onClick={handleGeneratePromotion}
                sx={{ mt: 2 }}
              >
                홍보 문구 생성
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* 생성된 홍보 문구 목록 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                생성된 홍보 문구
              </Typography>
              {generatedPromotions.length === 0 ? (
                <Alert severity="info">
                  제품 정보와 템플릿을 선택한 후 홍보 문구를 생성해주세요.
                </Alert>
              ) : (
                <List>
                  {generatedPromotions.map((promotion) => (
                    <ListItem
                      key={promotion.id}
                      sx={{
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 2,
                        flexDirection: 'column',
                        alignItems: 'stretch',
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {channelIcons[promotion.channel as keyof typeof channelIcons]}
                          <Typography variant="subtitle1" sx={{ ml: 1 }}>
                            {promotion.channel.toUpperCase()} 홍보 문구
                          </Typography>
                        </Box>
                        <Box>
                          <Tooltip title="미리보기">
                            <IconButton onClick={() => handlePreview(promotion)}>
                              <Preview />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="채널별 최적화">
                            <IconButton onClick={() => handleOptimizeForChannel(promotion)}>
                              <AutoAwesome />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="복사">
                            <IconButton onClick={() => handleCopyToClipboard(promotion.content)}>
                              <ContentCopy />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      <Box
                        sx={{
                          backgroundColor: 'grey.50',
                          p: 2,
                          borderRadius: 1,
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'monospace',
                          fontSize: '0.875rem',
                        }}
                      >
                        {promotion.content}
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                        <Typography variant="caption" color="textSecondary">
                          생성일: {promotion.generatedDate.toLocaleString()}
                        </Typography>
                        <Chip label={promotion.status} size="small" color="primary" />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 미리보기 다이얼로그 */}
      <Dialog
        open={previewDialog}
        onClose={() => setPreviewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedPromotion && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {channelIcons[selectedPromotion.channel as keyof typeof channelIcons]}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  {selectedPromotion.channel.toUpperCase()} 홍보 문구 미리보기
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box
                sx={{
                  backgroundColor: 'grey.50',
                  p: 3,
                  borderRadius: 1,
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '1rem',
                  lineHeight: 1.6,
                }}
              >
                {selectedPromotion.content}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setPreviewDialog(false)}>닫기</Button>
              <Button
                variant="contained"
                startIcon={<ContentCopy />}
                onClick={() => handleCopyToClipboard(selectedPromotion.content)}
              >
                복사
              </Button>
            </DialogActions>
          </>
        )}
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

export default PromotionGeneratorPage; 