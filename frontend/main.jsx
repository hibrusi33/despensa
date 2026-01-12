import React from 'react';
import ReactDOM from 'react-dom/client';
import PantryApp from './PantryApp.jsx';
import { AuthProvider } from './AuthContext.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <PantryApp />
    </AuthProvider>
  </React.StrictMode>
);
