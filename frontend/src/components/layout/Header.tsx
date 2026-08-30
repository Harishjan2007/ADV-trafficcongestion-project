import React from 'react';
import { useTrafficStore } from '../../store/trafficStore';
import { Navigation } from 'lucide-react';

export const Header: React.FC = () => {
  const { currentHour, cityOverview } = useTrafficStore();
  const timeFormatted = `${String(currentHour).padStart(2, '0')}:00 IST`;

  return (
    <header style={{
      height: '64px',
      background: 'var(--bg-glass-heavy)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          background: 'rgba(6, 182, 212, 0.15)',
          border: '1px solid var(--border-accent)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Navigation style={{ color: 'var(--color-flow)', width: 20, height: 20 }} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '15px', fontWeight: 800, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Chennai Traffic Intelligence Platform
            </h1>
            <span className="badge badge-simulated">{cityOverview?.data_state || 'SIMULATED'}</span>
            <span className="badge badge-pred">ML READY</span>
          </div>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Metropolitan Traffic Authority Interactive Command & Spatial Decision System
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Scenario Clock
          </div>
          <div style={{ fontSize: '14px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-flow)' }}>
            {timeFormatted}
          </div>
        </div>
        <div style={{ height: '28px', width: '1px', background: 'var(--border-subtle)' }} />
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            System Health
          </div>
          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-low)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-low)', display: 'inline-block' }} />
            100% ONLINE
          </div>
        </div>
      </div>
    </header>
  );
};
