<div align="center">

# AI Asset Recognition

### Enterprise AI Pipeline for OCR, Barcode Intelligence & Confidence-Based Asset Recognition

**Computer Vision • OCR • Barcode Recognition • Validation • Confidence Scoring • Structured AI Extraction**

[![Python Tests](https://github.com/shrenik355/AI-Asset-Recognition-Portfolio/actions/workflows/python-tests.yml/badge.svg)](https://github.com/shrenik355/AI-Asset-Recognition-Portfolio/actions/workflows/python-tests.yml)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Multi--Page-FF4B4B?logo=streamlit\&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-40%20Passing-45d483)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Style-blue)

**Transform a photo of an asset label into structured, validated, confidence-scored data using an explainable AI pipeline.**

---

### 🚀 Features

OCR • Barcode Detection • IMEI Validation • Confidence Intelligence • JSON Export • CSV Export • Benchmarking • Interactive Dashboard

</div>

---

# Overview

AI Asset Recognition is an end-to-end AI-powered asset recognition platform that automates the extraction and validation of information from electronic device labels.

The system combines optical character recognition (OCR), barcode decoding, rule-based validation, and an explainable confidence engine to produce structured asset information while clearly explaining how every confidence score is calculated.

Unlike traditional OCR applications, this project focuses not only on extracting data but also on determining how trustworthy that data is.

---

# Why This Project?

Manual inventory processing remains slow, inconsistent, and difficult to scale.

This project demonstrates how AI-assisted automation can:

* Reduce manual data entry
* Improve extraction accuracy
* Validate critical identifiers
* Prioritize records requiring human review
* Produce structured data ready for downstream systems

---

# Key Features

## Computer Vision

* OCR using Tesseract
* OCR bounding box visualization
* Image preprocessing
* Multi-image support (roadmap)

## Barcode Intelligence

* UPC-A validation
* EAN-13 validation
* Barcode checksum verification
* Barcode confidence analysis

## Data Extraction

* Label-based extraction
* Pattern recognition
* Keyword fallback
* Structured JSON generation

## Validation Engine

* IMEI validation (Luhn Algorithm)
* Barcode checksum validation
* Field verification
* Validation status indicators

## Explainable Confidence Engine

Instead of returning a simple confidence percentage, the application explains exactly how confidence is calculated.

Confidence is derived from multiple weighted signals including:

* OCR quality
* Barcode reliability
* Identifier validation
* Field completeness
* Extraction consistency

Each result includes:

* Overall confidence score
* Component breakdown
* Explanation cards
* Review recommendation

---

# Dashboard

The Streamlit application includes multiple pages designed to simulate a production AI platform.

* Dashboard
* Architecture
* Benchmarks
* Documentation
* API
* About

---

# Example Output

```json
{
  "asset_type": "smartphone",
  "brand": "Apple",
  "model": "iPhone 13",
  "serial_number": "SN-PH-774120",
  "imei": "490154203237518",
  "barcode": "012345678905",
  "confidence_score": 0.90,
  "review_recommendation": "Auto-review eligible"
}
```

---

# Technology Stack

| Category        | Technology     |
| --------------- | -------------- |
| Language        | Python 3.10+   |
| OCR             | Tesseract      |
| Barcode         | pyzbar         |
| Imaging         | Pillow         |
| Dashboard       | Streamlit      |
| Data Processing | pandas         |
| Testing         | pytest         |
| CI/CD           | GitHub Actions |

---

# Quick Start

Clone the repository

```bash
git clone https://github.com/shrenik355/AI-Asset-Recognition-Portfolio.git
cd AI-Asset-Recognition-Portfolio
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app/streamlit_app.py
```

Run tests

```bash
pytest tests -v
```

Run benchmarks

```bash
python benchmark/run_benchmark.py
```

---

# Project Structure

```text
AI-Asset-Recognition-Portfolio
│
├── app
├── src
├── tests
├── docs
├── benchmark
├── data
├── .github
└── requirements.txt
```

---

# Engineering Highlights

* Modular pipeline architecture
* Explainable confidence scoring
* Typed Python modules
* Multi-page dashboard
* Unit testing
* GitHub Actions CI
* Benchmark framework
* Documentation-first development

---

# Roadmap

* Image enhancement pipeline
* QR and Code-128 support
* REST API
* Docker deployment
* Batch processing
* Confidence calibration using labeled datasets
* Machine learning-assisted extraction
* Cloud deployment

---

# Disclaimer

This repository is an independent portfolio project created using original code and publicly available sample data.

It contains **no proprietary employer code, confidential business logic, or client information**.

---

# License

Released under the MIT License.
