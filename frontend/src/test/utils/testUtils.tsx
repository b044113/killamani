import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'

// Create a custom theme for testing
const theme = createTheme()

// Create a test query client with disabled retries for faster tests
export const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
        staleTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

interface AllTheProvidersProps {
  children: React.ReactNode
}

// Wrapper with all necessary providers for testing
export const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  const queryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>{children}</ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

// Custom render function that includes all providers
export const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, { wrapper: AllTheProviders, ...options })
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
