// src/index.js
import React from 'react';
import './index.css';
import ReactDOM from 'react-dom/client';
import F1Predictor from './components/F1Predictor.jsx';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <F1Predictor />
  </React.StrictMode>
);