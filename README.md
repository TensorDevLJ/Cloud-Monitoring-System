
# Cloud Monitoring System

A production-grade, end-to-end cloud monitoring system for AWS EC2 instances, built with modern technologies and best practices.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.2+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)


## 🚀 Features


### Monitoring Capabilities
- ✅ **Real-time Metrics** - CPU, Memory, Disk, Network, and Load averages
- ✅ **Multi-instance support** - Monitor multiple EC2 instances simultaneously
- ✅ **Asynchronous Operations** - Non-blocking data collection and processing

### 🧠 Machine Learning & AI Features
- ✅ **Anomaly Detection** - Unsupervised ML to detect unusual metric patterns
- ✅ **Capacity Planning** - Predictive forecasting for resource exhaustion
- ✅ **Failure Prediction** - Proactive warnings before system failures occur
- ✅ **Root Cause Analysis** - Automated diagnosis of performance bottlenecks
- ✅ **Health Scoring** - Dynamic instance health calculation based on ML models

### Alerting & Notifications
- ✅ **Threshold-based alerts** - CPU, memory, disk usage thresholds
- ✅ **Email notifications** - Automated alert emails via SMTP
- ✅ **Alert management** - View, filter, and track alert history
- ✅ **Severity levels** - Warning and critical alert classifications
- ✅ **Alert Manager integration** - Advanced alerting with Prometheus Alertmanager

### Dashboard & Visualization
- ✅ **Modern web interface** - Responsive React dashboard
- ✅ **Real-time charts** - Live updating metrics visualization
- ✅ **Grafana integration** - Professional monitoring dashboards
- ✅ **Dark mode support** - Eye-friendly interface
- ✅ **Custom time ranges** - Historical data analysis

### Security & Authentication
- ✅ **JWT authentication** - Secure token-based auth
- ✅ **Role-based access** - Admin and user roles
- ✅ **Password hashing** - Bcrypt password encryption
- ✅ **CORS configuration** - Secure cross-origin requests

### DevOps & Deployment
- ✅ **Docker containers** - Fully containerized application
- ✅ **Docker Compose** - One-command deployment
- ✅ **Production ready** - Optimized for production use
- ✅ **Health checks** - Service health monitoring
- ✅ **Auto-restart** - Service failure recovery

