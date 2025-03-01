import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../../context/AuthContext';
import { transition, hoverLift } from '../common/animations';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 64px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const MenuButton = styled.button`
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  ${transition()}
  
  &:hover {
    background-color: var(--hover-color);
    color: var(--text-primary);
  }
`;

const Logo = styled(Link)`
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  span {
    color: var(--text-primary);
  }
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background-color: var(--primary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1rem;
`;

const NavContainer = styled.nav`
  display: flex;
  align-items: center;
  gap: 1.5rem;
`;

const NavLink = styled(Link)`
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
  ${transition()}
  
  &:hover, &.active {
    color: var(--primary-color);
  }
  
  &.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: var(--primary-color);
    border-radius: 2px;
  }
`;

const UserContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  ${transition()}
  
  &:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
`;

const UserMenu = styled.div`
  position: absolute;
  top: 60px;
  right: 1.5rem;
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 200px;
  z-index: 100;
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
  
  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const UserMenuItem = styled.button`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  text-align: left;
  color: ${props => props.danger ? 'var(--danger-color)' : 'var(--text-primary)'};
  ${transition()}
  
  &:hover {
    background-color: var(--hover-color);
  }
`;

const UserInfo = styled.div`
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
`;

const UserName = styled.div`
  font-weight: 600;
  margin-bottom: 0.25rem;
`;

const UserEmail = styled.div`
  font-size: 0.875rem;
  color: var(--text-secondary);
`;

const Header = ({ toggleSidebar, isCollapsed }) => {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const handleLogout = async () => {
    await logout();
  };
  
  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };
  
  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user || !user.name) return '?';
    return user.name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };
  
  return (
    <HeaderContainer>
      <LogoContainer>
        <MenuButton onClick={toggleSidebar}>
          {isCollapsed ? '≡' : '☰'}
        </MenuButton>
        <Logo to="/">
          <LogoIcon>CRE</LogoIcon>
          <span>Email Assistant</span>
        </Logo>
      </LogoContainer>
      
      <NavContainer>
        <NavLink to="/inbox" className={location.pathname.includes('/inbox') ? 'active' : ''}>
          Inbox
        </NavLink>
        <NavLink to="/capsules" className={location.pathname.includes('/capsules') ? 'active' : ''}>
          Capsules
        </NavLink>
      </NavContainer>
      
      <UserContainer>
        <UserAvatar onClick={toggleUserMenu}>
          {getUserInitials()}
        </UserAvatar>
        
        {showUserMenu && (
          <UserMenu>
            <UserInfo>
              <UserName>{user?.name || 'User'}</UserName>
              <UserEmail>{user?.email || 'user@example.com'}</UserEmail>
            </UserInfo>
            <UserMenuItem>
              Profile Settings
            </UserMenuItem>
            <UserMenuItem>
              Preferences
            </UserMenuItem>
            <UserMenuItem danger onClick={handleLogout}>
              Logout
            </UserMenuItem>
          </UserMenu>
        )}
      </UserContainer>
    </HeaderContainer>
  );
};

export default Header; 