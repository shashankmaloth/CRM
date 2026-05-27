/**
 * Redux store configuration using Redux Toolkit.
 * Combines all slice reducers.
 */
import { configureStore } from '@reduxjs/toolkit';
import interactionsReducer from './slices/interactionsSlice';
import chatReducer from './slices/chatSlice';
import dashboardReducer from './slices/dashboardSlice';

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    dashboard: dashboardReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // Allow Date objects in state
    }),
});

export default store;
