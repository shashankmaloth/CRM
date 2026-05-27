/**
 * Redux slice for managing HCP interactions state.
 * Handles CRUD operations and API calls.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// ─── Async Thunks ────────────────────────────────────────────────────────────

export const fetchAllInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/interactions/');
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch interactions');
    }
  }
);

export const fetchInteractionsByHcp = createAsyncThunk(
  'interactions/fetchByHcp',
  async (hcpName, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/interactions/interactions/${encodeURIComponent(hcpName)}`);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch HCP interactions');
    }
  }
);

export const logInteraction = createAsyncThunk(
  'interactions/log',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/interactions/log-interaction', data);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to log interaction');
    }
  }
);

export const editInteraction = createAsyncThunk(
  'interactions/edit',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/api/interactions/edit-interaction/${id}`, data);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to update interaction');
    }
  }
);

export const deleteInteraction = createAsyncThunk(
  'interactions/delete',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/api/interactions/${id}`);
      return id;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to delete interaction');
    }
  }
);

// ─── Slice ───────────────────────────────────────────────────────────────────

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    loading: false,
    submitting: false,
    error: null,
    successMessage: null,
  },
  reducers: {
    clearMessages(state) {
      state.error = null;
      state.successMessage = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch all
    builder
      .addCase(fetchAllInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAllInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchAllInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Fetch by HCP
    builder
      .addCase(fetchInteractionsByHcp.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInteractionsByHcp.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchInteractionsByHcp.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Log interaction
    builder
      .addCase(logInteraction.pending, (state) => {
        state.submitting = true;
        state.error = null;
      })
      .addCase(logInteraction.fulfilled, (state, action) => {
        state.submitting = false;
        state.list.unshift(action.payload); // Add to top of list
        state.successMessage = 'Interaction logged successfully!';
      })
      .addCase(logInteraction.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      });

    // Edit interaction
    builder
      .addCase(editInteraction.fulfilled, (state, action) => {
        const idx = state.list.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
        state.successMessage = 'Interaction updated!';
      });

    // Delete interaction
    builder
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.list = state.list.filter((i) => i.id !== action.payload);
        state.successMessage = 'Interaction deleted.';
      });
  },
});

export const { clearMessages } = interactionsSlice.actions;
export default interactionsSlice.reducer;
