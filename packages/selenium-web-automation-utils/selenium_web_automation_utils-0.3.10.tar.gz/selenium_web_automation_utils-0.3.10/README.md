# Selenium Web Automation Utils

A lightweight Python utility package for **web scraping and automation** using Selenium.

## 🚀 Features
- **Reusable Selenium Utilities**: Simplify automation tasks.
- **Web Scraping Helpers**: Easily interact with web elements.
- **Task Automation**: Automate logins, form submissions, and more.
- **Human-Like Interactions**: Simulate realistic browsing behavior.

## 📦 Installation
Install the package using pip:
```bash
pip install selenium-web-automation-utils
```

## 📖 Usage Example
```python
from selenium_web_automation_utils.selenium_utils import get_webdriver, find_element_wait

with get_webdriver() as driver:
    driver.get("https://example.com")
    element = find_element_wait(driver, "//h1")
    print(element.text)
```

## 🛠 Requirements
- Python 3.7+
- `selenium`
- `undetected-chormedriver`
- `colorlog`


## 📝 Contributing
1. Fork the repo
2. Create a branch
3. Commit your changes
4. Submit a PR

## 📜 License
MIT License