## 📋 Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Monitoring Setup](#monitoring-setup)
- [Screenshots](#screenshots)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

```
┌─────────────────┐
│   EC2 Instance  │
│  Node Exporter  │  Port 9100
│   (metrics)     │
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │  Alertmanager   │
│  (collection)   │◄───┤   (alerts)      │
│   Port 9090     │    │   Port 9093     │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  FastAPI        │    │    Grafana      │
│  Backend API    │    │  (dashboards)   │
│   Port 8000     │    │   Port 3001     │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  React Frontend │
│   Dashboard     │
│   Port 3000     │
└─────────────────┘
```

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Bcrypt (passlib)
- **Database ODM**: Beanie (Motor)
- **Database**: MongoDB
- **Machine Learning**: Scikit-learn, NumPy, Pandas
- **Background Jobs**: APScheduler
- **API Client**: Requests, aiohttp
- **Monitoring Client**: Prometheus Python Client

### Frontend
- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **Routing**: React Router DOM 6.21
- **HTTP Client**: Axios 1.6
- **Charts**: Recharts 2.10
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React 0.303
- **Date Utilities**: date-fns 3.0

### Monitoring Stack
- **Metrics Collection**: Prometheus
- **Metrics Exporter**: Node Exporter
- **Visualization**: Grafana
- **Alerting**: Alertmanager

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Database**: MongoDB 6.0+
- **Web Server**: Nginx (production)

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Node.js** (20+) and **npm** (for local development)
- **Python** (3.11+) (for local development)
- **AWS EC2 instances** with Node Exporter installed

### EC2 Instance Setup

On each EC2 instance you want to monitor:

```bash
# Download Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz

# Extract
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz

# Move to /usr/local/bin
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter

# Verify
curl http://localhost:9100/metrics
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd cloud-monitoring-system

# Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Configure Prometheus targets
# Edit monitoring/prometheus/prometheus.yml
# Add your EC2 instance IPs

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file

# (No database migrations needed - MongoDB/Beanie handles schemas dynamically)

# Start server

uvicorn app.main:app --reload   
or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

## ⚙️ Configuration

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# Application
APP_NAME=Cloud Monitoring System
DEBUG=False

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=mongodb://localhost:27017/monitoring

# Prometheus
PROMETHEUS_URL=http://prometheus:9090

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@example.com

# Thresholds
CPU_THRESHOLD=80.0
MEMORY_THRESHOLD=85.0
DISK_THRESHOLD=90.0
```

### Prometheus Configuration

Edit `monitoring/prometheus/prometheus.yml` to add your EC2 instances:

```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - '10.0.1.100:9100'  # Your EC2 Instance 1
          - '10.0.1.101:9100'  # Your EC2 Instance 2
```

### Alertmanager Configuration

Edit `monitoring/alertmanager/config.yml` for email notifications:

```yaml
global:
  smtp_from: 'alerts@monitoring.com'
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
```

## 📚 API Documentation

### Authentication

**Register User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Metrics API

**Get All Metrics**
```http
GET /api/metrics/all/{instance_id}
Authorization: Bearer <token>
```

**Get CPU Metrics**
```http
GET /api/metrics/cpu/{instance_id}
Authorization: Bearer <token>
```

**Get Memory Metrics**
```http
GET /api/metrics/memory/{instance_id}
Authorization: Bearer <token>
```

**Dashboard Summary**
```http
GET /api/metrics/dashboard/summary
Authorization: Bearer <token>
```

### Instances API

**List Instances**
```http
GET /api/instances/
Authorization: Bearer <token>
```

**Add Instance**
```http
POST /api/instances/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Web Server 1",
  "instance_id": "i-1234567890abcdef0",
  "ip_address": "10.0.1.100",
  "port": 9100,
  "region": "us-east-1",
  "instance_type": "t3.medium"
}
```

**Get Instance Alerts**
```http
GET /api/instances/{instance_id}/alerts
Authorization: Bearer <token>
```

Full API documentation available at: `http://localhost:8000/api/docs`

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:

- AWS EC2 deployment
- Docker production setup
- Nginx configuration
- SSL/TLS setup
- Security best practices
- Monitoring production deployments

## 📊 Screenshots

### Dashboard
![Dashboard showing real-time metrics and alerts]

### Metrics View
![Detailed metrics with charts and graphs]

### Instance Management
![Instance configuration and management]

### Alerts
![Alert monitoring and notification history]

## 🔧 Troubleshooting

### Common Issues

**Issue: Cannot connect to Prometheus**
```bash
# Check if Prometheus is running
docker-compose ps prometheus

# Check Prometheus logs
docker-compose logs prometheus

# Verify Prometheus is accessible
curl http://localhost:9090/api/v1/status/config
```

**Issue: No metrics from EC2 instances**
```bash
# On EC2 instance, verify Node Exporter is running
sudo systemctl status node_exporter

# Check if metrics endpoint is accessible
curl http://localhost:9100/metrics

# Check security group allows port 9100
```

**Issue: Database connection errors**
```bash
# Check MongoDB is running
docker-compose ps mongodb

# Check database logs
docker-compose logs mongodb

# Verify connection string (mongodb://...) in .env file
```

**Issue: Frontend not loading**
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check frontend logs
docker-compose logs frontend

# Clear browser cache and reload
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Prometheus for metrics collection
- Grafana for visualization
- FastAPI for the excellent Python framework
- React team for the frontend framework
- All contributors and maintainers

## 📞 Support

For support, email likhithaj.dev@gmail .com or open an issue in the repository.

---

**Made with ❤️ by Likhithayaana**




