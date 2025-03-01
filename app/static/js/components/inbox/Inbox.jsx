import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { authAPI, emailAPI } from '../../services/api';
import EmailItem from './EmailItem';
import EmailDetail from './EmailDetail';

const InboxContainer = styled.div`
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 120px);
`;

const EmailListContainer = styled.div`
  flex: 1;
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const EmailListHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const EmailListTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
`;

const EmailListActions = styled.div`
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

const EmailList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const EmailDetailContainer = styled.div`
  flex: 1.5;
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
  padding: 2rem;
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

const Inbox = () => {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingEmails, setProcessingEmails] = useState(false);
  
  useEffect(() => {
    fetchEmails();
  }, []);
  
  const fetchEmails = async () => {
    setLoading(true);
    try {
      const response = await authAPI.getEmails();
      setEmails(response.data.emails || []);
      
      // Select the first email if available
      if (response.data.emails && response.data.emails.length > 0) {
        setSelectedEmail(response.data.emails[0]);
      }
    } catch (error) {
      console.error('Failed to fetch emails:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleProcessEmails = async () => {
    setProcessingEmails(true);
    try {
      await emailAPI.processEmails(10);
      // Refresh emails after processing
      fetchEmails();
    } catch (error) {
      console.error('Failed to process emails:', error);
    } finally {
      setProcessingEmails(false);
    }
  };
  
  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
  };
  
  return (
    <InboxContainer>
      <EmailListContainer>
        <EmailListHeader>
          <EmailListTitle>Inbox</EmailListTitle>
          <EmailListActions>
            <ActionButton onClick={fetchEmails}>Refresh</ActionButton>
            <ActionButton 
              primary 
              onClick={handleProcessEmails}
              disabled={processingEmails}
            >
              {processingEmails ? 'Processing...' : 'Process Emails'}
            </ActionButton>
          </EmailListActions>
        </EmailListHeader>
        
        <EmailList>
          {loading ? (
            <LoadingSpinner>Loading emails...</LoadingSpinner>
          ) : emails.length === 0 ? (
            <EmptyState>
              <EmptyStateIcon>📭</EmptyStateIcon>
              <p>No emails found. Process emails to get started.</p>
            </EmptyState>
          ) : (
            emails.map(email => (
              <EmailItem 
                key={email.id} 
                email={email} 
                isSelected={selectedEmail && selectedEmail.id === email.id}
                onClick={() => handleSelectEmail(email)}
              />
            ))
          )}
        </EmailList>
      </EmailListContainer>
      
      <EmailDetailContainer>
        {selectedEmail ? (
          <EmailDetail email={selectedEmail} />
        ) : (
          <EmptyState>
            <EmptyStateIcon>📝</EmptyStateIcon>
            <p>Select an email to view details</p>
          </EmptyState>
        )}
      </EmailDetailContainer>
    </InboxContainer>
  );
};

export default Inbox;