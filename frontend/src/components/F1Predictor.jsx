const NumberInput = ({ label, value, onChange, field, step = 'any', min, max }) => {
  const inputRef = React.useRef(null);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;

    // Allow numbers, decimal point, and ensure cursor stays
    const sanitizedValue = inputValue.replace(/[^0-9.]/g, '');

    // Prevent unnecessary re-renders
    e.target.value = sanitizedValue;

    // Call onChange with the sanitized value
    onChange(field, sanitizedValue);
  };

  const handleIncrement = (increment) => {
    const currentValue = parseFloat(value) || 0;
    const stepValue = step === 'any' ? 0.1 : parseFloat(step);

    const newValue = increment
      ? currentValue + stepValue
      : currentValue - stepValue;

    // Ensure input stays focused
    if (inputRef.current) {
      inputRef.current.focus();
    }

    onChange(field, newValue.toFixed(2));
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value === '' ? '' : value}
          onChange={handleInputChange}
          className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-f1-red focus:border-transparent pr-20"
          onFocus={(e) => {
            // Move cursor to end of input
            e.target.setSelectionRange(
              e.target.value.length,
              e.target.value.length
            );
          }}
        />
        <div className="absolute right-0 top-0 h-full flex">
          <button
            type="button"
            onClick={() => handleIncrement(false)}
            className="px-3 h-full hover:bg-white/10 text-gray-300 hover:text-white border-l border-white/20"
          >
            -
          </button>
          <button
            type="button"
            onClick={() => handleIncrement(true)}
            className="px-3 h-full hover:bg-white/10 text-gray-300 hover:text-white border-l border-white/20"
          >
            +
          </button>
        </div>
      </div>
    </div>
  );
};
import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CarFront, Flag, Timer, Trophy } from 'lucide-react';

