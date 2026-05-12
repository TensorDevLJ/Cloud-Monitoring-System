import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { mlAPI } from '../../services/api';

const AnomalyCard = ({ instanceId }) => {
  const [anomaly, setAnomaly] = useState(null);

  useEffect(() => {
    fetchAnomaly();
  }, [instanceId]);

  const fetchAnomaly = async () => {
    try {
      const response = await mlAPI.detectAnomaly(instanceId);
      setAnomaly(response.data);
    } catch (error) {
      console.error("Anomaly Error:", error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <h2 className="text-xl font-bold mb-4">
        Anomaly Detection
      </h2>

      <div
        className={`text-3xl font-bold ${
          anomaly?.is_anomaly
            ? 'text-red-500'
            : 'text-green-500'
        }`}
      >
        {anomaly?.is_anomaly ? 'Anomaly Detected' : 'Normal'}
      </div>

      <p className="text-gray-500 mt-2">
        Confidence:
        {" "}
        {(anomaly?.confidence * 100 || 0).toFixed(1)}%
      </p>
    </motion.div>
  );
};

export default AnomalyCard;