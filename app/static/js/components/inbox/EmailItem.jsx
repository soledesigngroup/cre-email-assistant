import React from 'react';
import styled from 'styled-components';

const EmailItemContainer = styled.div`
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  background-color: ${props => props.isSelected ? 'rgba(37, 99, 235, 0.05)' : 'transparent'};
  border-left: ${props => props.isSelected ? '3px solid var(--primary-color)' : '3px solid transparent'};
  
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
  color: var(--text-primary);
`;

const Date = styled.div`
  font-size: 0.8rem;
  color: var(--text-secondary);
`;

const Subject = styled.div`
  font-weight: ${props => props.unread ? '600' : '400'};
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const Preview = styled.div`
  font-size: 0.875rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const EmailItem = ({ email, isSelected, onClick }) => {
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
    <EmailItemContainer isSelected={isSelected} onClick={onClick}>
      <EmailHeader>
        <Sender>{email.sender_name || email.sender}</Sender>
        <Date>{formatDate(email.date)}</Date>
      </EmailHeader>
      <Subject unread={!email.read}>{email.subject}</Subject>
      <Preview>{email.snippet || 'No preview available'}</Preview>
    </EmailItemContainer>
  );
};

export default EmailItem; 