import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// 컴포넌트들
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import InfluencerDiscovery from './pages/InfluencerDiscovery/InfluencerDiscovery';
import CampaignManagement from './pages/CampaignManagement/CampaignManagement';
import PromotionGenerator from './pages/PromotionGenerator/PromotionGenerator';
import ContactAutomation from './pages/ContactAutomation/ContactAutomation';
import PerformanceAnalytics from './pages/PerformanceAnalytics/PerformanceAnalytics';
import NaverBlogGenerator from './pages/NaverBlogGenerator/NaverBlogGenerator';

// 테마 설정
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Noto Sans KR", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/influencers" element={<InfluencerDiscovery />} />
              <Route path="/campaigns" element={<CampaignManagement />} />
              <Route path="/promotion-generator" element={<PromotionGenerator />} />
              <Route path="/naver-blog" element={<NaverBlogGenerator />} />
              <Route path="/contact-automation" element={<ContactAutomation />} />
              <Route path="/analytics" element={<PerformanceAnalytics />} />
            </Routes>
          </Layout>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 