import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { capsuleAPI } from '../../services/api';

const CapsuleContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const CapsuleHeader = styled.div`
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const CapsuleInfo = styled.div`
  flex: 1;
`;

const CapsuleTitle = styled.h1`
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`;

const CapsuleMeta = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const CapsuleMetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
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

const CapsuleActions = styled.div`
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

const CapsuleContent = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const CapsuleMain = styled.div`
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const CapsulesSection = styled.div`
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CapsuleSidebar = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const EntityList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const EntityTag = styled.span`
  display: inline-block;
  background-color: ${props => {
    switch (props.type) {
      case 'property': return '#e0f2fe';
      case 'person': return '#dcfce7';
      case 'company': return '#fef3c7';
      case 'date': return '#f3e8ff';
      default: return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'property': return '#0369a1';
      case 'person': return '#166534';
      case 'company': return '#92400e';
      case 'date': return '#7e22ce';
      default: return '#4b5563';
    }
  }};
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
`;

const EmailList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const EmailItem = styled.div`
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
`;

const EmailHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const Sender = styled.div`
  font-weight: 600;
`;

const Date = styled.div`
  font-size: 0.8rem;
  color: var(--text-secondary);
`;

const Subject = styled.div`
  font-weight: 500;
  margin-bottom: 0.5rem;
`;

const Preview = styled.div`
  font-size: 0.875rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
`;

const CapsuleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [capsule, setCapsule] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchCapsule = async () => {
      setLoading(true);
      try {
        const response = await capsuleAPI.getCapsuleById(id);
        setCapsule(response.data.capsule);
      } catch (error) {
        console.error('Failed to fetch capsule:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCapsule();
  }, [id]);
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString([], {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  if (loading) {
    return <LoadingSpinner>Loading capsule...</LoadingSpinner>;
  }
  
  if (!capsule) {
    return (
      <div>
        <h2>Capsule not found</h2>
        <p>The capsule you're looking for doesn't exist or has been deleted.</p>
        <ActionButton onClick={() => navigate('/inbox')}>Back to Inbox</ActionButton>
      </div>
    );
  }
  
  return (
    <CapsuleContainer>
      <CapsuleHeader>
        <CapsuleInfo>
          <CapsuleTitle>{capsule.title}</CapsuleTitle>
          <CapsuleMeta>
            <CapsuleMetaItem>
              <CapsuleType>{capsule.type}</CapsuleType>
            </CapsuleMetaItem>
            <CapsuleMetaItem>
              <CapsuleStatus status={capsule.status}>{capsule.status}</CapsuleStatus>
            </CapsuleMetaItem>
            <CapsuleMetaItem>
              Created: {formatDate(capsule.created_at)}
            </CapsuleMetaItem>
            <CapsuleMetaItem>
              Updated: {formatDate(capsule.updated_at)}
            </CapsuleMetaItem>
          </CapsuleMeta>
        </CapsuleInfo>
        <CapsuleActions>
          <ActionButton>Edit</ActionButton>
          <ActionButton>Archive</ActionButton>
          <ActionButton primary>Add Email</ActionButton>
        </CapsuleActions>
      </CapsuleHeader>
      
      <CapsuleContent>
        <CapsuleMain>
          <CapsulesSection>
            <SectionTitle>Summary</SectionTitle>
            <p>{capsule.summary}</p>
          </CapsulesSection>
          
          <CapsulesSection>
            <SectionTitle>Emails ({capsule.emails.length})</SectionTitle>
            <EmailList>
              {capsule.emails.length === 0 ? (
                <p>No emails in this capsule yet.</p>
              ) : (
                capsule.emails.map((email, index) => (
                  <EmailItem key={index}>
                    <EmailHeader>
                      <Sender>{email.sender_name || email.sender}</Sender>
                      <Date>{formatDate(email.date)}</Date>
                    </EmailHeader>
                    <Subject>{email.subject}</Subject>
                    <Preview>{email.snippet}</Preview>
                  </EmailItem>
                ))
              )}
            </EmailList>
          </CapsulesSection>
        </CapsuleMain>
        
        <CapsuleSidebar>
          <CapsulesSection>
            <SectionTitle>Properties</SectionTitle>
            <EntityList>
              {capsule.entities.properties.length === 0 ? (
                <p>No properties detected.</p>
              ) : (
                capsule.entities.properties.map((property, index) => (
                  <EntityTag key={index} type="property">
                    {property.name || property.address}
                  </EntityTag>
                ))
              )}
            </EntityList>
          </CapsulesSection>
          
          <CapsulesSection>
            <SectionTitle>People</SectionTitle>
            <EntityList>
              {capsule.entities.people.length === 0 ? (
                <p>No people detected.</p>
              ) : (
                capsule.entities.people.map((person, index) => (
                  <EntityTag key={index} type="person">
                    {person.name}
                  </EntityTag>
                ))
              )}
            </EntityList>
          </CapsulesSection>
          
          <CapsulesSection>
            <SectionTitle>Companies</SectionTitle>
            <EntityList>
              {capsule.entities.companies.length === 0 ? (
                <p>No companies detected.</p>
              ) : (
                capsule.entities.companies.map((company, index) => (
                  <EntityTag key={index} type="company">
                    {company.name}
                  </EntityTag>
                ))
              )}
            </EntityList>
          </CapsulesSection>
          
          <CapsulesSection>
            <SectionTitle>Notes</SectionTitle>
            <p>{capsule.user_notes || 'No notes added yet.'}</p>
          </CapsulesSection>
        </CapsuleSidebar>
      </CapsuleContent>
    </CapsuleContainer>
  );
};

export default CapsuleDetail; 