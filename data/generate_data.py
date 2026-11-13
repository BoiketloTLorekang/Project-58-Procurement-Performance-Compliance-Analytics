import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(58)

print('Initializing Project 58 Procurement Dataset Generation...')

# ----------------------------------------------------
# 1. DIMENSION: Categories
# ----------------------------------------------------
categories_data = [
    {
        'CategoryID': 'CAT-01',
        'MajorGroup': 'IT Hardware & Software',
        'SubCategory': 'Enterprise Servers & Licensing',
    },
    {
        'CategoryID': 'CAT-02',
        'MajorGroup': 'IT Hardware & Software',
        'SubCategory': 'End-User Computing (Laptops/Peripherals)',
    },
    {
        'CategoryID': 'CAT-03',
        'MajorGroup': 'Facilities & Infrastructure',
        'SubCategory': 'HVAC & Facility Maintenance',
    },
    {
        'CategoryID': 'CAT-04',
        'MajorGroup': 'Facilities & Infrastructure',
        'SubCategory': 'Office Supplies & Furniture',
    },
    {
        'CategoryID': 'CAT-05',
        'MajorGroup': 'Professional Services',
        'SubCategory': 'Management & Financial Consulting',
    },
    {
        'CategoryID': 'CAT-06',
        'MajorGroup': 'Professional Services',
        'SubCategory': 'Legal & Compliance Auditing',
    },
    {
        'CategoryID': 'CAT-07',
        'MajorGroup': 'Logistics & Fleet',
        'SubCategory': 'Freight & Courier Services',
    },
    {
        'CategoryID': 'CAT-08',
        'MajorGroup': 'Logistics & Fleet',
        'SubCategory': 'Fleet Fuel & Maintenance',
    },
]
df_categories = pd.DataFrame(categories_data)

# ----------------------------------------------------
# 2. DIMENSION: Departments
# ----------------------------------------------------
departments_data = [
    {
        'DepartmentID': 'DEPT-101',
        'BusinessUnit': 'Information Technology',
        'CostCenter': 'CC-IT-901',
    },
    {
        'BusinessUnit': 'Finance & Procurement',
        'DepartmentID': 'DEPT-102',
        'CostCenter': 'CC-FIN-402',
    },
    {
        'BusinessUnit': 'Operations & Logistics',
        'DepartmentID': 'DEPT-103',
        'CostCenter': 'CC-OPS-305',
    },
    {
        'BusinessUnit': 'Facilities Management',
        'DepartmentID': 'DEPT-104',
        'CostCenter': 'CC-FAC-201',
    },
    {
        'BusinessUnit': 'Legal & Governance',
        'DepartmentID': 'DEPT-105',
        'CostCenter': 'CC-LEG-104',
    },
]
df_departments = pd.DataFrame(departments_data)

# ----------------------------------------------------
# 3. DIMENSION: Suppliers
# ----------------------------------------------------
n_suppliers = 20
supplier_names = [
    'Apex Systems Ltd',
    'BlueWave Technologies',
    'Zenith Office Solutions',
    'Vanguard Facility Maintenance',
    'Meridian Global Freight',
    'Solomon & Harris Legal',
    'Alpha Prime Consulting',
    'OmniFleet Services',
    'Nexus Hardware Hub',
    'Delta Clean & Maintenance',
    'Pioneer Business Advisory',
    'RapidTransit Couriers',
    'SecureCloud Networks',
    'Titanium Fuel Corp',
    'Metro Stationers',
    'Epsilon Strategy Group',
    'Summit Building Works',
    'Veritas Audit Partners',
    'Kalahari Logistics',
    'InfiniTech Solutions',
]

regions = ['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape']
risk_ratings = ['Low', 'Medium', 'High']

suppliers_data = []
for i in range(1, n_suppliers + 1):
  sup_id = f'SUP-{i:03d}'
  name = supplier_names[i - 1]
  # Assign category associations
  cat_id = np.random.choice(df_categories['CategoryID'])
  region = np.random.choice(regions, p=[0.4, 0.3, 0.2, 0.1])
  risk = np.random.choice(risk_ratings, p=[0.65, 0.25, 0.10])
  is_contracted = np.random.choice([True, False], p=[0.8, 0.2])

  suppliers_data.append({
      'SupplierID': sup_id,
      'SupplierName': name,
      'PrimaryCategoryID': cat_id,
      'Region': region,
      'RiskRating': risk,
      'IsContracted': is_contracted,
  })

df_suppliers = pd.DataFrame(suppliers_data)

# ----------------------------------------------------
# 4. FACT: Requisitions (1,500 rows)
# ----------------------------------------------------
n_requisitions = 1500
start_date = pd.to_datetime('2025-01-01')
end_date = pd.to_datetime('2025-12-31')

req_dates = pd.to_datetime(
    np.random.choice(
        pd.date_range(start_date, end_date), size=n_requisitions
    )
)
# Convert to a Series so we can sort and reset the index
req_dates = pd.Series(req_dates).sort_values().reset_index(drop=True)

