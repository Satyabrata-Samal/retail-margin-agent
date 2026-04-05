# Ticket: YCCP-41
status: open
supplier_id: raj.mehta@diageo.com
loop_count: 0
created_at: 2026-04-05T07:31:35.069064+00:00

## Dispute
Hi, we are disputing invoice YCCP-41 for Captain Morgan Tiki Mango 700ml week 202612. Our records show 8 units sold, not 10. Please review and correct the invoice amount from £2.00 to £1.60.

## Analyst Findings
Perfect! I now have all the key information. Let me analyze this dispute:

## DISPUTE ANALYSIS: YCCP-41

### 1. OUTCOME: **CORRECT**

---

### 2. EVIDENCE (from database):

| Field | Value |
|-------|-------|
| **Calculation ID** | YCCP-41 |
| **Product** | 87742417 - CAPTAIN MORGAN TIKI MANGO & P/APPLE 700ML |
| **Week** | 202612 |
| **Supplier** | 60198 (DIAGEO GREAT BRITAIN - subsidiary of 4958409) |
| **Promotion** | 98829437 (Personalised Prices) |
| **Agreed funding rate** | £0.20 per unit |
| **Actual sales volume (DB)** | **10 units** |
| **Supplier's claimed volume** | 8 units |
| **Invoice calculation (DB)** | 10 units × £0.20 = **£2.00** ✓ |
| **Supplier's proposed adjustment** | 8 units × £0.20 = £1.60 |

---

### 3. REASONING:

The supplier claims 8 units were sold, but the **database sales record clearly shows 10 units** were sold in week 202612:
- Sales volume in system: **sup_sales_volume = 10**
- Total sales volume: **tot_sales_volume = 10**
- Sales value: £158.14 (ex-VAT) for those 10 units

The calculation is **correct**:
- 10 units × £0.20/unit (agreed funding rate) = £2.00 ✓

**The supplier's records are inaccurate.** Their claim of 8 units sold does not match Tesco's point-of-sale data. The invoice amount of £2.00 is correctly calculated based on actual sales volumes.

The calculation status is "READY FOR INVOICING" and all checks have passed.

## Supervisor Notes
ANALYSIS COMPLETE - CALCULATION CONFIRMED AS CORRECT

Analyst verdict: CORRECT

Key findings:
- Tesco database records: 10 units sold (week 202612)
- Supplier claimed: 8 units sold
- Agreed funding rate: £0.20 per unit
- Correct invoice total: 10 × £0.20 = £2.00
- Supplier's proposed total: 8 × £0.20 = £1.60 (INCORRECT)

Action taken:
- Professional explanation email sent to supplier (raj.mehta@diageo.com)
- Email includes exact numbers, funding rate, and confirmed calculation
- Supplier advised that their records do not match Tesco POS data
- Invoice stands at £2.00 - no adjustment approved

Status: explanation_sent

## Thread
[2026-04-05 - Supervisor] CORRECT calculation confirmed. Explanation email sent to supplier at raj.mehta@diageo.com detailing:
- Actual sales volume: 10 units (not 8 as claimed)
- Correct invoice: £2.00 (not £1.60)
- Funding rate: £0.20 per unit (agreed)
- Invoice is valid and stands. Supplier records are inaccurate.
