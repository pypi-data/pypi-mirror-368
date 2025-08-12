# 📦 Data Import for Django

[![PyPI version](https://badge.fury.io/py/paquete-pypi.svg)](https://pypi.org/project/data_exchange_tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This package provides a **reusable Django library** for managing **data import processes** with features such as:

- Data preview before final import.
- Row-level error validation.
- Background processing with Celery.
- Import restrictions based on job state.
- Support for multiple content types.
- Integration with S3 or any storage backend via `django-storages`.

---

## 🚀 Installation

```bash
pip install django-data-exchange-tool
```

### Dependencies

- Python: 3.11
- Django: >= 3.0
- Celery: >= 5.0
- Redis (broker/result backend)
- S3 vía django-storages + boto3

---

## 🛠️ Usage

### 1️⃣ Django settings

This package supports uploading and storing import files on **Amazon S3** using `django-storages`.  
To enable this feature, define the following settings in your `settings.py`:

```python
# Required: S3 bucket name used for storing import files
MODEL_DATA_EXCHANGE_S3_BUCKET_NAME = "my-import-bucket"

# Optional: Base path (prefix) within the bucket
# Example: If set to "imports", files will be stored in "imports/<subfolder>/<file>"
MODEL_DATA_EXCHANGE_S3_BASE_PATH = "imports"

# Optional: Specify other celery queues for Preview task and Import task. 
# Value `data_exchange_shared_queue` by default
DATA_EXCHANGE_PREVIEW_QUEUE = "preview_queue"
DATA_EXCHANGE_IMPORT_QUEUE = "import_queue"
```


### 2️⃣ Create an Import Job
All import operations are managed entirely via the **Django Admin interface**:
- Navigate to the **Import Jobs** section in Django Admin.
- Upload your data file (CSV, XLSX, etc.).
- Select the target content type you want to import.

---

### 3️⃣ Preview Data
- After saving, the system automatically generates a **data preview**.
- This allows you to check for validation errors before proceeding.

---

### 4️⃣ Confirm Import
- In the job detail view, click **Confirm Import**.
- The system ensures:
  - No other job of the same content type is currently in progress.
  - The current job state is allowed for confirmation.
  - There are no preview errors blocking the process.

---

## 🔌 Extending the Library

This package is designed to be extendable.  
To create a custom importer for a specific model:

### 1️⃣ Create a proxy model

```python
from data_exchange_tool.models import ImportJob
from models import StockRecord
from myapp.serializers import ImportStockRecordSerializer


class StockRecordImportJob(ImportJob):
    class Meta:
        proxy = True
        target_model = StockRecord
        serializer_class = (
            "my_apps.data_exchange_tool.partner.serializers.ImportStockRecordSerializer"
        )
```

### 2️⃣ Create a custom admin

```python
from data_exchange_tool.admin import GenericImporterModelAdmin

class StockRecordNewImporterAdmin(GenericImporterModelAdmin):
    ...
```

This allows you to:

- Define **custom serializers** for validating and transforming data.
- Use **proxy models** to target specific Django models.
- Leverage the built-in admin UI for job management.

---

## 📊 Import Job Flow Diagram

```text
    ┌─────────┐        ┌───────────────────┐        ┌────────────────────┐          ┌──────────────────┐
    │ CREATED │ ─────▶ │ PREVIEW_SUCCEEDED │ ─────▶ │ IMPORT_IN_PROGRESS │ ─────▶   │ IMPORT_SUCCEEDED │        
    └─────────┘        └───────────────────┘        └────────────────────┘          └──────────────────┘     
         │                       │                                                            │
         ▼                       ▼                                                            ▼
 ┌────────────────┐     ┌────────────────┐                                          ┌──────────────────┐
 │ PREVIEW_FAILED │     │ PREVIEW_FAILED │                                          │   IMPORT_FAILED  │
 └────────────────┘     └────────────────┘                                          └──────────────────┘
```
---
