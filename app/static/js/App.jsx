import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';

// Components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Login from './components/auth/Login';
import Inbox from './components/inbox/Inbox';
import CapsuleDetail from './components/capsules/CapsuleDetail';
import NotFound from './components/common/NotFound';

// Context
import { AuthProvider } from './context/AuthContext';

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  margin-left: 250px; // Width of sidebar
`;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const checkAuth = async () => {
      try {
        const response = await fetch('/auth/test');
        const data = await response.json();
        setIsAuthenticated(data.authenticated);
      } catch (error) {
        console.error('Authentication check failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthProvider value={{ isAuthenticated, setIsAuthenticated }}>
      {isAuthenticated ? (
        <AppContainer>
          <Sidebar />
          <div>
            <Header />
            <MainContent>
              <Routes>
                <Route path="/" element={<Navigate to="/inbox" />} />
                <Route path="/inbox" element={<Inbox />} />
                <Route path="/capsule/:id" element={<CapsuleDetail />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </MainContent>
          </div>
        </AppContainer>
      ) : (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </AuthProvider>
  );
}

export default App; 