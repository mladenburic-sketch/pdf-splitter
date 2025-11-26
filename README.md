# PDF Invoice Splitter

A web application for splitting PDF files containing multiple invoices into individual PDF files.

## Features

- Split a single PDF file with multiple invoices into separate files
- Web-based interface (Streamlit) - easy to use in browser
- Customizable invoice detection markers
- Support for regex patterns for advanced matching
- Download individual files or complete ZIP archive
- Command-line interface also available

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
python -m streamlit run app.py
```

3. Open your browser and upload a PDF file with multiple invoices

### Command Line Interface

```bash
python src/main.py input/your_file.pdf
```

## Project Structure

```
pdfSplitter/
├── src/              # Source code
├── input/            # Input PDF files
├── output/           # Output PDF files
├── tests/            # Tests
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```
