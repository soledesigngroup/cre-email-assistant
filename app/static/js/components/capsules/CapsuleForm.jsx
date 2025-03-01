import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { capsuleAPI } from '../../services/api';

const FormContainer = styled.div`
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  
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
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  min-height: 150px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const CancelButton = styled(Button)`
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  
  &:hover:not(:disabled) {
    background-color: rgba(0, 0, 0, 0.05);
  }
`;

const SubmitButton = styled(Button)`
  background-color: var(--primary-color);
  border: none;
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--primary-dark);
  }
`;

const ErrorMessage = styled.div`
  color: var(--error-color);
  margin-top: 0.5rem;
  font-size: 0.875rem;
`;

const CapsuleForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    type: 'Property',
    status: 'Active',
    priority: 3,
    summary: '',
    user_notes: ''
  });
  
  useEffect(() => {
    if (id) {
      fetchCapsule();
    }
  }, [id]);
  
  const fetchCapsule = async () => {
    setLoading(true);
    try {
      const response = await capsuleAPI.getCapsuleById(id);
      const capsule = response.data.capsule;
      setFormData({
        title: capsule.title,
        type: capsule.type,
        status: capsule.status,
        priority: capsule.priority,
        summary: capsule.summary,
        user_notes: capsule.user_notes
      });
    } catch (error) {
      console.error('Failed to fetch capsule:', error);
      setError('Failed to load capsule data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      if (id) {
        await capsuleAPI.updateCapsule(id, formData);
      } else {
        await capsuleAPI.createCapsule(formData);
      }
      navigate('/capsules');
    } catch (error) {
      console.error('Failed to save capsule:', error);
      setError('Failed to save capsule. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = () => {
    navigate('/capsules');
  };
  
  return (
    <FormContainer>
      <FormTitle>{id ? 'Edit Capsule' : 'Create New Capsule'}</FormTitle>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="title">Title</Label>
          <Input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Enter capsule title"
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="type">Type</Label>
          <Select
            id="type"
            name="type"
            value={formData.type}
            onChange={handleChange}
            required
          >
            <option value="Property">Property</option>
            <option value="Deal">Deal</option>
            <option value="Client">Client</option>
            <option value="Project">Project</option>
            <option value="Other">Other</option>
          </Select>
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="status">Status</Label>
          <Select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            required
          >
            <option value="Active">Active</option>
            <option value="Pending">Pending</option>
            <option value="Closed">Closed</option>
          </Select>
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="priority">Priority (1-5)</Label>
          <Select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            required
          >
            <option value="1">1 - Highest</option>
            <option value="2">2 - High</option>
            <option value="3">3 - Medium</option>
            <option value="4">4 - Low</option>
            <option value="5">5 - Lowest</option>
          </Select>
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="summary">Summary</Label>
          <Textarea
            id="summary"
            name="summary"
            value={formData.summary}
            onChange={handleChange}
            placeholder="Enter a summary for this capsule"
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="user_notes">Notes</Label>
          <Textarea
            id="user_notes"
            name="user_notes"
            value={formData.user_notes}
            onChange={handleChange}
            placeholder="Add any additional notes here"
          />
        </FormGroup>
        
        <FormActions>
          <CancelButton type="button" onClick={handleCancel}>
            Cancel
          </CancelButton>
          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'Saving...' : id ? 'Update Capsule' : 'Create Capsule'}
          </SubmitButton>
        </FormActions>
      </form>
    </FormContainer>
  );
};

export default CapsuleForm; 