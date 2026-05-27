/**
 * Redux slice for managing chat state.
 * Handles messages, loading state, and agent responses.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// ─── Async Thunks ────────────────────────────────────────────────────────────

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/chat/', { message });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Chat request failed');
    }
  }
);

// ─── Slice ───────────────────────────────────────────────────────────────────

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "👋 Hi! I'm your AI CRM assistant. Tell me about your HCP interaction in natural language.\n\nFor example:\n*\"Met Dr. Rao at Apollo Hospital today. Discussed Januvia for diabetes. She was very interested and asked for samples. Follow up next Monday.\"*",
        timestamp: new Date().toISOString(),
      },
    ],
    loading: false,
    error: null,
    lastExtractedData: null,
    lastSuggestedActions: null,
  },
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({
        id: Date.now().toString(),
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    clearChat(state) {
      state.messages = [
        {
          id: 'welcome',
          role: 'assistant',
          content:
            "👋 Hi! I'm your AI CRM assistant. Tell me about your HCP interaction in natural language.",
          timestamp: new Date().toISOString(),
        },
      ];
      state.lastExtractedData = null;
      state.lastSuggestedActions = null;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.lastExtractedData = action.payload.extracted_data;
        state.lastSuggestedActions = action.payload.suggested_actions;

        // Add assistant response
        state.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: action.payload.message,
          timestamp: new Date().toISOString(),
          extractedData: action.payload.extracted_data,
          suggestedActions: action.payload.suggested_actions,
          interactionId: action.payload.interaction_id,
          agentSteps: action.payload.agent_steps,
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: `❌ Error: ${action.payload}. Please try again.`,
          timestamp: new Date().toISOString(),
          isError: true,
        });
      });
  },
});

export const { addUserMessage, clearChat, clearError } = chatSlice.actions;
export default chatSlice.reducer;
