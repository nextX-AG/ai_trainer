import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ProjectDashboard } from './components/ProjectDashboard';

const queryClient = new QueryClient();

const theme = createTheme({
    palette: {
        mode: 'dark',
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <ProjectDashboard projectId="test-project" />
            </ThemeProvider>
        </QueryClientProvider>
    );
}

export default App; 