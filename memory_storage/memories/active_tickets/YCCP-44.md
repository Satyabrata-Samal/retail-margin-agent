# Ticket: YCCP-44
status: open
supplier_id: tesco.invoices@colgate.com
loop_count: 0
created_at: 2026-04-06T06:58:20.879061+00:00

## Dispute
Hi, we are disputing invoice YCCP-44 for CCOLGATE TOTAL WHITENING TOOTHPASTE 125ML week 202612. From our calculation the total shoule be differnt. Please review and correct the invoice amount.

## Analyst Findings
Perfect. Now let me verify the calculation:

**ANALYSIS:**

**Calculation Details (YCCP-44):**
- Product: COLGATE TOTAL WHITENING TOOTHPASTE 125ML (TPNB: 52341876)
- Supplier: COLGATE-PALMOLIVE (UK) LIMITED (Supplier #63453)
- Week: 202612
- Promotion: Spring Clean Price Reduction (Ref: 98834521)
- Deal Status: Pending
- Final Check: READY FOR INVOICING

**Verification:**

1. **Sales Volume:** 50 units (matches promo_sales_volume in calculation)
2. **Funding Rate:** £0.20 per unit (confirmed in agreement)
3. **Calculation:** 50 units × £0.20/unit = **£10.00 total funding**
4. **Recorded Total:** £10.00 (matches calculation_id YCCP-44)

**Cross-check with sales data:**
- Supplier sales volume week 202612: 50 units ✓
- Supplier sales value (ex VAT): £85.00 ✓
- Promotion reference: 98834521 ✓

All calculation components are correct and verified against the database.

---

## OUTCOME: **CORRECT**

## EVIDENCE:
- **Promo Sales Volume:** 50 units
- **Funding Rate per Unit:** £0.20 (per agreement 98834521)
- **Total Funding Calculation:** 50 × £0.20 = **£10.00**
- **Recorded Invoice Amount:** £10.00
- **Sales Data Match:** Week 202612 shows 50 units sold by supplier 63453
- **Agreement Status:** Active (funding valid 11 Mar – 1 Apr 2026)

## REASONING:
The invoice calculation is mathematically correct. The promotion funding of £10.00 is properly calculated based on:
- The actual sales volume of 50 units in week 202612
- The agreed funding rate of £0.20 per promotional unit
- The promotion dates (offer 18–31 Mar, funding 11 Mar–1 Apr) which cover week 202612

The supplier's claim that "the total should be different" cannot be substantiated by the database. All underlying data (volume, rate, dates, product) validates the £10.00 invoice amount.

## Supervisor Notes
DECISION: CORRECT
- Analyst verified all calculation components
- Invoice amount £10.00 is accurate per agreement 98834521
- Sales volume (50 units) and funding rate (£0.20/unit) both validated
- Professional explanation email sent to supplier
- Status: explanation_sent
- No further action required

## Thread
[empty]
