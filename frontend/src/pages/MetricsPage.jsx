import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { metricsAPI, instancesAPI, mlAPI } from '../services/api';
import { Cpu, HardDrive, Database, Wifi, Server } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAutoRefresh } from '../hooks/useAutoRefresh';
import RefreshControl from '../components/RefreshControl';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const MetricsPage = () => {
  const [instances, setInstances] = useState([]);
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [instancesLoaded, setInstancesLoaded] = useState(false);
  const [mlData, setMlData] = useState(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // Fetch instances on mount
  const fetchInstances = useCallback(async () => {
    try {
      const res = await instancesAPI.list();
      setInstances(res.data);
      if (res.data.length > 0 && !selectedInstance) {
        setSelectedInstance(res.data[0]);
      }
      setInstancesLoaded(true);
    } catch (err) {
      console.error('Error:', err);
      toast.error('Failed to load instances');
    }
  }, [selectedInstance]);

  // Fetch metrics for selected instance
 const fetchMetrics = useCallback(async () => {
  if (!selectedInstance) return;

  try {
    const res = await metricsAPI.getAll(selectedInstance.instance_id);

    setMetrics(res.data);

    // ✅ ADD THIS HERE (IMPORTANT)
    setHistory(prev => [
      ...prev.slice(-20), // keep last 20 points
      {
        time: new Date().toLocaleTimeString().slice(0,5),
        cpu: res.data.cpu?.usage_percent,
        memory: res.data.memory?.usage_percent,
        disk: res.data.disk?.usage_percent,
        rx: res.data.network?.rx_bytes,
        tx: res.data.network?.tx_bytes
      }
    ]);

  } catch (err) {
    console.error('Error:', err);
    toast.error('Failed to load metrics');
  }
}, [selectedInstance]);
// const fetchML = useCallback(async () => {
//   if (!selectedInstance) return;

//   try {
//     setMlLoading(true);

//     const res = await mlAPI.getSummary(selectedInstance.instance_id);
//     setMlData(res.data);

//     // ✅ ALERTS (STEP 5)
//     if (res.data?.anomaly_detection?.is_anomaly) {
//       toast.error("🚨 Anomaly detected! System unstable");
//     }

//     if (res.data?.health_score?.health_score < 40) {
//       toast.error("⚠️ System health is critical!");
//     }

//     setMlLoading(false);

//   } catch (err) {
//     console.error('ML Error:', err);
//     setMlLoading(false);
//   }
// }, [selectedInstance]);

const fetchML = useCallback(async () => {
  if (!selectedInstance) return;

  try {
    setMlLoading(true);

    const res = await mlAPI.getSummary(
      selectedInstance.instance_id
    );
    console.log("FULL ML RESPONSE:", res.data);

    console.log("ML DATA:", res.data);

    if (
      res.data?.anomaly_detection?.is_anomaly
    ) {
      toast.dismiss();
      toast.error(
        "🚨 Anomaly detected! System unstable"
      );
    }

    if (
      res.data?.health_score?.health_score < 40
    ) {
      toast.dismiss();
      toast.error(
        "⚠️ System health is critical!"
      );
    }

    setMlData({
  healthScore:
  Number(
    res.data?.health_score?.health_score ??
    res.data?.healthScore ??
    0
  ),

  anomaly:
    res.data?.anomaly_detection?.is_anomaly ??
    false,

  failureProbability:
  Number(
    res.data?.failure_prediction?.failure_probability ??
    0
  ),

  cpuPrediction:
    res.data?.cpu_prediction ??
    { predictions: [] },

  memoryPrediction:
    res.data?.memory_prediction ??
    { predictions: [] },

  autoscaleRecommendation:
    res.data?.autoscale?.recommendation ??
    "No recommendation",

  rootCause:
    res.data?.root_cause ??
    {}
});

    setMlLoading(false);

  } catch (err) {
    console.error('ML Error:', err);
    setMlLoading(false);
  }
}, [selectedInstance]);
 

const formatPredictionData = (data) => {
  return data?.map(item => ({
    time: item.timestamp.slice(11, 16),
    cpu: item.predicted_cpu
  })) || [];
};
const formatMemoryData = (data) => {
  return data?.map(item => ({
    time: item.timestamp.slice(11, 16),
    memory: item.predicted_memory
  })) || [];
};

  // Auto-refresh for instances (once)
  // Auto-refresh for instances (once)
  useAutoRefresh(fetchInstances, 0, 300);
  useAutoRefresh(fetchML, 15, 300, [selectedInstance]);

  // Auto-refresh for metrics with configurable interval
  const { loading, refreshing, refreshInterval, setRefreshInterval, manualRefresh } =
    useAutoRefresh(fetchMetrics, 15, 300, [selectedInstance]);

  if (!instancesLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in pt-24">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Metrics</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Detailed system metrics</p>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          {/* Instance Selector */}
          <select
            value={selectedInstance?.instance_id || ''}
            onChange={(e) => {
              const inst = instances.find(i => i.instance_id === e.target.value);
              setSelectedInstance(inst);
            }}
            className="px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
          >
            {instances.map(inst => (
              <option key={inst.id} value={inst.instance_id}>
                {inst.name} ({inst.instance_id})
              </option>
            ))}
          </select>
          <RefreshControl
            refreshInterval={refreshInterval}
            setRefreshInterval={setRefreshInterval}
            refreshing={refreshing}
            onManualRefresh={manualRefresh}
          />
        </div>
      </div>

      {!metrics && !loading && (
        <div className="glass-card p-12 text-center">
          <Server className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500">Select an instance to view metrics</p>
        </div>
      )}

      {metrics && (
        <>
          {/* CPU Section */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Cpu className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">CPU</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricItem label="Usage" value={`${metrics.cpu?.usage_percent?.toFixed(1)}%`} color={getColor(metrics.cpu?.usage_percent)} />
              <MetricItem label="Load 1min" value={metrics.cpu?.load_1min?.toFixed(2)} />
              <MetricItem label="Load 5min" value={metrics.cpu?.load_5min?.toFixed(2)} />
              <MetricItem label="Load 15min" value={metrics.cpu?.load_15min?.toFixed(2)} />
            </div>
            {metrics.cpu?.per_core && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Per Core Usage</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {metrics.cpu.per_core.map((core, i) => (
                    <div key={i} className="text-center p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <p className="text-xs text-gray-500">Core {i}</p>
                      <p className={`font-bold ${getColor(core)}`}>{core.toFixed(1)}%</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Memory Section */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <HardDrive className="w-5 h-5 text-green-500" />
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Memory</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricItem label="Usage" value={`${metrics.memory?.usage_percent?.toFixed(1)}%`} color={getColor(metrics.memory?.usage_percent)} />
              <MetricItem label="Total" value={formatBytes(metrics.memory?.total)} />
              <MetricItem label="Used" value={formatBytes(metrics.memory?.used)} />
              <MetricItem label="Available" value={formatBytes(metrics.memory?.available)} />
            </div>
            {metrics.memory?.swap_total > 0 && (
              <div className="mt-4 grid grid-cols-2 gap-4">
                <MetricItem label="Swap Total" value={formatBytes(metrics.memory?.swap_total)} />
                <MetricItem label="Swap Used" value={formatBytes(metrics.memory?.swap_used)} />
              </div>
            )}
          </div>

          {/* Disk Section */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Disk</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricItem label="Usage" value={`${metrics.disk?.usage_percent?.toFixed(1)}%`} color={getColor(metrics.disk?.usage_percent)} />
              <MetricItem label="Total" value={formatBytes(metrics.disk?.total)} />
              <MetricItem label="Used" value={formatBytes(metrics.disk?.used)} />
              <MetricItem label="Available" value={formatBytes(metrics.disk?.available)} />
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <MetricItem label="Read Rate" value={formatBytes(metrics.disk?.read_bytes) + '/s'} />
              <MetricItem label="Write Rate" value={formatBytes(metrics.disk?.write_bytes) + '/s'} />
            </div>
          </div>

          {/* Network Section */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Wifi className="w-5 h-5 text-purple-500" />
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Network</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <MetricItem label="RX Bytes" value={formatBytes(metrics.network?.rx_bytes)} />
              <MetricItem label="TX Bytes" value={formatBytes(metrics.network?.tx_bytes)} />
              <MetricItem label="RX Packets" value={Math.round(metrics.network?.rx_packets || 0).toLocaleString()} />
              <MetricItem label="TX Packets" value={Math.round(metrics.network?.tx_packets || 0).toLocaleString()} />
              <MetricItem label="RX Errors" value={Math.round(metrics.network?.rx_errors || 0)} color={metrics.network?.rx_errors > 10 ? 'text-red-500' : ''} />
              <MetricItem label="TX Errors" value={Math.round(metrics.network?.tx_errors || 0)} color={metrics.network?.tx_errors > 10 ? 'text-red-500' : ''} />
            </div>
          </div>

          {/* Uptime */}
          {metrics.uptime_seconds && (
            <div className="glass-card p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">Uptime:</span> {formatUptime(metrics.uptime_seconds)}
              </p>
            </div>
          )}
         


       
          {/* ML Insights */}

{!mlData && !mlLoading && (
  <div className="glass-card p-4 text-center text-gray-500">
    No ML data available
  </div>
)}  

{mlLoading && (
  <div className="glass-card p-4 text-center">
    <p className="text-gray-500">Loading ML Insights...</p>
  </div>
)}
<div className="glass-card p-6">
  <h2 className="text-lg font-bold mb-4">Live Metrics</h2>
 {history.length > 0 && (
  <div className="mt-6">
  <h3 className="text-lg font-semibold mb-3">CPU Usage (Live)</h3>
  <p className="text-xs text-gray-400">
  Last updated: {new Date().toLocaleTimeString()}
</p>

  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={history}>
      <XAxis dataKey="time" />
      <YAxis width={40} />
      <Tooltip />
      <Line
  type="monotone"
  dataKey="cpu"
  stroke="#3b82f6"
  strokeWidth={2}
  animationDuration={500}
/>
      {/* <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} /> */}
    </LineChart>
  </ResponsiveContainer>
</div>

)}
</div>

{history.length > 0 && (
<div className="glass-card p-6">
 
  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-3">Memory Usage (Live)</h3>

<p className="text-xs text-gray-400">
  Last updated: {new Date().toLocaleTimeString()}
</p>

    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={history}>
        <XAxis dataKey="time" />
        <YAxis width={40} />
        <Tooltip />
       <Line
  type="monotone"
  dataKey="memory"
  stroke="#3b82f6"
  strokeWidth={2}
  animationDuration={500}
/>
      </LineChart>
    </ResponsiveContainer>
  </div>

  </div>
)}


{history.length > 0 && (
<div className="glass-card p-6">

  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-3">Disk Usage (Live)</h3>

<p className="text-xs text-gray-400">
  Last updated: {new Date().toLocaleTimeString()}
</p>

    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={history}>
        <XAxis dataKey="time" />
        <YAxis width={40} />
        <Tooltip />
        <Line
  type="monotone"
  dataKey="disk"
  stroke="#f97316"
  strokeWidth={2}
  animationDuration={500}
/>
        {/* <Line type="monotone" dataKey="disk" stroke="#f97316" strokeWidth={2} /> */}
      </LineChart>
    </ResponsiveContainer>
  </div>
  </div>
)}

{history.length > 0 && (
<div className="glass-card p-6">

  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-3">Network Traffic (Live)</h3>

<p className="text-xs text-gray-400">
  Last updated: {new Date().toLocaleTimeString()}
</p>

    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={history}>
        <XAxis dataKey="time" />
        <YAxis 
  width={60}
  tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} 
/>
        <Tooltip />
        <Line
  type="monotone"
  dataKey="rx"
  stroke="#8b5cf6"
  strokeWidth={2}
  animationDuration={500}
/>       
       <Line
  type="monotone"
  dataKey="tx"
  stroke="#ec4899"
  strokeWidth={2}
  animationDuration={500}
/>
        {/* <Line type="monotone" dataKey="rx" stroke="#8b5cf6" strokeWidth={2} /> */}
        {/* <Line type="monotone" dataKey="tx" stroke="#ec4899" strokeWidth={2} /> */}
      </LineChart>
    </ResponsiveContainer>
  </div>


</div>
)}

{mlData && (
  <div className="glass-card p-6">
    <h2 className="text-lg font-bold mb-4">🧠 ML Insights</h2>

    <div className="grid md:grid-cols-3 gap-6">
   

  {/* 🔥 HEALTH SCORE */}
{/* 🔥 HEALTH SCORE */}
<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold mb-2">
    Health Score
  </h3>

<div
  className={`text-3xl font-bold ${
    mlData?.healthScore < 40
  ? 'text-red-500'
  : mlData?.healthScore < 70
  ? 'text-yellow-500'
  : 'text-green-500'
  }`}
>
  {typeof mlData?.healthScore === 'number'
    ? mlData.healthScore.toFixed(2)
    : "N/A"}
</div>

  <p className="text-sm mt-1 text-gray-500">
    Status: {
  mlData?.healthScore < 40
    ? "Critical"
    : mlData?.healthScore < 70
    ? "Warning"
    : "Healthy"
}
  </p>

</div>

 {/* 🔥 ANOMALY CARD */}
{/* 🔥 ANOMALY CARD */}
<div
  className={`p-4 rounded-xl ${
    mlData?.anomaly
      ? 'bg-red-100 border border-red-400'
      : 'bg-green-100 border border-green-400'
  }`}
>
  <h3 className="font-semibold">
    Anomaly Status
  </h3>

  <p
    className={`text-sm mt-2 ${
      mlData?.anomaly
        ? 'text-red-600 font-semibold'
        : 'text-green-600'
    }`}
  >
    {mlData?.anomaly
      ? '⚠️ Anomaly detected'
      : '✅ System is stable'}
  </p>
</div>


{/* 🔥 FAILURE PREDICTION */}
{/* 🔥 FAILURE PREDICTION */}
<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold">
    Failure Prediction
  </h3>

  <p
    className={`text-sm mt-2 ${
      mlData?.failureProbability > 70
  ? 'text-red-500 font-semibold'
  : mlData?.failureProbability > 40
  ? 'text-yellow-500 font-semibold'
  : 'text-green-500'
    }`}
  >
    {mlData?.failureProbability !== undefined
      ? `Failure Risk: ${mlData.failureProbability.toFixed(1)}%`
      : 'N/A'}
  </p>

</div>
<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold mb-4">
    CPU Forecast
  </h3>

  {mlData?.cpuPrediction?.predictions?.length  > 0 ? (

    <ResponsiveContainer width="100%" height={200}>

      <LineChart
        data={formatPredictionData(
          mlData.cpuPrediction.predictions
        )}
      >

        <XAxis dataKey="time" />

        <YAxis />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="cpu"
          stroke="#3b82f6"
          strokeWidth={3}
        />

      </LineChart>

    </ResponsiveContainer>

  ) : (

    <p className="text-gray-500">
      No CPU prediction available
    </p>

  )}

</div>

<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold mb-4">
    Memory Forecast
  </h3>

  {mlData?.memoryPrediction?.predictions?.length  > 0 ? (

    <ResponsiveContainer width="100%" height={200}>

      <LineChart
        data={formatMemoryData(
          mlData.memoryPrediction.predictions
        )}
      >

        <XAxis dataKey="time" />

        <YAxis />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="memory"
          stroke="#8b5cf6"
          strokeWidth={3}
        />

      </LineChart>

    </ResponsiveContainer>

  ) : (

    <p className="text-gray-500">
      No memory prediction available
    </p>

  )}

</div>


<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold mb-2">
    Auto Scaling Recommendation
  </h3>

  <p className="text-blue-500 font-semibold text-lg">
    {mlData?.autoscaleRecommendation ||
      "No recommendation"}
  </p>

  <p className="text-sm text-gray-500 mt-2">
    AI infrastructure optimization
  </p>

</div>

<div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-md">

  <h3 className="font-semibold mb-2">
    Root Cause Analysis
  </h3>

  <p className="text-lg font-bold text-orange-500">
    {mlData?.rootCause?.primary_cause?.cause ||
      "No issue detected"}
  </p>

  <p className="text-sm text-gray-500 mt-2">
    {mlData?.rootCause?.summary ||
      "System stable"}
  </p>

</div>




</div>
  

    </div>
 
)}
 
        </>
      )}
    </div>
  );
};

const MetricItem = ({ label, value, color = '' }) => (
  <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{label}</p>
    <p className={`text-lg font-bold text-gray-900 dark:text-white ${color}`}>{value || '—'}</p>
  </div>
);

const getColor = (value) => {
  if (value == null) return '';
  if (value >= 90) return 'text-red-500';
  if (value >= 70) return 'text-yellow-500';
  return 'text-green-500';
};

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  parts.push(`${mins}m`);
  return parts.join(' ');
};

export default MetricsPage;
