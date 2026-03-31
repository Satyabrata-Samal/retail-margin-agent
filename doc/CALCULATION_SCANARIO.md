---

## Dispute Scenarios for Agent Testing

### Scenario 1 — Correct Calculation
Supplier disputes volume (says 8 units, Tesco has 10).
Agent queries `sales` table, confirms 10 units with sales data.
**Expected agent outcome:** Send explanation mail with sales breakdown.

```
funded_supplier: Diageo GB | promo_sales_volume: 10 | funding_per_unit: £0.20
total_funding: £2.00
supplier_claim: £1.60 (based on 8 units)
```

### Scenario 2 — Wrong Calculation (DB fix needed)
Agreement was entered with wrong `funding_per_unit` (£0.20 instead of agreed £0.25).
Supplier is correct to dispute.
**Expected agent outcome:** Flag to human. Human updates agreement, agent re-raises.

```
funded_supplier: Colgate | funding_per_unit in DB: £0.20
agreed rate in contract: £0.25
delta: £0.05 × volume = underpayment
```

### Scenario 3 — Parent / Subsidiary Mismatch
Invoice raised to parent (Diageo GB Limited) but email went to subsidiary (Diageo GB).
Subsidiary replies saying "this isn't our invoice."
**Expected agent outcome:** Identify `main_subsidiary_alternate = Subsidiary`,
explain that invoice correctly goes to parent per nomination rules.

```
sales_supplier: DIAGEO GREAT BRITAIN (subsidiary)
nominated_parent: DIAGEO GREAT BRITAIN LIMITED (invoiced party)
supplier_mismatch_check: flag if email contact doesn't match funded supplier
```

### Scenario 4 — Not Conclusive
Supplier disputes a promotion they say was cancelled, but `promotion_status = approved` in DB.
Agent cannot resolve — contract docs needed.
**Expected agent outcome:** Escalate to MD team with full analysis report.

---

## Common Dispute Reasons (BA Agent Knowledge Base)

| Dispute type | Root cause | Agent resolution |
|---|---|---|
| Volume mismatch | Supplier has different POS data | Query sales table, attach weekly breakdown |
| Rate mismatch | Agreement entered incorrectly | Flag wrong calc, human corrects agreement |
| Wrong supplier invoiced | Parent/subsidiary confusion | Explain nomination rule |
| Promo date out of range | Funding window ≠ promo window | Check funding_start/end vs offer_start/end |
| Duplicate invoice | Same calc_id raised twice | Check deal_dealref uniqueness |
| Cancelled promotion | Promotion status mismatch | Escalate — needs commercial check |

---

## Check Columns — What Each Means

| Column | Passes when |
|---|---|
| `funding_check` | `supplier_promotion_funding_per_unit > 0` |
| `funding_source_check` | `agreement_data_source` is not null |
| `promotion_source_check` | Promotion exists and is approved |
| `supplier_mismatch_check` | `funded_supplier` email matches `supplier_email_contact` |
| `sales_volume_check` | `sup_sales_volume > 0` |
| `missing_cost_center_check` | `cost_centre_code` is not null |
| `customer_details_check` | Buyer email populated |
| `calculation_check` | `total_supplier_promotion_funding_ex_vat` = `volume × rate` |
| `invoicing_check` | Deal raised and `deal_dealref` not null |
| `final_check` | All above pass → `READY FOR INVOICING` |

---

## Agent Query Patterns

Queries the Analyst Agent should know how to run:

```sql
-- 1. Pull full calculation row for a dispute
SELECT * FROM calculations WHERE calculation_id = :calc_id;

-- 2. Verify sales volume independently
SELECT sup_sales_volume, sup_sales_value_xvat
FROM sales
WHERE year_week_number = :week
  AND tpnb = :tpnb
  AND sales_supplier = :supplier;

-- 3. Check the agreement rate
SELECT supplier_promotion_funding_per_unit, funding_method,
       funding_start_date, funding_end_date
FROM agreements
WHERE promotion_reference_number = :promo_ref
  AND funded_supplier_number = :supplier;

-- 4. Resolve parent/subsidiary
SELECT supplier_number, supplier_name, supplier_type,
       parent_supplier_number, parent_supplier_name
FROM suppliers
WHERE supplier_number = :supplier;

-- 5. Check for duplicate deals
SELECT calculation_id, deal_dealref, deal_status
FROM calculations
WHERE funded_supplier_number = :supplier
  AND promotion_reference_number = :promo_ref
  AND year_week_number = :week;
```

---

## Seed Data Summary

Minimum seed to test all 4 scenarios:

| Entity | Records |
|---|---|
| suppliers | 5 (Diageo GB subsidiary, Diageo GB Ltd parent, Colgate main, Unilever main, one alternate) |
| products | 6 (2 per category: BWS, Household, Personal Care) |
| promotions | 4 (1 per scenario, all approved except scenario 4 edge case) |
| agreements | 4 (one with wrong rate for scenario 2) |
| sales | 8 (2 weeks of data, covering all promotions) |
| calculations | 4 (one per scenario, pre-loaded as Pending) |
