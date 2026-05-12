import React from 'react';
import { motion } from 'framer-motion';

const AllInsightsPanel = ({
  health,
  anomaly,
  failure,
  autoscale,
  rootCause,
  cpuPrediction,
  memoryPrediction
}) => {

  // HEALTH SCORE
  const healthScore =
    health?.healthScore ??
    health?.health_score ??
    health?.score ??
    0;

  const healthStatus =
    health?.status ??
    health?.health_status ??
    'Healthy';

  // ANOMALY
  const isAnomaly =
    anomaly?.is_anomaly ??
    anomaly?.anomalyDetected ??
    false;

  const anomalyConfidence =
    (
      anomaly?.confidence ??
      anomaly?.anomaly_score ??
      0
    ) * 100;

  // FAILURE
  const failureProbability =
    failure?.failureProbability ??
    failure?.failure_probability ??
    failure?.probability ??
    0;

  const failureStatus =
    failure?.status ??
    failure?.failureStatus ??
    'normal';

  // AUTOSCALE
  const autoscaleRecommendation =
    autoscale?.autoscaleRecommendation ??
    autoscale?.recommendation ??
    autoscale?.actions?.[0]?.action ??
    'No recommendation';

  // CPU PREDICTION
  const cpuForecast =
    cpuPrediction?.predictions?.[0]?.predicted_cpu ??
    cpuPrediction?.[0]?.predicted_cpu ??
    cpuPrediction?.predicted_cpu ??
    0;

  // MEMORY PREDICTION
  const memoryForecast =
    memoryPrediction?.predictions?.[0]?.predicted_memory ??
    memoryPrediction?.[0]?.predicted_memory ??
    memoryPrediction?.predicted_memory ??
    0;

  // ROOT CAUSE
  const primaryCause =
    rootCause?.primary_cause?.cause ??
    rootCause?.primary_cause ??
    'No major issues detected';

  const rootCauseSummary =
    rootCause?.summary ??
    'System operating normally';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6 mt-8"
    >

      <h2 className="text-2xl font-bold mb-6">
        AI / ML Insights
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* HEALTH */}
        <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-green-600">
            Health Score
          </h3>

          <p className="text-3xl font-bold mt-2">
            {Number(healthScore).toFixed(1)}%
          </p>

          <p className="text-sm text-gray-500 mt-1">
            Status: {healthStatus}
          </p>

        </div>

        {/* ANOMALY */}
        <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-orange-600">
            Anomaly Detection
          </h3>

          <p className="text-2xl font-bold mt-2">
            {isAnomaly
              ? 'Anomaly Detected'
              : 'System Stable'}
          </p>

          <p className="text-sm text-gray-500 mt-1">
            Confidence: {anomalyConfidence.toFixed(1)}%
          </p>

        </div>

        {/* FAILURE */}
        <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-red-600">
            Failure Prediction
          </h3>

          <p className="text-3xl font-bold mt-2">
            {Number(failureProbability).toFixed(1)}%
          </p>

          <p className="text-sm text-gray-500 mt-1">
            Status: {failureStatus}
          </p>

        </div>

        {/* AUTOSCALE */}
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-blue-600">
            Auto Scaling Recommendation
          </h3>

          <p className="text-lg font-bold mt-2">
            {autoscaleRecommendation}
          </p>

          <p className="text-sm text-gray-500 mt-1">
            AI scaling recommendation
          </p>

        </div>

        {/* CPU FORECAST */}
        <div className="bg-cyan-50 dark:bg-cyan-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-cyan-600">
            CPU Forecast
          </h3>

          <p className="text-3xl font-bold mt-2">
            {Number(cpuForecast).toFixed(1)}%
          </p>

          <p className="text-sm text-gray-500 mt-1">
            Predicted upcoming CPU usage
          </p>

        </div>

        {/* MEMORY FORECAST */}
        <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-xl">

          <h3 className="text-lg font-semibold text-purple-600">
            Memory Forecast
          </h3>

          <p className="text-3xl font-bold mt-2">
            {Number(memoryForecast).toFixed(1)}%
          </p>

          <p className="text-sm text-gray-500 mt-1">
            Predicted upcoming memory usage
          </p>

        </div>

      </div>

      {/* ROOT CAUSE */}
      <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 p-6 rounded-xl">

        <h3 className="text-xl font-bold text-yellow-700">
          Root Cause Analysis
        </h3>

        <p className="mt-4 text-lg font-semibold">
          {primaryCause}
        </p>

        <p className="text-gray-600 mt-2">
          {rootCauseSummary}
        </p>

      </div>

    </motion.div>
  );
};

export default AllInsightsPanel;