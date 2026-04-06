# Ticket: YCCP-41
status: open
supplier_id: raj.mehta@diageo.com
loop_count: 0
created_at: 2026-04-06T06:32:53.481391+00:00

## Dispute
Hi, we are disputing invoice YCCP-41 for Captain Morgan Tiki Mango 700ml week 202612. Our records show 8 units sold, not 10. Please review and correct the invoice amount from £2.00 to £1.60.

## Analyst Findings
Perfect. Now I have all the data I need to analyze this dispute. Let me summarize my findings:

---

## Dispute Analysis: YCCP-41

### OUTCOME: **CORRECT**

The calculation is correct. The supplier's claim is unsupported by the data.

---

### EVIDENCE (from Database):

| Data Point | Value |
|---|---|
| **Actual Sales Volume (Week 202612)** | 10 units |
| **Agreed Funding Rate** | £0.20 per unit |
| **Calculated Total Funding** | 10 units × £0.20 = **£2.00** |
| **Supplier's Claimed Volume** | 8 units |
| **Supplier's Claimed Total** | 8 units × £0.20 = £1.60 |

---

### REASONING:

1. **Sales Data Verification**: The sales breakdown from week 202612 confirms **10 units** were sold for TPNB 87742417 (CAPTAIN MORGAN TIKI MANGO & P/APPLE 700ML) by supplier 60198. This is recorded in the sales table with confirmed sales value of £158.14 ex-VAT.

2. **Agreement Verification**: The promotion agreement (Ref: 98829437) confirms the agreed funding rate of **£0.20 per unit**, valid from 2026-03-11 to 2026-05-26.

3. **Calculation Accuracy**: 
   - 10 units × £0.20/unit = **£2.00** ex-VAT ✓
   - The calculation in YCCP-41 is mathematically correct.

4. **Data Consistency**: The calculation record shows:
   - `promo_sales_volume`: 10 units
   - `supplier_promotion_funding_per_unit`: £0.20
   - `total_supplier_promotion_funding_ex_vat`: £2.00
   - Final status: "READY FOR INVOICING"

**The supplier's claim of 8 units sold is not supported by the sales data in the system, which definitively shows 10 units sold in week 202612 for this product.**

## Supervisor Notes
DECISION: CORRECT CALCULATION - EXPLANATION SENT

Analyst confirmed the invoice calculation is accurate:
- Actual sales volume: 10 units (verified from system)
- Funding rate: £0.20 per unit (as per agreement Ref: 98829437)
- Total funding: £2.00 ex-VAT ✓

Supplier's claim of 8 units is unsupported by system data.

Professional explanation email sent to supplier at raj.mehta@diageo.com with full evidence breakdown. Status updated to explanation_sent.

## Thread
TICKET STATUS: explanation_sent

Email sent to supplier on: [system timestamp]
Subject: Re: Invoice YCCP-41 - Resolution of Volume Dispute
Recipient: raj.mehta@diageo.com

Action: Supplier notified that calculation is correct. Dispute resolved. Invoice amount stands at £2.00 ex-VAT.
