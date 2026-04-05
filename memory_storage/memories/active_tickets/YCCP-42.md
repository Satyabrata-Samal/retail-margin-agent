# Ticket: YCCP-42
status: open
supplier_id: raj.mehta@diageo.com
loop_count: 0
created_at: 2026-04-05T07:35:35.887477+00:00

## Dispute
Hi, we are disputing invoice YCCP-42 for tpnb 87742417,you sent the invoive per unit funding is for 0.200 but we agreed for 0.16. Can you please check and confirm

## Analyst Findings
Perfect! I now have all the information I need. Let me analyze this dispute:

## DISPUTE ANALYSIS: YCCP-42

**OUTCOME: CORRECT**

---

**EVIDENCE:**

| Item | Value |
|------|-------|
| Calculation ID | YCCP-42 |
| Product (TPNB) | 87742417 (CAPTAIN MORGAN TIKI MANGO & P/APPLE 700ML) |
| Promotion Reference | 98829437 (Personalised Prices) |
| Funded Supplier | 60198 (DIAGEO GREAT BRITAIN) / Parent: 4958409 |
| Week | 202613 |
| **Agreed Funding Rate** | **£0.20 per unit** |
| **Supplier Claims** | **£0.16 per unit** |
| Sales Volume | 8 units |
| **Calculation: 8 × £0.20** | **£1.60** |
| Total Funding in Invoice | £1.60 |

**Key Data Point from Database:**
- Agreement record shows: `supplier_promotion_funding_per_unit: 0.2`
- This was sourced from BUYER (agreement_data_source: 'BUYER')
- Funding period: 2026-03-11 to 2026-05-26
- Promotion period: 2026-03-18 to 2026-03-24

---

**REASONING:**

The supplier is claiming the agreed rate was £0.16 per unit, but the database agreement record clearly shows the contracted rate is **£0.20 per unit**. The calculation in YCCP-42 correctly applies this rate:

- 8 units × £0.20/unit = £1.60 (exactly as invoiced)

The agreement was entered by the BUYER and has been properly recorded in our system. There is no discrepancy between the calculation and the agreed contract terms. The supplier's claim of £0.16 is not supported by any agreement record in the database.

**This invoice is correct as calculated.**

## Supervisor Notes
DISPUTE OUTCOME: CORRECT

Analyst confirmed calculation is accurate:
- Agreed rate: £0.20/unit (per BUYER agreement)
- Supplier claim: £0.16/unit
- Calculation: 8 units × £0.20 = £1.60 ✓

Professional explanation email sent to supplier on 2026-04-05 confirming correct invoice amount and offering to review if supplier can provide alternative agreement documentation.

Status: explanation_sent

## Thread
2026-04-05: Supervisor reviewed analyst findings (CORRECT outcome). Professional explanation email sent to raj.mehta@diageo.com confirming the invoice calculation is accurate per BUYER agreement records showing £0.20/unit funding rate. Dispute resolved.
