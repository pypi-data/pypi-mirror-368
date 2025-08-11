"""
Shared utils between web, cli and module applications.

Must not have any dependency other than stdlib, because sub modules (e.g. `config`) may be used (e.g. by `manage.py`) to update the dependency path.
"""