requisitions_data = []
for i in range(1, n_requisitions + 1):
  req_id = f'REQ-{i:05d}'
  r_date = req_dates[i - 1]

  # Approval lag: 1 to 10 days
  approval_lag = np.random.randint(1, 11)
  approval_date = r_date + pd.Timedelta(days=int(approval_lag))

  dept_id = np.random.choice(df_departments['DepartmentID'])
  cat_id = np.random.choice(df_categories['CategoryID'])

  # Estimated values skewed towards lower values
  est_value = round(float(np.random.exponential(scale=15000) + 1200), 2)

  status = np.random.choice(
      ['Approved', 'Rejected', 'Pending'], p=[0.85, 0.10, 0.05]
  )
  if status != 'Approved':
    approval_date = pd.NaT

  requisitions_data.append({
      'RequisitionID': req_id,
      'RequisitionDate': r_date.strftime('%Y-%m-%d'),
      'ApprovalDate': (
          approval_date.strftime('%Y-%m-%d')
          if pd.notnull(approval_date)
          else ''
      ),
      'DepartmentID': dept_id,
      'CategoryID': cat_id,
      'EstimatedValue': est_value,
      'Status': status,
  })

df_requisitions = pd.DataFrame(requisitions_data)

# Filter only approved requisitions for PO generation
df_approved_reqs = df_requisitions[
    df_requisitions['Status'] == 'Approved'
].copy()

# ----------------------------------------------------
# 5. FACT: Purchase Orders (Linked to Approved Requisitions)
# ----------------------------------------------------
po_data = []
po_counter = 1

for _, row in df_approved_reqs.iterrows():
  req_id = row['RequisitionID']
  approval_date = pd.to_datetime(row['ApprovalDate'])
  cat_id = row['CategoryID']

  # Select supplier matching category or random
  matching_sups = df_suppliers[df_suppliers['PrimaryCategoryID'] == cat_id][
      'SupplierID'
  ].tolist()
  if not matching_sups:
    matching_sups = df_suppliers['SupplierID'].tolist()
  sup_id = np.random.choice(matching_sups)

  # PO Issue lag: 1 to 5 days after requisition approval
  issue_lag = np.random.randint(1, 6)
  issue_date = approval_date + pd.Timedelta(days=int(issue_lag))

  # Contract compliance link (if supplier is contracted, 90% chance PO references contract)
  sup_info = df_suppliers[df_suppliers['SupplierID'] == sup_id].iloc[0]
  is_under_contract = sup_info['IsContracted'] and np.random.rand() < 0.92
  contract_id = f'MSA-2025-{np.random.randint(100, 500)}' if is_under_contract else 'SPOT-BUY'

  # Actual PO Value close to estimated value (+/- 10%)
  variance_factor = np.random.uniform(0.92, 1.08)
  po_value = round(float(row['EstimatedValue'] * variance_factor), 2)

  # Agreed delivery term (days)
  lead_time_days = np.random.choice([7, 14, 21, 30, 45], p=[0.2, 0.4, 0.2, 0.15, 0.05])
  agreed_delivery_date = issue_date + pd.Timedelta(days=int(lead_time_days))

  po_id = f'PO-{po_counter:05d}'
  po_counter += 1

  po_data.append({
      'PurchaseOrderID': po_id,
      'RequisitionID': req_id,
      'SupplierID': sup_id,
      'IssueDate': issue_date.strftime('%Y-%m-%d'),
      'AgreedDeliveryDate': agreed_delivery_date.strftime('%Y-%m-%d'),
      'POValue': po_value,
      'ContractID': contract_id,
  })

df_pos = pd.DataFrame(po_data)

# ----------------------------------------------------
# 6. FACT: Goods Receipts & Delivery Performance
# ----------------------------------------------------
receipts_data = []

for _, row in df_pos.iterrows():
  po_id = row['PurchaseOrderID']
  agreed_date = pd.to_datetime(row['AgreedDeliveryDate'])
  po_value = row['POValue']

  # Delivery variance: normal distribution centered around 0 days (on-time), with some late deliveries
  delivery_variance_days = int(np.random.normal(loc=1.5, scale=4.0))
  actual_delivery_date = agreed_date + pd.Timedelta(days=delivery_variance_days)

  # Ensure delivery is not before issue date
  issue_dt = pd.to_datetime(row['IssueDate'])
  if actual_delivery_date < issue_dt:
    actual_delivery_date = issue_dt + pd.Timedelta(days=2)

  # Quality acceptance status
  quality_status = np.random.choice(
      ['Accepted', 'Accepted with Deviations', 'Rejected'], p=[0.88, 0.09, 0.03]
  )

  receipt_id = po_id.replace('PO-', 'REC-')

  receipts_data.append({
      'ReceiptID': receipt_id,
      'PurchaseOrderID': po_id,
      'ActualDeliveryDate': actual_delivery_date.strftime('%Y-%m-%d'),
      'DaysVariance': (actual_delivery_date - agreed_date).days,
      'QualityStatus': quality_status,
      'InvoicedAmount': po_value,
  })

df_receipts = pd.DataFrame(receipts_data)

# Export tables to CSV
df_categories.to_csv('Dim_Categories.csv', index=False)
df_departments.to_csv('Dim_Departments.csv', index=False)
df_suppliers.to_csv('Dim_Suppliers.csv', index=False)
df_requisitions.to_csv('Fact_Requisitions.csv', index=False)
df_pos.to_csv('Fact_Purchase_Orders.csv', index=False)
df_receipts.to_csv('Fact_Receipts.csv', index=False)

print('Successfully generated all Project 58 Procurement tables:')
print(f' - Dim_Categories.csv ({len(df_categories)} rows)')
print(f' - Dim_Departments.csv ({len(df_departments)} rows)')
print(f' - Dim_Suppliers.csv ({len(df_suppliers)} rows)')
print(f' - Fact_Requisitions.csv ({len(df_requisitions)} rows)')
print(f' - Fact_Purchase_Orders.csv ({len(df_pos)} rows)')
print(f' - Fact_Receipts.csv ({len(df_receipts)} rows)')