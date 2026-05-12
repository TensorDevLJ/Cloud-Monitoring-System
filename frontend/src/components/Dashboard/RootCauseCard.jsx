import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiSearch } from 'react-icons/fi';
import { mlAPI } from '../../services/api';

const RootCauseCard = ({ instanceId }) => {
  const [rootCause, setRootCause] = useState(null);

  useEffect(() => {
    fetchRootCause();
  }, []);

  const fetchRootCause = async () => {
    try {
      const response = await mlAPI.getSummary(instanceId);
      setRootCause(response.data.rootCause);
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
        <FiSearch className="text-blue-500 text-2xl" />
        <h2 className="text-2xl font-bold">
          Root Cause Analysis
        </h2>
      </div>

      <h3 className="text-xl font-semibold">
        {rootCause?.primary_cause?.cause || 'No issue detected'}
      </h3>

      <p className="mt-3 text-gray-500">
        {rootCause?.summary}
      </p>

      <div className="mt-4 text-sm">
        {rootCause?.primary_cause?.recommendation}
      </div>
    </motion.div>
  );
};

export default RootCauseCard;