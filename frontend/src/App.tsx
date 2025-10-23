/**
 * Main App Component
 *
 * Application root with routing and theme provider
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages
import { LoginForm } from './features/auth/components/LoginForm';
import { useAuthStore } from './features/auth/hooks/useAuthStore';
import { Layout } from './shared/components/Layout';
import { ErrorBoundary } from './shared/components/ErrorBoundary';
import { Dashboard } from './features/dashboard/components/Dashboard';
import { ClientList } from './features/clients/components/ClientList';
import { ChartList } from './features/charts/components/ChartList';
import { Settings } from './features/settings/components/Settings';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1', // Indigo
    },
    secondary: {
      main: '#ec4899', // Pink
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <BrowserRouter>
            <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<div>Register (TODO)</div>} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/clients"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ClientList />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/charts"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChartList />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
