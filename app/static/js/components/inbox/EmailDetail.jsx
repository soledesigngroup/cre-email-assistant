import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { capsuleAPI } from '../../services/api';

const EmailDetailWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  animation: fadeIn 0.3s ease-in-out;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const EmailHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
`;

const Subject = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
`;

const EmailMetadata = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const Sender = styled.div`
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SenderAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
`;

const Recipients = styled.div`
  color: var(--text-secondary);
  font-size: 0.875rem;
`;

const Date = styled.div`
  color: var(--text-secondary);
  font-size: 0.875rem;
`;

const EmailBody = styled.div`
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  line-height: 1.6;
`;

const EmailActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  background-color: ${props => props.primary ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.primary ? 'white' : 'var(--text-secondary)'};
  border: ${props => props.primary ? 'none' : '1px solid var(--border-color)'};
  border-radius: var(--border-radius);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-dark)' : 'rgba(0, 0, 0, 0.05)'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &.pinned {
    background-color: var(--warning-color);
    color: white;
    border: none;
  }
  
  &.archived {
    background-color: var(--secondary-color);
    color: white;
    border: none;
  }
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
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
`;

const EntitiesSection = styled.div`
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  animation: slideUp 0.3s ease-in-out;
  
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const SectionTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const EntitySection = styled.div`
  margin-bottom: 1rem;
`;

const EntityTitle = styled.h4`
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
`;

const EntityContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const CreateCapsuleForm = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background-color: var(--background-color);
  animation: slideDown 0.3s ease-in-out;
  
  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const FormTitle = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
