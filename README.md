# Secure CI/CD Pipeline - Phishing Detection Extension

A phishing detection browser extension with Flask API backend, featuring a complete CI/CD pipeline with security analysis -- SAST + DAST.

## Project Overview

This project demonstrates a secure CI/CD pipeline implementation with:
- **Static Application Security Testing (SAST)** using Semgrep
- **Dynamic Application Security Testing (DAST)** using OWASP ZAP
- **Automated vulnerability detection and reporting**

##  Project Structure

```
secure-ci-cd/
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline configuration
├── .zap/
│   └── rules.tsv            # ZAP scanning rules
├── src/
│   ├── api.py               # Flask API with ML model
│   ├── feature_extraction.py # URL feature extraction
│   └── train.py             # Model training script
├── extension/
│   ├── manifest.json        # Chrome extension manifest
│   ├── background.js        # Background service worker
│   ├── popup.html/js        # Extension popup UI
│   └── content.js           # Content script
├── tests/
│   └── test_api.py          # Unit tests
└── requirements.txt         # Python dependencies
```

## CI/CD Pipeline Stages

The pipeline runs on every push and pull request:

| Stage | Tool | Purpose |
|-------|------|---------|
| **Build & Test** | pytest | Run unit tests |
| **Static Analysis** | Semgrep | SAST - Find vulnerabilities in source code |
| **Dynamic Analysis** | OWASP ZAP | DAST - Test running application |
| **Security Summary** | Custom | Aggregate security reports |

## Quick Start

### Run the API locally

```bash
cd src
pip install -r ../requirements.txt
python train.py   # Train the ML model first
python api.py     # Start the API server
```

### Run tests locally

```bash
pip install pytest
pytest tests/ -v
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Predict if URL is phishing |
| `/health` | GET | Health check |
| `/reload` | POST | Reload the ML model |

## Security Analysis

This project intentionally includes security vulnerabilities for educational purposes to demonstrate:

1. How SAST tools detect code-level vulnerabilities
2. How DAST tools detect runtime vulnerabilities
3. The importance of security in CI/CD pipelines

</br>

> ⚠️ **Warning**: This code contains intentional vulnerabilities for demonstration. Do not use in production!

## 📚 Assignment Information

**Course:** Software Security  
**Topic:** CI/CD Pipeline with Static & Dynamic Analysis  
**Tools:** GitHub Actions, Semgrep, OWASP ZAP

## Team

- Liyu Desta - UGR/4648/14
- Fozia Mohammed - UGR/4648/14
- Eyoab Amare - UGR/4648/14
- Meaza Tadele - UGR/4648/14
- Natanim Kemal - UGR/4648/14


## 📝 License

Educational use only.
