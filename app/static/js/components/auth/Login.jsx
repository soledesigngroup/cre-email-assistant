import React from 'react';
import styled from 'styled-components';
import { authAPI } from '../../services/api';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--background-color);
`;

const LoginCard = styled.div`
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
  text-align: center;
`;

const Logo = styled.h1`
  color: var(--primary-color);
  margin-bottom: 1.5rem;
  font-size: 2rem;
`;

const Description = styled.p`
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.6;
`;

const LoginButton = styled.button`
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
  
  &:hover {
    background-color: var(--primary-dark);
  }
`;

const GoogleIcon = styled.span`
  margin-right: 0.5rem;
`;

const Login = () => {
  const handleLogin = () => {
    authAPI.login();
  };
  
  return (
    <LoginContainer>
      <LoginCard>
        <Logo>CRE Email Assistant</Logo>
        <Description>
          AI-powered email management system for commercial real estate brokers.
          Connect your Gmail account to get started.
        </Description>
        <LoginButton onClick={handleLogin}>
          <GoogleIcon>G</GoogleIcon>
          Sign in with Google
        </LoginButton>
      </LoginCard>
    </LoginContainer>
  );
};

export default Login; 