`;

const EmailDetail = ({ email }) => {
  const [showEntities, setShowEntities] = useState(false);
  const [isPinned, setIsPinned] = useState(email.pinned || false);
  const [isArchived, setIsArchived] = useState(email.archived || false);
  const [showCreateCapsule, setShowCreateCapsule] = useState(false);
  const [capsuleForm, setCapsuleForm] = useState({
    title: email.subject || '',
    type: 'Property',
    includeEmail: true
  });
  const [creatingCapsule, setCreatingCapsule] = useState(false);
  
  // Get initials for avatar
  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString([], {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const handleTogglePin = () => {
    setIsPinned(!isPinned);
    // In a real app, you would call an API to update the email
  };
  
  const handleToggleArchive = () => {
    setIsArchived(!isArchived);
    // In a real app, you would call an API to update the email
  };
  
  const handleCreateCapsule = () => {
    setShowCreateCapsule(!showCreateCapsule);
  };
  
  const handleCapsuleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCapsuleForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmitCapsule = async (e) => {
    e.preventDefault();
    setCreatingCapsule(true);
    
    try {
      // In a real app, you would call an API to create the capsule
      await capsuleAPI.createCapsule({
        title: capsuleForm.title,
        type: capsuleForm.type,
        emails: capsuleForm.includeEmail ? [email.id] : [],
        entities: email.entities || {}
      });
      
      setShowCreateCapsule(false);
      // Show success message or redirect
    } catch (error) {
      console.error('Failed to create capsule:', error);
    } finally {
      setCreatingCapsule(false);
    }
  };
  
  return (
    <EmailDetailWrapper>
      <EmailHeader>
        <Subject>{email.subject}</Subject>
        <EmailMetadata>
          <Sender>
            <SenderAvatar>
              {getInitials(email.sender_name || email.sender)}
            </SenderAvatar>
            {email.sender_name || email.sender}
          </Sender>
          <Date>{formatDate(email.date)}</Date>
        </EmailMetadata>
        <Recipients>
          To: {email.recipients ? email.recipients.join(', ') : 'No recipients'}
        </Recipients>
        
        <EmailActions>
          <ActionButton>Reply</ActionButton>
          <ActionButton>Forward</ActionButton>
          <ActionButton 
            onClick={() => setShowEntities(!showEntities)}
          >
            {showEntities ? 'Hide Entities' : 'Show Entities'}
          </ActionButton>
          <ActionButton 
            className={isPinned ? 'pinned' : ''}
            onClick={handleTogglePin}
          >
            {isPinned ? 'Unpin' : 'Pin'}
          </ActionButton>
          <ActionButton 
            className={isArchived ? 'archived' : ''}
            onClick={handleToggleArchive}
          >
            {isArchived ? 'Unarchive' : 'Archive'}
          </ActionButton>
          <ActionButton primary onClick={handleCreateCapsule}>
            Create Capsule
          </ActionButton>
        </EmailActions>
        
        {showCreateCapsule && (
          <CreateCapsuleForm>
            <FormTitle>Create New Capsule</FormTitle>
            <form onSubmit={handleSubmitCapsule}>
              <FormGroup>
                <Label htmlFor="title">Capsule Title</Label>
                <Input
                  type="text"
                  id="title"
                  name="title"
                  value={capsuleForm.title}
                  onChange={handleCapsuleFormChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="type">Capsule Type</Label>
                <Select
                  id="type"
                  name="type"
                  value={capsuleForm.type}
                  onChange={handleCapsuleFormChange}
                >
                  <option value="Property">Property</option>
                  <option value="Deal">Deal</option>
                  <option value="Client">Client</option>
                  <option value="Project">Project</option>
                  <option value="Other">Other</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <label>
                  <input
                    type="checkbox"
                    name="includeEmail"
                    checked={capsuleForm.includeEmail}
                    onChange={handleCapsuleFormChange}
                  />
                  {' '}Include this email in the capsule
                </label>
              </FormGroup>
              
              <FormActions>
                <ActionButton type="button" onClick={() => setShowCreateCapsule(false)}>
                  Cancel
                </ActionButton>
                <ActionButton primary type="submit" disabled={creatingCapsule}>
                  {creatingCapsule ? 'Creating...' : 'Create Capsule'}
                </ActionButton>
              </FormActions>
            </form>
          </CreateCapsuleForm>
        )}
      </EmailHeader>
      
      <EmailBody>
        <div dangerouslySetInnerHTML={{ __html: email.body_html || email.body_text || 'No content available' }} />
        
        {showEntities && email.entities && (
          <EntitiesSection>
            <SectionTitle>Detected Entities</SectionTitle>
            
            {email.entities.properties && email.entities.properties.length > 0 && (
              <EntitySection>
                <EntityTitle>Properties</EntityTitle>
                <EntityContainer>
                  {email.entities.properties.map((property, index) => (
                    <EntityTag key={index} type="property">
                      {property.name || property.address}
                    </EntityTag>
                  ))}
                </EntityContainer>
              </EntitySection>
            )}
            
            {email.entities.people && email.entities.people.length > 0 && (
              <EntitySection>
                <EntityTitle>People</EntityTitle>
                <EntityContainer>
                  {email.entities.people.map((person, index) => (
                    <EntityTag key={index} type="person">
                      {person.name}
                    </EntityTag>
                  ))}
                </EntityContainer>
              </EntitySection>
            )}
            
            {email.entities.companies && email.entities.companies.length > 0 && (
              <EntitySection>
                <EntityTitle>Companies</EntityTitle>
                <EntityContainer>
                  {email.entities.companies.map((company, index) => (
                    <EntityTag key={index} type="company">
                      {company.name}
                    </EntityTag>
                  ))}
                </EntityContainer>
              </EntitySection>
            )}
            
            {email.entities.dates && email.entities.dates.length > 0 && (
              <EntitySection>
                <EntityTitle>Dates</EntityTitle>
                <EntityContainer>
                  {email.entities.dates.map((date, index) => (
                    <EntityTag key={index} type="date">
                      {date.text}
                    </EntityTag>
                  ))}
                </EntityContainer>
              </EntitySection>
            )}
          </EntitiesSection>
        )}
      </EmailBody>
    </EmailDetailWrapper>
  );
};

export default EmailDetail; 