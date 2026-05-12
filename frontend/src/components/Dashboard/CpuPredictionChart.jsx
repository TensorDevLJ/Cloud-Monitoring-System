import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { mlAPI } from '../../services/api';

const CPUPredictionCard = ({ instanceId }) => {
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetchPrediction();
  }, [instanceId]);

  const fetchPrediction = async () => {
    try {
      const response = await mlAPI.predictCPU(instanceId);
      setPrediction(response.data);
    } catch (error) {
      console.error("CPU Prediction Error:", error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <h2 className="text-xl font-bold mb-4">
        CPU Prediction
      </h2>

      <div className="text-4xl font-bold text-blue-500">
        {prediction?.predictions?.[0]?.predicted_cpu?.toFixed(1) || 0}%
      </div>

      <p className="text-gray-500 mt-2">
        Predicted CPU usage
      </p>
    </motion.div>
  );
};

export default CPUPredictionCard;