const F1Predictor = () => {
  const [formData, setFormData] = useState({
    gridPosition: 1,
    q1Time: 80.00,
    q2Time: 0.00,
    q3Time: 0.00,
    teamPoints: 0,
    teamAvgPoints: 0.00,
    driverPoints: 0,
    recentAvgPosition: 10.00,
    constructor: 0,
    track: 0,
    laps: 50,
    raceRound: 1,
    trackExperience: 0,
    avgTrackPosition: 10.00
  });

  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const constructors = [
    "Mercedes", "Red Bull", "Ferrari", "McLaren", "Alpine",
    "AlphaTauri", "Aston Martin", "Williams", "Alfa Romeo", "Haas"
  ];

  const tracks = [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
    "Monaco", "Spain", "Canada", "Austria", "Britain", "Hungary",
    "Belgium", "Netherlands", "Italy", "Singapore", "Japan",
    "Qatar", "USA", "Mexico", "Brazil", "Vegas", "Abu Dhabi"
  ];

  // Modified handleChange to allow empty values
  const handleChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? '' : Number(value)
    }));
  };

  // New increment/decrement helper
  const handleIncrement = (field, increment) => {
    const step = ['gridPosition', 'teamPoints', 'driverPoints', 'laps', 'raceRound'].includes(field) ? 1 : 0.1;
    let currentValue = formData[field] || 0;
    const newValue = increment ? currentValue + step : currentValue - step;

    // Apply min/max constraints for grid position
    if (field === 'gridPosition') {
      handleChange(field, Math.min(Math.max(1, newValue), 20));
    } else {
      handleChange(field, Number(newValue.toFixed(2)));
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    const requestData = {
      GridPosition: formData.gridPosition,
      Q1_seconds: formData.q1Time,
      Q2_seconds: formData.q2Time,
      Q3_seconds: formData.q3Time,
      BestQualiTime: Math.min(...[formData.q1Time, formData.q2Time, formData.q3Time].filter(t => t > 0)),
      PositionsGained: 0,
      year: new Date().getFullYear(),
      round: formData.raceRound,
      Points: formData.driverPoints,
      laps: formData.laps,
      Constructor_encoded: formData.constructor,
      raceName_encoded: formData.track,
      TeamSeasonPoints: formData.teamPoints,
      TeamAvgPoints: formData.teamAvgPoints,
      RecentAvgPosition: formData.recentAvgPosition,
      TrackExperience: formData.trackExperience || 0,
      AvgTrackPosition: formData.avgTrackPosition || 10
    };

    console.log('Attempting to send request to:', 'https://your-backend-api.com/api/predict');
    console.log('With data:', requestData);

    try {
      const response = await fetch('https://your-backend-api.com/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.log('Error text:', errorText);
        throw new Error(`Server error: ${errorText}`);
      }

      const data = await response.json();
      console.log('Received predictions:', data);
      setPredictions(data);
    } catch (err) {
      console.error('Full error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Input field component with increment/decrement buttons
  const NumberInput = ({ label, value, onChange, field, step = 'any', min, max }) => {
    const handleInputChange = (e) => {
      const inputValue = e.target.value;
      // Allow only numbers, decimal point, and empty string
      const sanitizedValue = inputValue.replace(/[^0-9.]/g, '');
      onChange(field, sanitizedValue);
    };

    return (
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
        <div className="relative">
          <input
            type="text"
            value={value === '' ? '' : value}
            onChange={handleInputChange}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-f1-red focus:border-transparent pr-20"
          />
          <div className="absolute right-0 top-0 h-full flex">
            <button
              type="button"
              onClick={() => handleIncrement(field, false)}
              className="px-3 h-full hover:bg-white/10 text-gray-300 hover:text-white border-l border-white/20"
            >
              -
            </button>
            <button
              type="button"
              onClick={() => handleIncrement(field, true)}
              className="px-3 h-full hover:bg-white/10 text-gray-300 hover:text-white border-l border-white/20"
            >
              +
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold flex items-center justify-center gap-4">
            <CarFront className="h-12 w-12 text-f1-red" />
            Formula 1 Race Predictor
          </h1>
          <p className="text-xl text-gray-400">Enter race information to predict outcomes</p>
        </div>

        {/* Main Form Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Qualifying Section */}
          <div className="bg-white/5 rounded-xl p-6 backdrop-blur-sm border border-white/10">
            <div className="flex items-center gap-3 mb-6">
              <Timer className="h-6 w-6 text-f1-red" />
              <h2 className="text-2xl font-bold">Qualifying</h2>
            </div>

            <div className="space-y-4">
              <NumberInput
                label="Grid Position"
                value={formData.gridPosition}
                onChange={handleChange}
                field="gridPosition"
                min={1}
                max={20}
              />
              <NumberInput
                label="Q1 Time (seconds)"
                value={formData.q1Time}
                onChange={handleChange}
                field="q1Time"
                step="0.1"
              />
              <NumberInput
                label="Q2 Time (seconds)"
                value={formData.q2Time}
                onChange={handleChange}
                field="q2Time"
                step="0.1"
              />
              <NumberInput
                label="Q3 Time (seconds)"
                value={formData.q3Time}
                onChange={handleChange}
                field="q3Time"
                step="0.1"
              />
            </div>
          </div>

          {/* Team Performance Section */}
          <div className="bg-white/5 rounded-xl p-6 backdrop-blur-sm border border-white/10">
            <div className="flex items-center gap-3 mb-6">
              <Trophy className="h-6 w-6 text-f1-red" />
              <h2 className="text-2xl font-bold">Team Performance</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Constructor
                </label>
                <select
                  value={formData.constructor}
                  onChange={(e) => handleChange('constructor', Number(e.target.value))}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-f1-red focus:border-transparent"
                >
                  {constructors.map((team, index) => (
                    <option key={team} value={index}>{team}</option>
                  ))}
                </select>
              </div>

              <NumberInput
                label="Team Points"
                value={formData.teamPoints}
                onChange={handleChange}
                field="teamPoints"
                min={0}
              />
              <NumberInput
                label="Average Points"
                value={formData.teamAvgPoints}
                onChange={handleChange}
                field="teamAvgPoints"
                step="0.1"
                min={0}
              />
              <NumberInput
                label="Driver Points"
                value={formData.driverPoints}
                onChange={handleChange}
                field="driverPoints"
                min={0}
              />
            </div>
          </div>

          {/* Race Information Section */}
          <div className="bg-white/5 rounded-xl p-6 backdrop-blur-sm border border-white/10">
            <div className="flex items-center gap-3 mb-6">
              <Flag className="h-6 w-6 text-f1-red" />
              <h2 className="text-2xl font-bold">Race Information</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Track
                </label>
                <select
                  value={formData.track}
                  onChange={(e) => handleChange('track', Number(e.target.value))}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-f1-red focus:border-transparent"
                >
                  {tracks.map((track, index) => (
                    <option key={track} value={index}>{track}</option>
                  ))}
                </select>
              </div>

              <NumberInput
                label="Race Laps"
                value={formData.laps}
                onChange={handleChange}
                field="laps"
                min={1}
              />
              <NumberInput
                label="Race Round"
                value={formData.raceRound}
                onChange={handleChange}
                field="raceRound"
                min={1}
                max={23}
              />
              <NumberInput
                label="Recent Average Position"
                value={formData.recentAvgPosition}
                onChange={handleChange}
                field="recentAvgPosition"
                step="0.1"
                min={1}
              />
            </div>
          </div>
        </div>

        {/* Track History Section */}
        <div className="mt-8 bg-white/5 rounded-xl p-6 backdrop-blur-sm border border-white/10">
          <div className="flex items-center gap-3 mb-6">
            <Flag className="h-6 w-6 text-f1-red" />
            <h2 className="text-2xl font-bold">Track History</h2>
          </div>
          <div className="space-y-4">
            <NumberInput
              label="Previous Races at Track"
              value={formData.trackExperience}
              onChange={handleChange}
              field="trackExperience"
              min={0}
            />
            <NumberInput
              label="Average Finish Position at Track"
              value={formData.avgTrackPosition}
              onChange={handleChange}
              field="avgTrackPosition"
              step="0.1"
              min={1}
              max={20}
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-f1-red hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg transform transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Calculating...' : 'Make Predictions'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 text-white px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* Predictions Display */}
        {predictions && (
          <div className="mt-12 space-y-6">
            <h2 className="text-3xl font-bold text-center mb-8">Race Predictions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(predictions).map(([outcome, probability]) => (
                <div key={outcome} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 shadow-lg">
                  <h3 className="text-lg font-semibold mb-4">{outcome}</h3>
                  <div className="relative">
                    <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-f1-red transition-all duration-1000 ease-out"
                        style={{ width: `${probability * 100}%` }}
                      />
                    </div>
                    <div className="mt-3 text-center">
                      <span className="text-3xl font-bold">{(probability * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Feature Importance Chart */}
            <div className="mt-8 bg-white/5 rounded-xl p-6 backdrop-blur-sm border border-white/10">
              <h3 className="text-2xl font-bold mb-6">Prediction Factors Impact</h3>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      { name: 'Grid Position', value: 0.8 },
                      { name: 'Q3 Time', value: 0.6 },
                      { name: 'Team Points', value: 0.7 },
                      { name: 'Track Experience', value: 0.4 },
                      { name: 'Recent Performance', value: 0.5 }
                    ]}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                      dataKey="name"
                      stroke="#ffffff"
                      tick={{ fill: '#ffffff' }}
                    />
                    <YAxis
                      stroke="#ffffff"
                      tick={{ fill: '#ffffff' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#e10600"
                      strokeWidth={3}
                      dot={{ fill: '#e10600', strokeWidth: 2 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default F1Predictor;