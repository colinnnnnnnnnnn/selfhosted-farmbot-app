import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import {
  getSequences,
  createSequence,
  updateSequence,
  deleteSequence,
  executeSequence,
  AVAILABLE_COMMANDS,
} from '../services/sequenceService';

const modalBackdrop = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: 'rgba(0,0,0,0.7)',
  zIndex: 2000,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const modalContent = {
  background: '#222',
  borderRadius: '10px',
  padding: '24px',
  width: '800px',
  maxWidth: '95vw',
  maxHeight: '85vh',
  overflow: 'auto',
  color: 'white',
  boxShadow: '0 4px 32px rgba(0,0,0,0.7)',
};

const buttonStyle = {
  background: '#13a73f',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  padding: '8px 16px',
  cursor: 'pointer',
  fontSize: '14px',
  marginRight: '8px',
};

const dangerButtonStyle = {
  ...buttonStyle,
  background: '#dc3545',
};

const secondaryButtonStyle = {
  ...buttonStyle,
  background: '#444',
};

const inputStyle = {
  background: '#333',
  border: '1px solid #555',
  borderRadius: '4px',
  padding: '8px 12px',
  color: 'white',
  fontSize: '14px',
  width: '100%',
  boxSizing: 'border-box',
};

const selectStyle = {
  ...inputStyle,
  cursor: 'pointer',
};

const stepCardStyle = {
  background: '#333',
  borderRadius: '8px',
  padding: '12px',
  marginBottom: '8px',
  border: '1px solid #444',
};

