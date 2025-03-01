import React, { useState } from 'react';
import styled from 'styled-components';

const EmailDetailWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
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
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-dark)' : 'rgba(0, 0, 0, 0.05)'};
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
`;

const EntitiesSection = styled.div`
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
`;

const SectionTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
`;

const EmailDetail = ({ email }) => {
  const [showEntities, setShowEntities] = useState(false);
  
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
  
  return (
    <EmailDetailWrapper>
      <EmailHeader>
        <Subject>{email.subject}</Subject>
        <EmailMetadata>
          <Sender>{email.sender_name || email.sender}</Sender>
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
          <ActionButton primary>Create Capsule</ActionButton>
        </EmailActions>
      </EmailHeader>
      
      <EmailBody>
        <div dangerouslySetInnerHTML={{ __html: email.body_html || email.body_text || 'No content available' }} />
        
        {showEntities && email.entities && (
          <EntitiesSection>
            <SectionTitle>Detected Entities</SectionTitle>
            
            {email.entities.properties && email.entities.properties.length > 0 && (
              <div>
                <h4>Properties</h4>
                <div>
                  {email.entities.properties.map((property, index) => (
                    <EntityTag key={index} type="property">
                      {property.name || property.address}
                    </EntityTag>
                  ))}
                </div>
              </div>
            )}
            
            {email.entities.people && email.entities.people.length > 0 && (
              <div>
                <h4>People</h4>
                <div>
                  {email.entities.people.map((person, index) => (
                    <EntityTag key={index} type="person">
                      {person.name}
                    </EntityTag>
                  ))}
                </div>
              </div>
            )}
            
            {email.entities.companies && email.entities.companies.length > 0 && (
              <div>
                <h4>Companies</h4>
                <div>
                  {email.entities.companies.map((company, index) => (
                    <EntityTag key={index} type="company">
                      {company.name}
                    </EntityTag>
                  ))}
                </div>
              </div>
            )}
            
            {email.entities.dates && email.entities.dates.length > 0 && (
              <div>
                <h4>Dates</h4>
                <div>
                  {email.entities.dates.map((date, index) => (
                    <EntityTag key={index} type="date">
                      {date.text}
                    </EntityTag>
                  ))}
                </div>
              </div>
            )}
          </EntitiesSection>
        )}
      </EmailBody>
    </EmailDetailWrapper>
  );
};

export default EmailDetail; 