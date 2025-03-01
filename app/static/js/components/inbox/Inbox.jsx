import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import EmailItem from './EmailItem';
import EmailDetail from './EmailDetail';
import { emailAPI } from '../../services/api';

const InboxContainer = styled.div`
  display: flex;
  height: 100%;
  overflow: hidden;
`;

const EmailListContainer = styled.div`
  width: 35%;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const EmailListHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const HeaderTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
`;

const FilterContainer = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const FilterButton = styled.button`
  background-color: ${props => props.active ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};
  border: ${props => props.active ? 'none' : '1px solid var(--border-color)'};
  border-radius: var(--border-radius);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.active ? 'var(--primary-dark)' : 'rgba(0, 0, 0, 0.05)'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const SearchContainer = styled.div`
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
`;

const SearchInput = styled.input`
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

const EmailList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const EmailDetailContainer = styled.div`
  flex: 1;
  height: 100%;
  overflow: hidden;
  animation: fadeIn 0.3s ease-in-out;
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  padding: 2rem;
  text-align: center;
`;

const EmptyStateIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--border-color);
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
`;

const Spinner = styled.div`
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ActionBar = styled.div`
  display: flex;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  gap: 0.5rem;
`;

const ActionButton = styled.button`
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Inbox = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [filter, setFilter] = useState('all'); // all, unread, pinned, archived
  const [searchQuery, setSearchQuery] = useState('');
  
  useEffect(() => {
    fetchEmails();
  }, []);
  
  useEffect(() => {
    if (id && emails.length > 0) {
      const email = emails.find(email => email.id === id);
      setSelectedEmail(email);
      
      // Mark as read if not already
      if (email && !email.read) {
        markAsRead(email.id);
      }
    } else if (emails.length > 0) {
      navigate(`/inbox/${emails[0].id}`);
    }
  }, [id, emails]);
  
  const fetchEmails = async () => {
    setLoading(true);
    try {
      const response = await emailAPI.getEmails();
      setEmails(response.data);
      
      // If no email is selected and we have emails, select the first one
      if (!id && response.data.length > 0) {
        navigate(`/inbox/${response.data[0].id}`);
      }
    } catch (error) {
      console.error('Failed to fetch emails:', error);
      setError('Failed to load emails. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const markAsRead = async (emailId) => {
    try {
      await emailAPI.markAsRead(emailId);
      setEmails(emails.map(email => 
        email.id === emailId ? { ...email, read: true } : email
      ));
    } catch (error) {
      console.error('Failed to mark email as read:', error);
    }
  };
  
  const handleTogglePin = async (emailId) => {
    try {
      const email = emails.find(e => e.id === emailId);
      const newPinnedState = !email.pinned;
      
      await emailAPI.updateEmail(emailId, { pinned: newPinnedState });
      
      setEmails(emails.map(email => 
        email.id === emailId ? { ...email, pinned: newPinnedState } : email
      ));
    } catch (error) {
      console.error('Failed to update email:', error);
    }
  };
  
  const handleToggleArchive = async (emailId) => {
    try {
      const email = emails.find(e => e.id === emailId);
      const newArchivedState = !email.archived;
      
      await emailAPI.updateEmail(emailId, { archived: newArchivedState });
      
      setEmails(emails.map(email => 
        email.id === emailId ? { ...email, archived: newArchivedState } : email
      ));
    } catch (error) {
      console.error('Failed to update email:', error);
    }
  };
  
  const handleMarkAsUnread = async (emailId) => {
    try {
      await emailAPI.updateEmail(emailId, { read: false });
      
      setEmails(emails.map(email => 
        email.id === emailId ? { ...email, read: false } : email
      ));
    } catch (error) {
      console.error('Failed to update email:', error);
    }
  };
  
  const handleRefresh = () => {
    fetchEmails();
  };
  
  const filteredEmails = emails.filter(email => {
    // Apply filter
    if (filter === 'unread' && email.read) return false;
    if (filter === 'pinned' && !email.pinned) return false;
    if (filter === 'archived' && !email.archived) return false;
    if (filter === 'inbox' && email.archived) return false;
    
    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        (email.subject && email.subject.toLowerCase().includes(query)) ||
        (email.sender && email.sender.toLowerCase().includes(query)) ||
        (email.sender_name && email.sender_name.toLowerCase().includes(query)) ||
        (email.body_text && email.body_text.toLowerCase().includes(query))
      );
    }
    
    return true;
  });
  
  return (
    <InboxContainer>
      <EmailListContainer>
        <EmailListHeader>
          <HeaderTitle>Inbox</HeaderTitle>
          <FilterContainer>
            <FilterButton 
              active={filter === 'inbox'} 
              onClick={() => setFilter('inbox')}
            >
              Inbox
            </FilterButton>
            <FilterButton 
              active={filter === 'unread'} 
              onClick={() => setFilter('unread')}
            >
              Unread
            </FilterButton>
            <FilterButton 
              active={filter === 'pinned'} 
              onClick={() => setFilter('pinned')}
            >
              Pinned
            </FilterButton>
            <FilterButton 
              active={filter === 'archived'} 
              onClick={() => setFilter('archived')}
            >
              Archived
            </FilterButton>
            <FilterButton 
              active={filter === 'all'} 
              onClick={() => setFilter('all')}
            >
              All
            </FilterButton>
          </FilterContainer>
        </EmailListHeader>
        
        <SearchContainer>
          <SearchInput 
            type="text" 
            placeholder="Search emails..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchContainer>
        
        <ActionBar>
          <ActionButton onClick={handleRefresh}>
            Refresh
          </ActionButton>
          {selectedEmail && (
            <>
              <ActionButton 
                onClick={() => handleTogglePin(selectedEmail.id)}
              >
                {selectedEmail.pinned ? 'Unpin' : 'Pin'}
              </ActionButton>
              <ActionButton 
                onClick={() => handleToggleArchive(selectedEmail.id)}
              >
                {selectedEmail.archived ? 'Unarchive' : 'Archive'}
              </ActionButton>
              <ActionButton 
                onClick={() => handleMarkAsUnread(selectedEmail.id)}
              >
                Mark as Unread
              </ActionButton>
            </>
          )}
        </ActionBar>
        
        <EmailList>
          {loading ? (
            <LoadingState>
              <Spinner />
              Loading emails...
            </LoadingState>
          ) : error ? (
            <EmptyState>
              <EmptyStateIcon>⚠️</EmptyStateIcon>
              {error}
            </EmptyState>
          ) : filteredEmails.length === 0 ? (
            <EmptyState>
              <EmptyStateIcon>📭</EmptyStateIcon>
              {searchQuery 
                ? 'No emails match your search criteria' 
                : 'No emails found in this category'}
            </EmptyState>
          ) : (
            filteredEmails.map(email => (
              <EmailItem 
                key={email.id} 
                email={email} 
                isActive={selectedEmail && selectedEmail.id === email.id}
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
            <EmptyStateIcon>📧</EmptyStateIcon>
            <p>Select an email to view its contents</p>
          </EmptyState>
        )}
      </EmailDetailContainer>
    </InboxContainer>
  );
};

export default Inbox;