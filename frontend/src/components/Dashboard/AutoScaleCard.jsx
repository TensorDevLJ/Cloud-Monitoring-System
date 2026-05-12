import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { mlAPI } from '../../services/api';

const AutoScaleCard = ({ instanceId }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchRecommendation();
  }, [instanceId]);

  const fetchRecommendation = async () => {
    try {
      const response = await mlAPI.getAutoscaleRecommendation(instanceId);
      setData(response.data);
    } catch (error) {
      console.error("Autoscale Error:", error);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <h2 className="text-xl font-bold mb-4">
        Auto Scaling
      </h2>

      <div className="text-2xl font-bold text-blue-500">
        {data?.recommendation || "No Recommendation"}
      </div>

      <p className="text-gray-500 mt-2">
        ML scaling recommendation
      </p>
    </motion.div>
  );
};

export default AutoScaleCard;