import { Routes, Route } from 'react-router-dom'
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material'
import Dashboard from './pages/Dashboard'
import CampaignManagement from './pages/CampaignManagement'
import InfluencerManagement from './pages/InfluencerManagement'

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Marketing Automation RPA
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/campaigns" element={<CampaignManagement />} />
          <Route path="/influencers" element={<InfluencerManagement />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App