## Business Context

Tesco runs promotional agreements with suppliers. A supplier (e.g. Diageo) agrees to fund a discount
on their products during a promotion window. Tesco sells the products, records the sales, then
charges the supplier back for the agreed funding — this is the invoice the supplier may dispute.

### Grain of the Calculation
Every row in the calculation table is at the grain of:
```
year_week_number + funded_supplier_number + promotion_reference_number + tpnb
```
One row = one product (tpnb), one supplier, one promotion, one week.

### Key Business Rule — Parent / Subsidiary Suppliers
A supplier selling at Tesco may be a **subsidiary** of a larger parent.
Example: `DIAGEO GREAT BRITAIN` (sales supplier) is a subsidiary of
`DIAGEO GREAT BRITAIN LIMITED` (parent supplier, who actually gets invoiced).

The `Main_subsidiary_Alternate_Supplier` column controls this:
- `Main` — sales supplier = funded supplier, invoice goes directly to them
- `Subsidiary` — sales supplier is a child; invoice goes to `nominated_parent_supplier_number`
- `Alternate` — a third-party supplier arrangement

This is the most common source of disputes. Supplier says "this isn't our invoice" —
it's often a parent/subsidiary mismatch.