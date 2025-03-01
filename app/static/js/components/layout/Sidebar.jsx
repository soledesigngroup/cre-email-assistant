import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const SidebarContainer = styled.aside`
  width: 250px;
  background-color: var(--card-background);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.1);
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  padding: 0 1.5rem;
  margin-bottom: 2rem;
`;

const NavMenu = styled.nav`
  margin-top: 1rem;
`;

const NavItem = styled.div`
  padding: 0.75rem 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: ${props => props.active ? 'var(--primary-color)' : 'var(--text-primary)'};
  background-color: ${props => props.active ? 'rgba(37, 99, 235, 0.1)' : 'transparent'};
  border-left: ${props => props.active ? '3px solid var(--primary-color)' : '3px solid transparent'};
  
  &:hover {
    background-color: rgba(37, 99, 235, 0.05);
  }
`;

const NavLink = styled(Link)`
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
`;

const ActionButton = styled.button`
  margin: 1.5rem;
  padding: 0.75rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  &:hover {
    background-color: var(--primary-dark);
  }
`;

const Sidebar = () => {
  const location = useLocation();
  
  return (
    <SidebarContainer>
      <Logo>CRE Email Assistant</Logo>
      
      <ActionButton onClick={() => window.location.href = '/auth/login'}>
        Sync Emails
      </ActionButton>
      
      <NavMenu>
        <NavItem active={location.pathname === '/inbox'}>
          <NavLink to="/inbox">📥 Inbox</NavLink>
        </NavItem>
        <NavItem active={location.pathname === '/capsules'}>
          <NavLink to="/capsules">📦 Capsules</NavLink>
        </NavItem>
        <NavItem active={location.pathname === '/properties'}>
          <NavLink to="/properties">🏢 Properties</NavLink>
        </NavItem>
        <NavItem active={location.pathname === '/contacts'}>
          <NavLink to="/contacts">👥 Contacts</NavLink>
        </NavItem>
        <NavItem active={location.pathname === '/settings'}>
          <NavLink to="/settings">⚙️ Settings</NavLink>
        </NavItem>
      </NavMenu>
    </SidebarContainer>
  );
};

export default Sidebar; 