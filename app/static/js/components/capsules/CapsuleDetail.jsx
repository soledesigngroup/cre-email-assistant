import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { capsuleAPI, emailAPI } from '../../services/api';
import EmailItem from '../inbox/EmailItem';

const CapsuleContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeIn 0.3s ease-in-out;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
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
  flex-wrap: wrap;
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
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-dark)' : 'rgba(0, 0, 0, 0.05)'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const CapsuleContent = styled.div`
  display: flex;
  gap: 1.5rem;
  
  @media (max-width: 1024px) {
    flex-direction: column;
  }
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
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
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
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
`;

const EmailList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const EmailItemContainer = styled.div`
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1rem;
`;

const Tab = styled.button`
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid ${props => props.active ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.active ? 'var(--primary-color)' : 'var(--text-secondary)'};
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: var(--primary-color);
  }
`;

const NotesTextarea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  min-height: 150px;
  resize: vertical;
  margin-bottom: 1rem;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const CapsuleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [capsule, setCapsule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('emails');
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  
  useEffect(() => {
    if (id) {
      fetchCapsule();
    }
  }, [id]);
  
  const fetchCapsule = async () => {
    setLoading(true);
    try {
      const response = await capsuleAPI.getCapsuleById(id);
      const capsuleData = response.data.capsule;
      setCapsule(capsuleData);
      setNotes(capsuleData.user_notes || '');
    } catch (error) {
      console.error('Failed to fetch capsule:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleEditCapsule = () => {
    navigate(`/capsule/${id}/edit`);
  };
  
  const handleArchiveCapsule = async () => {
    try {
      await capsuleAPI.updateCapsule(id, { 
        ...capsule, 
        status: 'Closed' 
      });
      fetchCapsule();
    } catch (error) {
      console.error('Failed to archive capsule:', error);
    }
  };
  
  const handleSaveNotes = async () => {
    setSavingNotes(true);
    try {
      await capsuleAPI.updateCapsule(id, { 
        user_notes: notes 
      });
    } catch (error) {
      console.error('Failed to save notes:', error);
    } finally {
      setSavingNotes(false);
    }
  };
  
  const handleAddEmail = () => {
    navigate(`/capsule/${id}/add-email`);
  };
  
  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
  };
  
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
        <ActionButton onClick={() => navigate('/capsules')}>Back to Capsules</ActionButton>
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
          <ActionButton onClick={handleEditCapsule}>Edit</ActionButton>
          <ActionButton onClick={handleArchiveCapsule}>
            {capsule.status === 'Closed' ? 'Reopen' : 'Archive'}
          </ActionButton>
          <ActionButton primary onClick={handleAddEmail}>Add Email</ActionButton>
        </CapsuleActions>
      </CapsuleHeader>
      
      <CapsuleContent>
        <CapsuleMain>
          <CapsulesSection>
            <SectionTitle>Summary</SectionTitle>
            <p>{capsule.summary || 'No summary available.'}</p>
          </CapsulesSection>
          
          <CapsulesSection>
            <TabContainer>
              <Tab 
                active={activeTab === 'emails'} 
                onClick={() => setActiveTab('emails')}
              >
                Emails ({capsule.emails.length})
              </Tab>
              <Tab 
                active={activeTab === 'notes'} 
                onClick={() => setActiveTab('notes')}
              >
                Notes
              </Tab>
            </TabContainer>
            
            {activeTab === 'emails' ? (
              <EmailList>
                {capsule.emails.length === 0 ? (
                  <p>No emails in this capsule yet.</p>
                ) : (
                  capsule.emails.map((email, index) => (
                    <EmailItemContainer key={index}>
                      <EmailItem 
                        email={email} 
                        isSelected={selectedEmail && selectedEmail.id === email.id}
                        onClick={() => handleSelectEmail(email)}
                      />
                    </EmailItemContainer>
                  ))
                )}
              </EmailList>
            ) : (
              <div>
                <NotesTextarea 
                  value={notes} 
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add your notes here..."
                />
                <ActionButton 
                  primary 
                  onClick={handleSaveNotes}
                  disabled={savingNotes}
                >
                  {savingNotes ? 'Saving...' : 'Save Notes'}
                </ActionButton>
              </div>
            )}
          </CapsulesSection>
        </CapsuleMain>
        
        <CapsuleSidebar>
          <CapsulesSection>
            <SectionTitle>Properties</SectionTitle>
            <EntityList>
              {!capsule.entities.properties || capsule.entities.properties.length === 0 ? (
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
              {!capsule.entities.people || capsule.entities.people.length === 0 ? (
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
              {!capsule.entities.companies || capsule.entities.companies.length === 0 ? (
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
        </CapsuleSidebar>
      </CapsuleContent>
    </CapsuleContainer>
  );
};

export default CapsuleDetail; 