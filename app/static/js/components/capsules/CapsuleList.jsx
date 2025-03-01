import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { capsuleAPI } from '../../services/api';

const CapsuleListContainer = styled.div`
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const CapsuleListHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CapsuleListTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
`;

const CapsuleListActions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ActionButton = styled.button`
  background-color: ${props => props.primary ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.primary ? 'white' : 'var(--text-secondary)'};
  border: ${props => props.primary ? 'none' : '1px solid var(--border-color)'};
  border-radius: var(--border-radius);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-dark)' : 'rgba(0, 0, 0, 0.05)'};
  }
`;

const CapsuleListContent = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const CapsuleItem = styled(Link)`
  display: block;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  text-decoration: none;
  color: var(--text-primary);
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
  
  &.active {
    background-color: rgba(37, 99, 235, 0.05);
    border-left: 3px solid var(--primary-color);
  }
`;

const CapsuleTitle = styled.div`
  font-weight: 600;
  margin-bottom: 0.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CapsuleType = styled.span`
  background-color: var(--primary-light);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
`;

const CapsuleStatus = styled.span`
  background-color: ${props => {
    switch (props.status.toLowerCase()) {
      case 'active': return '#dcfce7';
      case 'pending': return '#fef3c7';
      case 'closed': return '#f3f4f6';
      default: return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.status.toLowerCase()) {
      case 'active': return '#166534';
      case 'pending': return '#92400e';
      case 'closed': return '#4b5563';
      default: return '#4b5563';
    }
  }};
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
`;

const CapsuleMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--text-secondary);
`;

const CapsuleDate = styled.div`
  font-size: 0.75rem;
  color: var(--text-secondary);
`;

const CapsulePreview = styled.div`
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
`;

const EmptyStateIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--border-color);
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
`;

const CapsuleList = ({ activeCapsuleId }) => {
  const [capsules, setCapsules] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchCapsules();
  }, []);
  
  const fetchCapsules = async () => {
    setLoading(true);
    try {
      const response = await capsuleAPI.getCapsules();
      setCapsules(response.data.capsules || []);
    } catch (error) {
      console.error('Failed to fetch capsules:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateCapsule = () => {
    navigate('/capsules/new');
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    // If today, show time
    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // If this year, show month and day
    if (date.getFullYear() === now.getFullYear()) {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    
    // Otherwise show full date
    return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
  };
  
  return (
    <CapsuleListContainer>
      <CapsuleListHeader>
        <CapsuleListTitle>Capsules</CapsuleListTitle>
        <CapsuleListActions>
          <ActionButton onClick={fetchCapsules}>Refresh</ActionButton>
          <ActionButton primary onClick={handleCreateCapsule}>New Capsule</ActionButton>
        </CapsuleListActions>
      </CapsuleListHeader>
      
      <CapsuleListContent>
        {loading ? (
          <LoadingSpinner>Loading capsules...</LoadingSpinner>
        ) : capsules.length === 0 ? (
          <EmptyState>
            <EmptyStateIcon>📦</EmptyStateIcon>
            <p>No capsules found. Create a new capsule to get started.</p>
          </EmptyState>
        ) : (
          capsules.map(capsule => (
            <CapsuleItem 
              key={capsule._id || capsule.id} 
              to={`/capsule/${capsule._id || capsule.id}`}
              className={activeCapsuleId === (capsule._id || capsule.id) ? 'active' : ''}
            >
              <CapsuleTitle>
                {capsule.title}
                <CapsuleType>{capsule.type}</CapsuleType>
              </CapsuleTitle>
              <CapsuleMeta>
                <CapsuleStatus status={capsule.status}>{capsule.status}</CapsuleStatus>
                <CapsuleDate>Updated: {formatDate(capsule.updated_at)}</CapsuleDate>
              </CapsuleMeta>
              <CapsulePreview>
                {capsule.summary || 'No summary available'}
              </CapsulePreview>
            </CapsuleItem>
          ))
        )}
      </CapsuleListContent>
    </CapsuleListContainer>
  );
};

export default CapsuleList; 