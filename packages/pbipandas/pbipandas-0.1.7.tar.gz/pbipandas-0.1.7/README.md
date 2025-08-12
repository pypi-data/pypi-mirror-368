# pbipandas
![CI](https://github.com/hoangdinh2710/pbipandas/actions/workflows/ci.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/pbipandas.svg)](https://pypi.org/project/pbipandas/)


**pbipandas** is a lightweight Python client for the [Power BI REST API](https://learn.microsoft.com/en-us/rest/api/power-bi/) that helps you authenticate and retrieve data directly into **Pandas DataFrames**. This package helps to get metadata details for all items (including datasets, dataflows, reports, refresh logs, datasources) in all of your workspaces.

---

## 🚀 Features

- 🗂️ Get metadata for all items in all workspaces
- 🔐 Easy OAuth2 authentication using client credentials
- 📊 Seamless integration with Pandas for data analysis
- ⚡ Simplifies working with Power BI API endpoints

---

## 📦 Installation

```bash
pip install pbipandas
```

Or for development:

```bash
git clone https://github.com/hoangdinh2710/pbipandas.git
cd pbipandas
pip install -e .
```

---

## 🔧 Usage

```python
from pbipandas import PowerBIClient

pbi_client = PowerBIClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Example: 
1. get_all_dataset
dataset_df = pbi_client.get_all_datasets()
2. Get all dataset history logs
dataset_df = pbi_client.get_all_dataset_refresh_history()
3. Get all dataset sources
dataset_sources_Df = pbi_client.get_all_dataset_sources()

```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🧹 Lint and Format Code

```bash
flake8 .
black .
```

---

## 📄 License

[MIT License](LICENSE)

---

## 🙌 Contributing

Pull requests are welcome! Please open an issue first to discuss what you would like to change.

---

## ✨ Reference

- [Power BI REST API Docs](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [pandas Documentation](https://pandas.pydata.org/)
