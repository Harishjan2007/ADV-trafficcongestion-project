import React from 'react';
import { Header } from './components/layout/Header';
import { FilterBar } from './components/layout/FilterBar';

export const App: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Header />
      <FilterBar />
      <main style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <iframe
          src={`/index.html?apiKey=${import.meta.env.VITE_CARTO_API_KEY || ''}`}
          style={{ width: '100%', height: '100%', border: 'none' }}
          title="Chennai Traffic Intelligence Shell"
        />
      </main>
    </div>
  );
};
