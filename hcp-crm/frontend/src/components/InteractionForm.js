import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logInteraction } from '../store/slices/interactionsSlice';
import { toast } from 'react-toastify';
import './InteractionForm.css';

/**
 * Structured form for logging HCP interactions.
 * Validates and submits data to the backend.
 */
function InteractionForm() {
  const dispatch = useDispatch();
  const { submitting } = useSelector((state) => state.interactions);

  const [formData, setFormData] = useState({
    hcp_name: '',
    specialty: '',
    hospital: '',
    interaction_type: 'Visit',
    datetime: '',
    products: '',
    notes: '',
    follow_up_date: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.hcp_name.trim()) {
      toast.error('HCP Name is required');
      return;
    }

    // Convert datetime strings to ISO format
    const payload = {
      ...formData,
      datetime: formData.datetime ? new Date(formData.datetime).toISOString() : null,
      follow_up_date: formData.follow_up_date ? new Date(formData.follow_up_date).toISOString() : null,
    };

    try {
      await dispatch(logInteraction(payload)).unwrap();
      toast.success('✅ Interaction logged successfully!');
      // Reset form
      setFormData({
        hcp_name: '',
        specialty: '',
        hospital: '',
        interaction_type: 'Visit',
        datetime: '',
        products: '',
        notes: '',
        follow_up_date: '',
      });
    } catch (err) {
      toast.error(`❌ ${err}`);
    }
  };

  return (
    <form className="interaction-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        {/* HCP Name */}
        <div className="form-group">
          <label htmlFor="hcp_name">
            HCP Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="hcp_name"
            name="hcp_name"
            value={formData.hcp_name}
            onChange={handleChange}
            placeholder="e.g., Dr. Priya Rao"
            required
          />
        </div>

        {/* Specialty */}
        <div className="form-group">
          <label htmlFor="specialty">Specialty</label>
          <input
            type="text"
            id="specialty"
            name="specialty"
            value={formData.specialty}
            onChange={handleChange}
            placeholder="e.g., Endocrinology"
          />
        </div>

        {/* Hospital */}
        <div className="form-group">
          <label htmlFor="hospital">Hospital / Clinic</label>
          <input
            type="text"
            id="hospital"
            name="hospital"
            value={formData.hospital}
            onChange={handleChange}
            placeholder="e.g., Apollo Hospital"
          />
        </div>

        {/* Interaction Type */}
        <div className="form-group">
          <label htmlFor="interaction_type">Interaction Type</label>
          <select
            id="interaction_type"
            name="interaction_type"
            value={formData.interaction_type}
            onChange={handleChange}
          >
            <option value="Visit">Visit</option>
            <option value="Call">Call</option>
            <option value="Meeting">Meeting</option>
          </select>
        </div>

        {/* Date & Time */}
        <div className="form-group">
          <label htmlFor="datetime">Date & Time</label>
          <input
            type="datetime-local"
            id="datetime"
            name="datetime"
            value={formData.datetime}
            onChange={handleChange}
          />
        </div>

        {/* Follow-up Date */}
        <div className="form-group">
          <label htmlFor="follow_up_date">Follow-up Date</label>
          <input
            type="datetime-local"
            id="follow_up_date"
            name="follow_up_date"
            value={formData.follow_up_date}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Products */}
      <div className="form-group">
        <label htmlFor="products">Products Discussed</label>
        <input
          type="text"
          id="products"
          name="products"
          value={formData.products}
          onChange={handleChange}
          placeholder="e.g., Metformin XR, Januvia"
        />
      </div>

      {/* Notes */}
      <div className="form-group">
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows="4"
          placeholder="Additional details about the interaction..."
        />
      </div>

      {/* Submit */}
      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? 'Saving...' : '✅ Log Interaction'}
      </button>
    </form>
  );
}

export default InteractionForm;
