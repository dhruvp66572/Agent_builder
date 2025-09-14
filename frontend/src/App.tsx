import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/ui/toast';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <ToastProvider>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workflow/:id?" element={<WorkflowBuilder />} />
        </Routes>
      </ToastProvider>
    </div>
  );
}

export default App;