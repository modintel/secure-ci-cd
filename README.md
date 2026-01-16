# Phishing Detection

A machine learning-powered phishing detection system with a Chrome extension for real-time website analysis. Built using real-world data from the **PhiUSIIL Phishing URL Dataset (UCI Machine Learning Repository)**.


## Overview

This project provides an end-to-end solution for detecting phishing websites:
- A **Random Forest classifier** trained on 100,000+ real URLs
- A **Flask REST API** for URL predictions
- A **Chrome Extension** for automatic, real-time protection while browsing


## Features

### Machine Learning Model
- **Algorithm**: Random Forest Classifier (100 estimators)
- **Dataset**: PhiUSIIL Phishing URL Dataset from UCI
- **Validation**: 5-fold cross-validation with train/test split
- **Output**: Classification report, confusion matrix, and accuracy metrics


### Chrome Extension
- **Automatic Scanning**: Checks every page you visit
- **Visual Indicators**: Badge shows OK, DIE, or ERR 
- **Notifications**: Desktop alerts when phishing is detected
- **Warning Banner**: Injects a dismissible warning banner on phishing pages
- **Caching**: 24-hour cache to avoid redundant API calls
- **Whitelist**: Pre-configured list of trusted domains (Google, Facebook, Amazon, etc.)
- **Re-scan Button**: Manual rescan option in the popup

## Usage
1. Ensure the Flask API is running (`python src/api.py`)
2. Browse the web as normal
3. The extension automatically scans each page:
   - **Green "OK" badge**: Site appears legitimate
   - **Red "DIE" badge**: Phishing detected - a warning banner will appear
   - **Orange "..." badge**: Scan in progress
   - **Gray "ERR" badge**: Could not reach the API
4. Click the extension icon to see details and confidence score
5. Use the **Re-scan** button to manually recheck a page
