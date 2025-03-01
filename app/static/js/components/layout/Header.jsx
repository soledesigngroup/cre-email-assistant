import React from 'react';
import styled from 'styled-components';
import { useAuth } from '../../context/AuthContext';

const HeaderContainer = styled.header`
  background-color: var(--card-background);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
`;

const UserName = styled.span`
  font-weight: 500;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.9rem;
  
  &:hover {
    color: var(--primary-color);
  }
`;

const Header = () => {
  const { setIsAuthenticated } = useAuth();
  
  const handleLogout = () => {
    // In a real app, you would call a logout API endpoint
    setIsAuthenticated(false);
  };
  
  return (
    <HeaderContainer>
      <Logo>CRE Email Assistant</Logo>
      <UserInfo>
        <UserName>John Broker</UserName>
        <UserAvatar>JB</UserAvatar>
        <ActionButton onClick={handleLogout}>Logout</ActionButton>
      </UserInfo>
    </HeaderContainer>
  );
};

export default Header; 