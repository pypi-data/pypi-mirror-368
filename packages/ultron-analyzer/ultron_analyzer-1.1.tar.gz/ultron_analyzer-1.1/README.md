# ULTRON

Ultron is a comprehensive Python tool for analyzing website performance, security, SEO, accessibility, and technical issues. Get instant insights and actionable recommendations to supercharge your website's performance and outrank the competition!

**Key Features:**
- ⚡ Lightning fast analysis - Complete site audit in under 30 seconds
- 📊 Professional Excel reports with 7 detailed sheets and color-coded insights
- 🔒 Security assessment - Validates critical security headers and vulnerabilities
- 📝 SEO analysis - Meta tags, headings, image alt text, and link optimization
- 🖼️ Image optimization - Size analysis, format suggestions, and compression tips
- 🔗 Broken link detection - Identifies and reports 404s and failed requests
- 📱 Mobile-friendly checks - Responsive design and viewport validation
- 💡 Performance boost guide - Step-by-step improvement recommendations
- 🎯 Rating system - Get scored from Beginner to Champion level
- 🤖 Both CLI and Python API - Use in terminal or integrate into your projects

![Ultron Logo](Assets/Logo.jpg)

## Installation

```bash
pip install ultron-analyzer
```

## Python Usage

```python
from ultron import UltronAnalyzer

# Initialize analyzer
analyzer = UltronAnalyzer()

# Analyze website
results = analyzer.run_comprehensive_check("https://example.com")

# Print results
analyzer.print_results(results)

# Generate Excel report
analyzer.save_report(results, 'excel')

# Get performance suggestions
suggestions = analyzer.generate_performance_suggestions(results)
analyzer.print_performance_suggestions(suggestions)
```

## CLI Usage

```
usage: ultron [-h] [--version] {analyze} ...

🤖 Ultron - Advanced Website Performance Analyzer

positional arguments:
  {analyze}   Available commands
    analyze   Analyze a website performance

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Examples:
  ultron analyze https://example.com
  ultron analyze https://example.com --format excel
  ultron analyze https://example.com --format all --timeout 60
  ultron --version

Report formats:
  json     - Technical data in JSON format
  html     - Web-friendly HTML report  
  excel    - Professional Excel report (requires openpyxl)
  all      - Generate all format types
  console  - Display results in terminal only
```

## Screenshots

### CLI Interface
![CLI Screenshot](Assets/CLI.png)

### Excel Reports
![Report 1](Assets/Report1.png)

![Report 2](Assets/Report2.png)

![Report 3](Assets/Report3.png)

![Report 4](Assets/Report4.png)

## About

**Om Pandey** - Software Developer who loves building awesome tools and applications.

📧 Email: iamompandey.it@gmail.com