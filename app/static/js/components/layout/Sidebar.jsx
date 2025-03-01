import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { transition } from '../common/animations';

const SidebarContainer = styled.aside`
  background-color: white;
  height: 100%;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: width 0.3s ease;
`;

const NavSection = styled.div`
  padding: ${props => props.isCollapsed ? '1rem 0.5rem' : '1rem'};
  
  &:not(:last-child) {
    border-bottom: 1px solid var(--border-color);
  }
`;

const SectionTitle = styled.h3`
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
  padding: 0 0.5rem;
  display: ${props => props.isCollapsed ? 'none' : 'block'};
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const NavItem = styled.li`
  margin-bottom: 0.25rem;
`;

const StyledNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  padding: ${props => props.isCollapsed ? '0.75rem 0.5rem' : '0.75rem 1rem'};
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  gap: ${props => props.isCollapsed ? '0' : '0.75rem'};
  ${transition()}
  
  &:hover {
    background-color: var(--hover-color);
    color: var(--text-primary);
  }
  
  &.active {
    background-color: var(--primary-light);
    color: var(--primary-color);
  }
  
  svg {
    font-size: 1.25rem;
    min-width: ${props => props.isCollapsed ? '100%' : '1.25rem'};
    text-align: center;
  }
  
  span {
    display: ${props => props.isCollapsed ? 'none' : 'inline'};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: ${props => props.isCollapsed ? 'center' : 'flex-start'};
  width: ${props => props.isCollapsed ? '100%' : 'auto'};
  padding: ${props => props.isCollapsed ? '0.75rem 0.5rem' : '0.75rem 1rem'};
  margin: ${props => props.isCollapsed ? '0' : '0 1rem'};
  border: none;
  border-radius: var(--border-radius);
  background-color: ${props => props.primary ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.primary ? 'white' : 'var(--text-secondary)'};
  font-weight: 500;
  cursor: pointer;
  gap: ${props => props.isCollapsed ? '0' : '0.75rem'};
  ${transition()}
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-dark)' : 'var(--hover-color)'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  svg {
    font-size: 1.25rem;
    min-width: ${props => props.isCollapsed ? '100%' : '1.25rem'};
    text-align: center;
  }
  
  span {
    display: ${props => props.isCollapsed ? 'none' : 'inline'};
  }
`;

const Sidebar = ({ isCollapsed }) => {
  const location = useLocation();
  
  return (
    <SidebarContainer>
      <NavSection isCollapsed={isCollapsed}>
        <SectionTitle isCollapsed={isCollapsed}>Main</SectionTitle>
        <NavList>
          <NavItem>
            <StyledNavLink 
              to="/inbox" 
              isCollapsed={isCollapsed}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <span role="img" aria-label="inbox">📥</span>
              <span>Inbox</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/capsules" 
              isCollapsed={isCollapsed}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <span role="img" aria-label="capsules">📦</span>
              <span>Capsules</span>
            </StyledNavLink>
          </NavItem>
        </NavList>
      </NavSection>
      
      <NavSection isCollapsed={isCollapsed}>
        <SectionTitle isCollapsed={isCollapsed}>Capsules</SectionTitle>
        <NavList>
          <NavItem>
            <StyledNavLink 
              to="/capsules?type=property" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/capsules' && location.search.includes('type=property') ? 'active' : ''}
            >
              <span role="img" aria-label="properties">🏢</span>
              <span>Properties</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/capsules?type=deal" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/capsules' && location.search.includes('type=deal') ? 'active' : ''}
            >
              <span role="img" aria-label="deals">💼</span>
              <span>Deals</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/capsules?type=client" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/capsules' && location.search.includes('type=client') ? 'active' : ''}
            >
              <span role="img" aria-label="clients">👥</span>
              <span>Clients</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/capsules?type=project" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/capsules' && location.search.includes('type=project') ? 'active' : ''}
            >
              <span role="img" aria-label="projects">📋</span>
              <span>Projects</span>
            </StyledNavLink>
          </NavItem>
        </NavList>
        
        <ActionButton 
          primary 
          isCollapsed={isCollapsed}
          onClick={() => window.location.href = '/capsules/new'}
        >
          <span role="img" aria-label="new">➕</span>
          <span>New Capsule</span>
        </ActionButton>
      </NavSection>
      
      <NavSection isCollapsed={isCollapsed}>
        <SectionTitle isCollapsed={isCollapsed}>Email</SectionTitle>
        <NavList>
          <NavItem>
            <StyledNavLink 
              to="/inbox?filter=unread" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/inbox' && location.search.includes('filter=unread') ? 'active' : ''}
            >
              <span role="img" aria-label="unread">📩</span>
              <span>Unread</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/inbox?filter=pinned" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/inbox' && location.search.includes('filter=pinned') ? 'active' : ''}
            >
              <span role="img" aria-label="pinned">📌</span>
              <span>Pinned</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/inbox?filter=archived" 
              isCollapsed={isCollapsed}
              className={location.pathname === '/inbox' && location.search.includes('filter=archived') ? 'active' : ''}
            >
              <span role="img" aria-label="archived">🗃️</span>
              <span>Archived</span>
            </StyledNavLink>
          </NavItem>
        </NavList>
      </NavSection>
      
      <NavSection isCollapsed={isCollapsed}>
        <SectionTitle isCollapsed={isCollapsed}>Settings</SectionTitle>
        <NavList>
          <NavItem>
            <StyledNavLink 
              to="/settings/profile" 
              isCollapsed={isCollapsed}
              className={location.pathname.includes('/settings/profile') ? 'active' : ''}
            >
              <span role="img" aria-label="profile">👤</span>
              <span>Profile</span>
            </StyledNavLink>
          </NavItem>
          <NavItem>
            <StyledNavLink 
              to="/settings/preferences" 
              isCollapsed={isCollapsed}
              className={location.pathname.includes('/settings/preferences') ? 'active' : ''}
            >
              <span role="img" aria-label="preferences">⚙️</span>
              <span>Preferences</span>
            </StyledNavLink>
          </NavItem>
        </NavList>
      </NavSection>
    </SidebarContainer>
  );
};

export default Sidebar; 