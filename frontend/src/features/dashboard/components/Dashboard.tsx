/**
 * Dashboard Component
 *
 * Main dashboard view showing statistics and recent activity
 */
import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  People as PeopleIcon,
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { useAuthStore } from '@/features/auth/hooks/useAuthStore';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              bgcolor: `${color}.light`,
              color: `${color}.main`,
              borderRadius: 2,
              p: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();

  // TODO: Replace with actual data from API
  const stats = {
    totalClients: 0,
    totalCharts: 0,
    chartsThisMonth: 0,
    activeConsultants: 0,
  };

  const isLoading = false; // TODO: Add loading state

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('dashboard.welcome')}, {user?.firstName || user?.email}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {new Date().toLocaleDateString(undefined, {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('dashboard.totalClients')}
            value={stats.totalClients}
            icon={<PeopleIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('dashboard.totalCharts')}
            value={stats.totalCharts}
            icon={<DescriptionIcon />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('dashboard.chartsThisMonth')}
            value={stats.chartsThisMonth}
            icon={<TrendingUpIcon />}
            color="success"
          />
        </Grid>
        {user?.role === 'ADMIN' && (
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title={t('dashboard.activeConsultants')}
              value={stats.activeConsultants}
              icon={<PersonIcon />}
              color="info"
            />
          </Grid>
        )}
      </Grid>

      {/* Recent Activity Section */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {t('dashboard.recentClients')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('clients.noClients')}
            </Typography>
            {/* TODO: Add recent clients list */}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {t('dashboard.recentCharts')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('charts.noCharts')}
            </Typography>
            {/* TODO: Add recent charts list */}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};
