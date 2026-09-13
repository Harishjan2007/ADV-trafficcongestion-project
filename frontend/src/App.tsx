import React from 'react';

export const App: React.FC = () => {
  return (
    <main style={{ height: '100vh', width: '100vw', overflow: 'hidden', margin: 0, padding: 0 }}>
      <iframe
        src={`/index.html?apiKey=${import.meta.env.VITE_CARTO_API_KEY || ''}`}
        style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
        title="Traffic Intelligence Platform"
      />
    </main>
  );
};

