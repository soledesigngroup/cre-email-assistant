import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import styled from 'styled-components';
import Header from './Header';
import Sidebar from './Sidebar';
import { animateFadeIn } from '../common/animations';

const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  ${animateFadeIn()}
`;

const MainContainer = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const SidebarContainer = styled.div`
  width: ${props => props.isCollapsed ? '64px' : '250px'};
  transition: width 0.3s ease;
  height: calc(100vh - 64px);
  overflow: hidden;
`;

const ContentContainer = styled.main`
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 64px);
  position: relative;
`;

const Layout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };
  
  return (
    <LayoutContainer>
      <Header toggleSidebar={toggleSidebar} isCollapsed={sidebarCollapsed} />
      <MainContainer>
        <SidebarContainer isCollapsed={sidebarCollapsed}>
          <Sidebar isCollapsed={sidebarCollapsed} />
        </SidebarContainer>
        <ContentContainer>
          <Outlet />
        </ContentContainer>
      </MainContainer>
    </LayoutContainer>
  );
};

export default Layout; 