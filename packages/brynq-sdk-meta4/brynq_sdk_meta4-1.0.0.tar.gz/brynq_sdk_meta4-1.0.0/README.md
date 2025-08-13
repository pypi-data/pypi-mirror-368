## BrynQ Meta4 SDK

A lightweight toolkit to validate data and generate Meta4-ready CSV files. It validates Pandas DataFrames using Pydantic schemas and writes `.csv` files into the `outputs/` directory. Then upload the files via SFTP.

This SDK consists of two parts:
- CSV generation: validate and accumulate data in memory, then export to CSV files under `outputs/`.
- SFTP upload: send the generated CSV files to the target server directories.

### How it works

1. Instantiate the Meta4 client.
2. Use entity managers (Employees, CostCenters, Jobs) to call `create/update/delete` with DataFrames. Each call validates rows against the entity schema and appends valid rows to that entity’s in-memory `batch_df`. No file open/close happens per call; data is only accumulated.
3. When ready, call the entity’s `export()` to write all accumulated rows from its `batch_df` into a CSV under `outputs/`.
4. Call `meta4.upload()` (on the Meta4 client) to send the generated CSV files to the server over SFTP.

- Employee movement codes: `1=Create`, `2=Delete`, `3=Update`
- Cost center movement codes: `-36=Creation/Modification`, `-37=Deletion`
- Job movement codes: `-28=Creation`, `-29=Modification/Deletion`

Notes:
- Date fields expect the `DD/MM/YYYY` format. Schemas will auto-parse strings.
- DataFrame column names must match schema field names (e.g., `job_id`, `cost_center_id`, `employee_name`). Schemas output by aliases, but input can use field names.

### Design: batch_df per entity

Each entity manager (`employees`, `cost_centers`, `jobs`) maintains its own `batch_df` in memory. Calls to `create`, `update`, and `delete` only validate input data and append valid rows to the corresponding `batch_df`. This avoids repeated reads/writes and keeps I/O minimal. The actual file write happens only when you call the entity’s `export()` method, which flushes the accumulated rows into a CSV under `outputs/`.

### Installation

```bash
pip install -e .
```

Or activate your virtual environment and run the same command from the repository root.

### Quick start

```python
import pandas as pd
from brynq_sdk_meta4 import Meta4

meta4 = Meta4()  # writes to outputs/

# 1) Cost Centers
df_cc = pd.DataFrame([
    {"cost_center_id": "C200", "cost_center_name": "Centro de coste"},
])
meta4.cost_centers.create(df_cc)
meta4.cost_centers.export()  # outputs/cost_center_import.csv

# 2) Jobs
df_jobs = pd.DataFrame([
    {"job_id": "100", "job_name": "Puesto 1", "start_date": "01/01/2025", "end_date": "31/12/2025", "cno_subcode": "1120"},
])
meta4.jobs.create(df_jobs)
meta4.jobs.export()  # outputs/job_import.csv

# 3) Employees
df_emp = pd.DataFrame([
    {"effective_date": "06/03/2025", "person_id": "M88019", "employee_name": "Carlos", "document_type": "1", "document_number": "16719242J"}
])
meta4.employees.create(df_emp)
meta4.employees.export()  # outputs/employee_import.csv
```

### CRUD workflow examples

```python
# Jobs UPDATE/DELETE
df_update = pd.DataFrame([
    {"job_id": "100", "job_name": "Puesto 1 actualizado"}
])
meta4.jobs.update(df_update)

df_delete = pd.DataFrame([
    {"job_id": "100"}
])
meta4.jobs.delete(df_delete)

# Export (writes all accumulated valid rows)
meta4.jobs.export()
```

```python
# Cost Centers UPDATE/DELETE
df_cc_update = pd.DataFrame([
    {"cost_center_id": "C200", "cost_center_name": "Centro actualizado"}
])
meta4.cost_centers.update(df_cc_update)

df_cc_delete = pd.DataFrame([
    {"cost_center_id": "C200"}
])
meta4.cost_centers.delete(df_cc_delete)
meta4.cost_centers.export()
```

```python
# Employees UPDATE/DELETE
df_emp_update = pd.DataFrame([
    {"effective_date": "06/03/2025", "person_id": "M88077", "ss_number": "2000"}
])
meta4.employees.update(df_emp_update)

df_emp_delete = pd.DataFrame([
    {"effective_date": "06/03/2025", "termination_date": "08/03/2025", "termination_reason": "012", "unemployment_cause": "74", "person_id": "M88087"}
])
meta4.employees.delete(df_emp_delete)
meta4.employees.export()
```

### Outputs

- `outputs/employee_import.csv`
- `outputs/cost_center_import.csv`
- `outputs/job_import.csv`

### Running the tests

See `brynq_sdk_meta4/test_meta.py` for end-to-end examples (create/update/delete/export). Run directly:

```bash
python brynq_sdk_meta4/test_meta.py
```

### Upload via SFTP

The client can upload generated CSVs via SFTP. By default, `employee_import.csv` goes to `ENTRADA/EMPLEADOS`, and other files go to `SALIDA`.

```python
from brynq_sdk_meta4 import Meta4
meta4 = Meta4()

# After you have exported CSVs
meta4.upload()  # uploads to '/' + expected folders, then deletes uploaded CSVs locally

# Custom remote base path
meta4.upload(upload_path="/custom/path")
```

How it works:

- **Scan output directory**: Looks for all files ending with `.csv` under the local `outputs/` folder (or the custom `output_path` if you set it on the `Meta4` client).
- **Per-file routing**:
  - `employee_import.csv` is uploaded to `ENTRADA/EMPLEADOS` on the remote side.
  - All other CSVs are uploaded to `SALIDA`.
- **Remote path base**: The optional `upload_path` argument is prepended to the remote folders (e.g., `/custom/path/ENTRADA/EMPLEADOS/employee_import.csv`).
- **Upload behavior**: Each file is attempted independently. Failures are printed and skipped so the rest can continue.
- **Return value**: A string summarizing the successfully uploaded remote file paths.
- **Errors**: If no files are successfully uploaded, an exception is raised.

### Notes & tips

- Replace `NaN` values before validation if needed: `df.replace({pd.NA: None, pd.NaT: None})` (see examples).
- `export()` writes only the accumulated valid records from the internal `batch_df`. Use `get_batch_df()` to inspect and `clear_batch_df()` to reset when starting a new batch.
