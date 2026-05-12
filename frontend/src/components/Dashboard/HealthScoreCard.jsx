import React, { useEffect, useState } from 'react';
import GaugeChart from 'react-gauge-chart';
import { motion } from 'framer-motion';
import { mlAPI } from '../../services/api';

const HealthScoreCard = ({ instanceId }) => {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const response = await mlAPI.getHealthScore(instanceId);
      setHealth(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <h2 className="text-2xl font-bold mb-4">
        Health Score
      </h2>

      <GaugeChart
        id="health-gauge"
        nrOfLevels={20}
        percent={(health?.healthScore || 0) / 100}
      />

      <div className="text-center mt-4">
        <h1 className="text-4xl font-bold">
          {health?.healthScore || 0}%
        </h1>

        <p className="text-gray-500 mt-2 capitalize">
          {health?.status || 'Healthy'}
        </p>
      </div>
    </motion.div>
  );
};

export default HealthScoreCard;