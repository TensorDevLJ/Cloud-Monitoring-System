import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiAlertTriangle } from 'react-icons/fi';
import { mlAPI } from '../../services/api';

const FailurePredictionCard = ({ instanceId }) => {
  const [failure, setFailure] = useState(null);

  useEffect(() => {
    fetchFailure();
  }, []);

  const fetchFailure = async () => {
    try {
      const response = await mlAPI.predictFailure(instanceId);
      setFailure(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <div className="flex items-center gap-3 mb-4">
        <FiAlertTriangle className="text-red-500 text-2xl" />
        <h2 className="text-2xl font-bold">
          Failure Prediction
        </h2>
      </div>

      <h1 className="text-5xl font-bold text-red-500">
        {failure?.failure_probability || 0}%
      </h1>

      <p className="mt-3 text-gray-500 capitalize">
        {failure?.severity || 'normal'}
      </p>

      <div className="mt-4 text-sm">
        {failure?.recommendation}
      </div>
    </motion.div>
  );
};

export default FailurePredictionCard;