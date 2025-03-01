import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const EmailItemContainer = styled(Link)`
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  position: relative;
  
  ${props => props.isActive && `
    background-color: var(--primary-light);
    border-left: 4px solid var(--primary-color);
  `}
  
  ${props => props.isRead ? `
    background-color: var(--background-color);
  ` : `
    background-color: white;
    font-weight: 500;
  `}
  
  &:hover {
    background-color: var(--hover-color);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  animation: fadeIn 0.3s ease-in-out;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const EmailHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const Sender = styled.div`
  font-weight: ${props => props.isRead ? '500' : '600'};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SenderAvatar = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
`;

const Date = styled.div`
  font-size: 0.75rem;
  color: var(--text-secondary);
`;

const Subject = styled.div`
  font-weight: ${props => props.isRead ? '400' : '600'};
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const Preview = styled.div`
  font-size: 0.875rem;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
`;

const StatusIndicators = styled.div`
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.25rem;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => {
    if (props.type === 'pinned') return 'var(--warning-color)';
    if (props.type === 'archived') return 'var(--secondary-color)';
    if (props.type === 'capsule') return 'var(--success-color)';
    return 'var(--primary-color)';
  }};
`;

const Tags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
`;

const Tag = styled.span`
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
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
`;

const EmailItem = ({ email, isActive }) => {
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
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays < 7) {
      const options = { weekday: 'short' };
      return date.toLocaleDateString([], options);
    } else {
      const options = { month: 'short', day: 'numeric' };
      return date.toLocaleDateString([], options);
    }
  };
  
  // Get a preview of the email body
  const getPreview = (body) => {
    if (!body) return 'No content';
    
    // If it's HTML, strip the tags
    if (body.startsWith('<')) {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = body;
      return tempDiv.textContent || tempDiv.innerText || '';
    }
    
    return body;
  };
  
  // Get top entities to display as tags
  const getTopEntities = () => {
    if (!email.entities) return [];
    
    const entities = [];
    
    if (email.entities.properties && email.entities.properties.length > 0) {
      entities.push({
        type: 'property',
        text: email.entities.properties[0].name || email.entities.properties[0].address
      });
    }
    
    if (email.entities.companies && email.entities.companies.length > 0) {
      entities.push({
        type: 'company',
        text: email.entities.companies[0].name
      });
    }
    
    if (email.entities.people && email.entities.people.length > 0) {
      entities.push({
        type: 'person',
        text: email.entities.people[0].name
      });
    }
    
    return entities.slice(0, 3); // Limit to 3 tags
  };
  
  return (
    <EmailItemContainer 
      to={`/inbox/${email.id}`} 
      isRead={email.read} 
      isActive={isActive}
    >
      <StatusIndicators>
        {email.pinned && <StatusIndicator type="pinned" title="Pinned" />}
        {email.archived && <StatusIndicator type="archived" title="Archived" />}
        {email.in_capsule && <StatusIndicator type="capsule" title="In Capsule" />}
      </StatusIndicators>
      
      <EmailHeader>
        <Sender isRead={email.read}>
          <SenderAvatar>
            {getInitials(email.sender_name || email.sender)}
          </SenderAvatar>
          {email.sender_name || email.sender}
        </Sender>
        <Date>{formatDate(email.date)}</Date>
      </EmailHeader>
      
      <Subject isRead={email.read}>{email.subject}</Subject>
      <Preview>{getPreview(email.body_text || email.body_html)}</Preview>
      
      {getTopEntities().length > 0 && (
        <Tags>
          {getTopEntities().map((entity, index) => (
            <Tag key={index} type={entity.type}>
              {entity.text}
            </Tag>
          ))}
        </Tags>
      )}
    </EmailItemContainer>
  );
};

export default EmailItem; 