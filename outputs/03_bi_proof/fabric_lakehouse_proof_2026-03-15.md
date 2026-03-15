# Microsoft Fabric Lakehouse Proof

**Date:** 2026-03-15  
**Status:** ✅ Verified

## Lakehouse Created

**Lakehouse ID:** `28903c65-fb33-4a32-96ec-73898f26b13f`  
**Name:** HealthcareAnalytics  
**Workspace:** 577de43f-21b4-479e-99b6-ea78f32e5216

## Table Loaded

**Table:** `healthcare_encounters`  
**Format:** Delta (managed)  
**Location:** `abfss://577de43f-21b4-479e-99b6-ea78f32e5216@onelake.dfs.fabric.microsoft.com/28903c65-fb33-4a32-96ec-73898f26b13f/Tables/healthcare_encounters`  
**Source:** 1,000 healthcare encounter records (sample from 55,500 total)

## Columns

- Name
- Age
- Gender
- Blood_Type
- Medical_Condition
- Date_of_Admission
- Doctor
- Hospital
- Insurance_Provider
- Billing_Amount
- Room_Number
- Admission_Type
- Discharge_Date
- Medication
- Test_Results

## API Operations Used

1. **Create Lakehouse:** `POST /v1/workspaces/{workspaceId}/lakehouses`
2. **Upload to OneLake:** ADLS Gen2 API (create, append, flush)
3. **Load Table:** `POST /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}/tables/{tableName}/load`
4. **List Tables:** `GET /v1/workspaces/{workspaceId}/lakehouses/{lakehouseId}/tables`

## Authentication

Service Principal (Azure AD app) with:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`

## Verification

```bash
# List tables
curl -X GET "https://api.fabric.microsoft.com/v1/workspaces/${FABRIC_WORKSPACE_ID}/lakehouses/${LAKEHOUSE_ID}/tables" \
  -H "Authorization: Bearer $TOKEN"
```

**Result:** Table `healthcare_encounters` confirmed in Lakehouse.
