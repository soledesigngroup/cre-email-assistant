import React, { createContext, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children, value }) => {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 