function SequenceEditor({ open, onClose, setMoveStatus }) {
  const [sequences, setSequences] = useState([]);
  const [editingSequence, setEditingSequence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [view, setView] = useState('list'); // 'list' | 'edit'

  const loadSequences = async () => {
    setLoading(true);
    try {
      const data = await getSequences();
      setSequences(data);
    } catch (error) {
      console.error('Failed to load sequences:', error);
      setMoveStatus?.('Failed to load sequences');
    } finally {
      setLoading(false);
    }
  };

  // Load sequences when modal opens
  useEffect(() => {
    if (open) {
      loadSequences();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const handleCreateNew = () => {
    setEditingSequence({
      name: 'New Sequence',
      steps: [],
    });
    setView('edit');
  };

  const handleEdit = (sequence) => {
    setEditingSequence({ ...sequence, steps: [...sequence.steps] });
    setView('edit');
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this sequence?')) return;
    
    try {
      await deleteSequence(id);
      setSequences(sequences.filter(s => s.id !== id));
      setMoveStatus?.('Sequence deleted');
    } catch (error) {
      console.error('Failed to delete sequence:', error);
      setMoveStatus?.('Failed to delete sequence');
    }
  };

  const handleExecute = async (id) => {
    setExecuting(true);
    setMoveStatus?.('Executing sequence...');
    onClose(); // Close the modal immediately after hitting run
    try {
      await executeSequence(id);
      setMoveStatus?.('Sequence executed successfully');
    } catch (error) {
      console.error('Failed to execute sequence:', error);
      const errorMsg = error.response?.data?.error || 'Execution failed';
      setMoveStatus?.(errorMsg);
    } finally {
      setExecuting(false);
    }
  };

  const handleSave = async () => {
    if (!editingSequence.name.trim()) {
      setMoveStatus?.('Please enter a sequence name');
      return;
    }

    setLoading(true);
    try {
      // Ensure steps have proper order
      const sequenceData = {
        name: editingSequence.name,
        steps: editingSequence.steps.map((step, idx) => ({
          ...step,
          order: idx + 1,
        })),
      };

      if (editingSequence.id) {
        await updateSequence(editingSequence.id, sequenceData);
        setMoveStatus?.('Sequence updated');
      } else {
        await createSequence(sequenceData);
        setMoveStatus?.('Sequence created');
      }
      
      await loadSequences();
      setView('list');
      setEditingSequence(null);
    } catch (error) {
      console.error('Failed to save sequence:', error);
      setMoveStatus?.('Failed to save sequence');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStep = () => {
    const newStep = {
      command: 'move_absolute',
      parameters: { x: 0, y: 0, z: 0, speed: 100 },
      order: editingSequence.steps.length + 1,
    };
    setEditingSequence({
      ...editingSequence,
      steps: [...editingSequence.steps, newStep],
    });
  };

  const handleRemoveStep = (index) => {
    setEditingSequence({
      ...editingSequence,
      steps: editingSequence.steps.filter((_, i) => i !== index),
    });
  };

  const handleMoveStep = (index, direction) => {
    const newSteps = [...editingSequence.steps];
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= newSteps.length) return;
    
    [newSteps[index], newSteps[newIndex]] = [newSteps[newIndex], newSteps[index]];
    setEditingSequence({ ...editingSequence, steps: newSteps });
  };

  const handleStepChange = (index, field, value) => {
    const newSteps = [...editingSequence.steps];
    if (field === 'command') {
      // Reset parameters when command changes
      const cmd = AVAILABLE_COMMANDS.find(c => c.value === value);
      const newParams = {};
      cmd?.params.forEach(p => {
        newParams[p.name] = p.default;
      });
      newSteps[index] = { ...newSteps[index], command: value, parameters: newParams };
    } else {
      newSteps[index] = {
        ...newSteps[index],
        parameters: { ...newSteps[index].parameters, [field]: value },
      };
    }
    setEditingSequence({ ...editingSequence, steps: newSteps });
  };

  const handleBackdrop = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!open) return null;

  const renderStepParams = (step, index) => {
    const cmd = AVAILABLE_COMMANDS.find(c => c.value === step.command);
    if (!cmd || cmd.params.length === 0) {
      return <span style={{ color: '#888', fontSize: '12px' }}>No parameters</span>;
    }

    return (
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
        {cmd.params.map(param => (
          <div key={param.name} style={{ flex: '1', minWidth: '100px' }}>
            <label style={{ fontSize: '11px', color: '#aaa', display: 'block', marginBottom: '2px' }}>
              {param.label}
            </label>
            {param.type === 'select' ? (
              <select
                value={step.parameters[param.name] || param.default}
                onChange={(e) => handleStepChange(index, param.name, e.target.value)}
                style={{ ...selectStyle, padding: '4px 8px', fontSize: '12px' }}
              >
                {param.options.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            ) : (
              <input
                type={param.type}
                value={step.parameters[param.name] ?? param.default}
                onChange={(e) => handleStepChange(index, param.name, 
                  param.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value
                )}
                style={{ ...inputStyle, padding: '4px 8px', fontSize: '12px' }}
              />
            )}
          </div>
        ))}
      </div>
    );
  };

  const modal = (
    <div style={modalBackdrop} onClick={handleBackdrop}>
      <div style={modalContent} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '22px' }}>
            {view === 'list' ? 'Sequence Editor' : 'Edit Sequence'}
          </h2>
          <button onClick={onClose} style={secondaryButtonStyle}>Close</button>
        </div>

        {view === 'list' ? (
          /* Sequence List View */
          <>
            <div style={{ marginBottom: '16px' }}>
              <button onClick={handleCreateNew} style={buttonStyle}>
                + New Sequence
              </button>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>Loading...</div>
            ) : sequences.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                No sequences yet. Create one to automate your FarmBot!
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {sequences.map(seq => (
                  <div key={seq.id} style={{
                    background: '#333',
                    borderRadius: '8px',
                    padding: '16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{seq.name}</div>
                      <div style={{ fontSize: '12px', color: '#888' }}>
                        {seq.steps?.length || 0} step{seq.steps?.length !== 1 ? 's' : ''}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => handleExecute(seq.id)}
                        disabled={executing}
                        style={{ ...buttonStyle, background: executing ? '#666' : '#13a73f' }}
                      >
                        ▶ Run
                      </button>
                      <button onClick={() => handleEdit(seq)} style={secondaryButtonStyle}>
                        Edit
                      </button>
                      <button onClick={() => handleDelete(seq.id)} style={dangerButtonStyle}>
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          /* Edit View */
          <>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px' }}>
                Sequence Name
              </label>
              <input
                type="text"
                value={editingSequence?.name || ''}
                onChange={(e) => setEditingSequence({ ...editingSequence, name: e.target.value })}
                style={inputStyle}
                placeholder="Enter sequence name"
              />
            </div>

            <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '16px' }}>Steps</h3>
              <button onClick={handleAddStep} style={buttonStyle}>+ Add Step</button>
            </div>

            {editingSequence?.steps?.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '30px', color: '#888', background: '#2a2a2a', borderRadius: '8px' }}>
                No steps yet. Add a step to build your sequence.
              </div>
            ) : (
              <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                {editingSequence?.steps?.map((step, index) => (
                  <div key={index} style={stepCardStyle}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ 
                          background: '#13a73f', 
                          borderRadius: '50%', 
                          width: '24px', 
                          height: '24px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          fontSize: '12px',
                          fontWeight: 'bold',
                        }}>
                          {index + 1}
                        </span>
                        <select
                          value={step.command}
                          onChange={(e) => handleStepChange(index, 'command', e.target.value)}
                          style={{ ...selectStyle, width: 'auto', minWidth: '150px' }}
                        >
                          {AVAILABLE_COMMANDS.map(cmd => (
                            <option key={cmd.value} value={cmd.value}>{cmd.label}</option>
                          ))}
                        </select>
                      </div>
                      <div style={{ display: 'flex', gap: '4px' }}>
                        <button
                          onClick={() => handleMoveStep(index, -1)}
                          disabled={index === 0}
                          style={{ ...secondaryButtonStyle, padding: '4px 8px', opacity: index === 0 ? 0.5 : 1 }}
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => handleMoveStep(index, 1)}
                          disabled={index === editingSequence.steps.length - 1}
                          style={{ ...secondaryButtonStyle, padding: '4px 8px', opacity: index === editingSequence.steps.length - 1 ? 0.5 : 1 }}
                        >
                          ↓
                        </button>
                        <button
                          onClick={() => handleRemoveStep(index)}
                          style={{ ...dangerButtonStyle, padding: '4px 8px' }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                    {renderStepParams(step, index)}
                  </div>
                ))}
              </div>
            )}

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <button onClick={() => { setView('list'); setEditingSequence(null); }} style={secondaryButtonStyle}>
                Cancel
              </button>
              <button onClick={handleSave} disabled={loading} style={buttonStyle}>
                {loading ? 'Saving...' : 'Save Sequence'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

export default SequenceEditor;
