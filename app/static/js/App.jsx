import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { createGlobalStyle, ThemeProvider } from 'styled-components';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/auth/Login';
import NotFound from './components/common/NotFound';
import Layout from './components/layout/Layout';
import Inbox from './components/inbox/Inbox';
import Capsules from './components/capsules/Capsules';
import { pageTransitionIn, pageTransitionOut } from './components/common/animations';

// Global styles
const GlobalStyle = createGlobalStyle`
  :root {
    --primary-color: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #dbeafe;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --background-color: #f8fafc;
    --card-background: #ffffff;
    --border-color: #e2e8f0;
    --hover-color: #f1f5f9;
    --box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --border-radius: 0.375rem;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }
  
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: var(--font-family);
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.5;
  }
  
  a {
    color: var(--primary-color);
    text-decoration: none;
  }
  
  button {
    cursor: pointer;
  }
  
  ${pageTransitionIn}
  ${pageTransitionOut}
`;

// Theme
const theme = {
  colors: {
    primary: 'var(--primary-color)',
    primaryDark: 'var(--primary-dark)',
    primaryLight: 'var(--primary-light)',
    secondary: 'var(--secondary-color)',
    success: 'var(--success-color)',
    warning: 'var(--warning-color)',
    danger: 'var(--danger-color)',
    textPrimary: 'var(--text-primary)',
    textSecondary: 'var(--text-secondary)',
    background: 'var(--background-color)',
    cardBackground: 'var(--card-background)',
    borderColor: 'var(--border-color)',
    hoverColor: 'var(--hover-color)',
  },
  shadows: {
    small: 'var(--box-shadow)',
    medium: '0 4px 6px rgba(0, 0, 0, 0.1)',
    large: '0 10px 15px rgba(0, 0, 0, 0.1)',
  },
  borderRadius: 'var(--border-radius)',
  transitions: {
    default: 'all 0.3s ease',
    fast: 'all 0.15s ease',
    slow: 'all 0.5s ease',
  },
};

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        <div style={{ 
          border: '3px solid rgba(0, 0, 0, 0.1)',
          borderTop: '3px solid var(--primary-color)',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          animation: 'spin 1s linear infinite'
        }} />
        <p>Loading...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/inbox" />} />
              <Route path="inbox" element={<Inbox />} />
              <Route path="inbox/:id" element={<Inbox />} />
              <Route path="capsules" element={<Capsules />} />
              <Route path="capsules/:id" element={<Capsules />} />
              <Route path="capsules/new" element={<Capsules />} />
              <Route path="capsules/:id/edit" element={<Capsules />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App; 