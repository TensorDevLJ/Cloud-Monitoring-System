import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { mlAPI } from '../../services/api';

const MemoryPredictionCard = ({ instanceId }) => {
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetchPrediction();
  }, [instanceId]);

  const fetchPrediction = async () => {
    try {
      const response = await mlAPI.predictMemory(instanceId);
      setPrediction(response.data);
    } catch (error) {
      console.error("Memory Prediction Error:", error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <h2 className="text-xl font-bold mb-4">
        Memory Prediction
      </h2>

      <div className="text-4xl font-bold text-purple-500">
        {prediction?.predictions?.[0]?.predicted_memory?.toFixed(1) || 0}%
      </div>

      <p className="text-gray-500 mt-2">
        Predicted memory usage
      </p>
    </motion.div>
  );
};

export default MemoryPredictionCard;