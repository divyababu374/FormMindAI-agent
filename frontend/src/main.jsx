import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { FormProvider } from './context/FormContext.jsx';
import { ErrorBoundary } from './components/common/ErrorBoundary.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <FormProvider>
        <App />
      </FormProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
