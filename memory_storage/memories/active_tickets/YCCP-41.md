# Ticket: YCCP-41
status: open
supplier_id: raj.mehta@diageo.com
loop_count: 0
created_at: 2026-04-05T07:46:45.149291+00:00

## Dispute
Hi, we are disputing invoice YCCP-41 for Captain Morgan Tiki Mango 700ml week 202612. Our records show 8 units sold, not 10. Please review and correct the invoice amount from £2.00 to £1.60.

## Analyst Findings
Perfect. Now I have all the data I need. Let me analyze the dispute:

## DISPUTE ANALYSIS: YCCP-41

### OUTCOME: **CORRECT**

### EVIDENCE:

From the database:
- **Product**: CAPTAIN MORGAN TIKI MANGO & P/APPLE 700ML (TPNB: 87742417)
- **Week**: 202612
- **Supplier**: DIAGEO GREAT BRITAIN (Supplier ID: 60198, Parent: 4958409)
- **Promotion**: Personalised Prices (Ref: 98829437)
- **Agreed Funding Rate**: £0.20 per unit
- **Actual Sales Volume (DB)**: 10 units
- **Calculation**: 10 units × £0.20/unit = **£2.00** ✓
- **Supplier Claims**: 8 units sold = £1.60

### REASONING:

The calculation in YCCP-41 is **CORRECT** and the supplier's claim is **WRONG**:

1. **Sales Data Verification**: The sales breakdown from our database shows 10 units were sold in week 202612, not 8 units as the supplier claims. Both the `sup_sales_volume` (10) and `tot_sales_volume` (10) fields confirm this.

2. **Funding Rate Confirmation**: The agreed promotion funding is £0.20 per unit (confirmed in the agreements table).

3. **Calculation Check**: 
   - Our calculation: 10 units × £0.20 = **£2.00** (as shown in `total_supplier_promotion_funding_ex_vat`)
   - Supplier's claim: 8 units × £0.20 = £1.60

4. **Data Source**: This is Tesco's own sales data, not supplier-submitted data, so it represents the actual point-of-sale volume recorded at checkout.

The invoice YCCP-41 should remain at **£2.00**. The supplier's records appear to be inaccurate.

## Supervisor Notes
DISPUTE RESOLUTION COMPLETED

Status: CORRECT - Invoice upheld at £2.00

Action Taken:
- Analyst confirmed calculation is correct (10 units × £0.20/unit = £2.00)
- Professional explanation email sent to supplier (raj.mehta@diageo.com)
- Supplier's claim of 8 units rejected; POS data confirms 10 units sold
- Supplier advised to review internal sales records for discrepancy

Ticket Status: explanation_sent

## Thread
[empty]
