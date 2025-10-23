/**
 * ErrorBoundary Component
 *
 * Catches React errors and displays a fallback UI
 */
import { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Alert,
} from '@mui/material';
import { ErrorOutline as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container maxWidth="md">
          <Box
            sx={{
              minHeight: '100vh',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              py: 4,
            }}
          >
            <Paper
              elevation={3}
              sx={{
                p: 4,
                textAlign: 'center',
                width: '100%',
              }}
            >
              <ErrorIcon
                sx={{
                  fontSize: 80,
                  color: 'error.main',
                  mb: 2,
                }}
              />
              <Typography variant="h4" component="h1" gutterBottom>
                Oops! Something went wrong
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                We're sorry for the inconvenience. An unexpected error occurred.
              </Typography>

              {this.state.error && (
                <Alert severity="error" sx={{ my: 3, textAlign: 'left' }}>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {this.state.error.toString()}
                  </Typography>
                </Alert>
              )}

              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <Alert severity="warning" sx={{ my: 3, textAlign: 'left' }}>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.75rem' }}>
                    {this.state.errorInfo.componentStack}
                  </Typography>
                </Alert>
              )}

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={this.handleReset}
                  size="large"
                >
                  Return to Home
                </Button>
              </Box>
            </Paper>
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}
