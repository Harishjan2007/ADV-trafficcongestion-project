import React from 'react';
import { useTrafficStore } from '../../store/trafficStore';
import { Play, Pause, Sparkles, MoveRight } from 'lucide-react';

export const FilterBar: React.FC = () => {
  const {
    currentHour,
    isPlaying,
    setHour,
    togglePlay,
    layers,
    setLayers,
    selectedZone,
    setZoneFilter,
    selectedSeverity,
    setSeverityFilter
  } = useTrafficStore();

  const timeFormatted = `${String(currentHour).padStart(2, '0')}:00`;

  return (
    <nav style={{
      height: '52px',
      background: 'var(--bg-surface-primary)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      zIndex: 40,
      gap: '12px'
    }}>
      <div style={{ display: 'flex', alignItem: 'center', gap: '10px' }}>
        {/* Time Slider Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          background: 'var(--bg-surface-secondary)',
          padding: '4px 12px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)'
        }}>
          <button
            onClick={togglePlay}
            style={{
              background: 'var(--color-flow)',
              color: 'var(--bg-core)',
              border: 'none',
              width: 28,
              height: 28,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
          </button>
          <input
            type="range"
            min="0"
            max="23"
            step="1"
            value={currentHour}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setHour(parseInt(e.target.value, 10))}
            style={{ width: 150, accentColor: 'var(--color-flow)', cursor: 'pointer' }}
          />
          <span style={{ fontSize: '12px', fontWeight: 700, fontFamily: 'var(--font-mono)', minWidth: 45 }}>
            {timeFormatted}
          </span>
        </div>

        {/* Zone Selector */}
        <select
          value={selectedZone}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setZoneFilter(e.target.value)}
          className="select-control"
          style={{
            background: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-primary)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px'
          }}
        >
          <option value="">All Chennai Zones</option>
          <option value="Central Zone">Central Zone</option>
          <option value="South Zone">South Zone</option>
          <option value="North Zone">North Zone</option>
          <option value="West Zone">West Zone</option>
          <option value="OMR IT Corridor">OMR IT Corridor</option>
        </select>

        {/* Severity Selector */}
        <select
          value={selectedSeverity}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSeverityFilter(e.target.value)}
          className="select-control"
          style={{
            background: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-primary)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px'
          }}
        >
          <option value="">All Severities</option>
          <option value="Severe">🔴 Severe (CI ≥ 75)</option>
          <option value="High">🟠 High (CI 55-75)</option>
          <option value="Moderate">🟡 Moderate (CI 30-55)</option>
          <option value="Low">🟢 Low (CI &lt; 30)</option>
        </select>
      </div>

      {/* Layer Toggles */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          className={`chip-toggle ${layers.congestion ? 'active' : ''}`}
          onClick={() => setLayers({ congestion: !layers.congestion })}
        >
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--color-severe)' }} />
          Congestion
        </button>
        <button
          className={`chip-toggle ${layers.accidents ? 'active' : ''}`}
          onClick={() => setLayers({ accidents: !layers.accidents })}
        >
          <span style={{ color: 'var(--color-accident)' }}>⚠</span> Incidents
        </button>
        <button
          className={`chip-toggle ${layers.flow ? 'active' : ''}`}
          onClick={() => setLayers({ flow: !layers.flow })}
        >
          <MoveRight size={12} /> Flow
        </button>
        <button
          className={`chip-toggle ${layers.prediction ? 'active' : ''}`}
          onClick={() => setLayers({ prediction: !layers.prediction })}
        >
          <Sparkles size={12} style={{ color: 'var(--color-prediction)' }} /> +30m Forecast
        </button>
      </div>
    </nav>
  );
};
