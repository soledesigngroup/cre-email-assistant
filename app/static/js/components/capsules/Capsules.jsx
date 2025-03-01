import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import CapsuleList from './CapsuleList';
import CapsuleDetail from './CapsuleDetail';
import CapsuleForm from './CapsuleForm';

const CapsulesContainer = styled.div`
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 120px);
`;

const CapsulesListContainer = styled.div`
  flex: 1;
  max-width: 400px;
`;

const CapsuleContentContainer = styled.div`
  flex: 2;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
`;

const EmptyStateIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1rem;
  color: var(--border-color);
`;

const EmptyStateTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
`;

const Capsules = () => {
  const { id, action } = useParams();
  
  return (
    <CapsulesContainer>
      <CapsulesListContainer>
        <CapsuleList activeCapsuleId={id} />
      </CapsulesListContainer>
      
      <CapsuleContentContainer>
        {action === 'new' ? (
          <CapsuleForm />
        ) : id ? (
          <CapsuleDetail />
        ) : (
          <EmptyState>
            <EmptyStateIcon>📦</EmptyStateIcon>
            <EmptyStateTitle>No Capsule Selected</EmptyStateTitle>
            <p>Select a capsule from the list or create a new one to get started.</p>
          </EmptyState>
        )}
      </CapsuleContentContainer>
    </CapsulesContainer>
  );
};

export default Capsules; 