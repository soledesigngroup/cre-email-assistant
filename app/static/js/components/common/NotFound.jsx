import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const NotFoundContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  text-align: center;
`;

const NotFoundTitle = styled.h1`
  font-size: 6rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
`;

const NotFoundText = styled.p`
  font-size: 1.5rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
`;

const BackButton = styled(Link)`
  background-color: var(--primary-color);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    background-color: var(--primary-dark);
  }
`;

const NotFound = () => {
  return (
    <NotFoundContainer>
      <NotFoundTitle>404</NotFoundTitle>
      <NotFoundText>Oops! The page you're looking for doesn't exist.</NotFoundText>
      <BackButton to="/">Back to Home</BackButton>
    </NotFoundContainer>
  );
};

export default NotFound; 