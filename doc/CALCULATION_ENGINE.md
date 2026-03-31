# Calculation Engine — Agent Reference Document

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

---

## Table Schema (Supabase / PostgreSQL)

### 1. `suppliers`
Master supplier list. Self-referencing for parent-subsidiary relationship.

```sql
CREATE TABLE suppliers (
    supplier_number         BIGINT PRIMARY KEY,
    supplier_name           TEXT NOT NULL,
    parent_supplier_number  BIGINT REFERENCES suppliers(supplier_number),
    parent_supplier_name    TEXT,
    supplier_type           TEXT CHECK (supplier_type IN ('Main', 'Subsidiary', 'Alternate')),
    email_contact           TEXT,
    currency                CHAR(3) DEFAULT 'GBP',
    created_at              TIMESTAMPTZ DEFAULT NOW()
);
```

**Test data scenarios to seed:**
- Diageo GB (subsidiary) → parent: Diageo GB Limited
- Colgate-Palmolive (main, no parent)
- Unilever UK (main, no parent)

---

### 2. `products`
Product master — one row per TPNB (Tesco Product Number Base).

```sql
CREATE TABLE products (
    tpnb                BIGINT PRIMARY KEY,
    tpnb_description    TEXT NOT NULL,
    category            TEXT NOT NULL,
    vat_rate_percent    NUMERIC(5,2),
    vat_code            TEXT,
    sell_by_weight_ind  CHAR(1) CHECK (sell_by_weight_ind IN ('I', 'W')),
    sell_by_weight_measure TEXT
);
```

---

### 3. `promotions`
One row per promotion. A promotion can span multiple weeks and multiple TPNBs.

```sql
CREATE TABLE promotions (
    promotion_reference_number  BIGINT PRIMARY KEY,
    promotion_api_uuid          UUID UNIQUE,
    promotion_description       TEXT,
    promotion_type              TEXT CHECK (promotion_type IN (
                                    'PERSONALISED_PRICE',
                                    'MULTI_BUY',
                                    'PRICE_REDUCTION',
                                    'TPR'
                                )),
    offer_start_date            DATE NOT NULL,
    offer_end_date              DATE NOT NULL,
    promotion_status            TEXT CHECK (promotion_status IN ('approved','pending','cancelled')),
    parent_promo_id             TEXT,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 4. `agreements`
Funding agreement between Tesco and the supplier for a specific promotion.
This is what the invoice is based on.

```sql
CREATE TABLE agreements (
    agreement_id                        SERIAL PRIMARY KEY,
    promotion_reference_number          BIGINT REFERENCES promotions(promotion_reference_number),
    funded_supplier_number              BIGINT REFERENCES suppliers(supplier_number),
    tpnb                                BIGINT REFERENCES products(tpnb),
    funding_method                      TEXT CHECK (funding_method IN (
                                            'Funding per promotional unit sold',
                                            'Fixed lump sum',
                                            'Percentage of sales'
                                        )),
    funding_start_date                  DATE,
    funding_end_date                    DATE,
    supplier_promotion_funding_per_unit NUMERIC(10,4),
    proposed_yccp_promotional_price     NUMERIC(10,2),
    agreement_data_source               TEXT CHECK (agreement_data_source IN ('BUYER', 'API', 'MANUAL')),
    funding_source                      TEXT,
    created_at                          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 5. `sales`
Weekly sales actuals at tpnb + supplier grain. Loaded from Tesco's sales systems.

```sql
CREATE TABLE sales (
    id                          SERIAL PRIMARY KEY,
    year_week_number            INT NOT NULL,          -- e.g. 202603
    tpnb                        BIGINT REFERENCES products(tpnb),
    sales_supplier              BIGINT REFERENCES suppliers(supplier_number),
    sales_parent_supplier_no    BIGINT REFERENCES suppliers(supplier_number),
    promotion_reference_number  BIGINT REFERENCES promotions(promotion_reference_number),
    sup_sales_value_inc_vat     NUMERIC(12,2),
    sup_sales_value_xvat        NUMERIC(12,2),
    sup_sales_volume            INT,
    sup_cost_of_goods_sold      NUMERIC(12,3),
    tot_sales_value_inc_vat     NUMERIC(12,2),
    tot_sales_value_xvat        NUMERIC(12,2),
    tot_sales_volume            INT,
    tot_cost_of_goods_sold      NUMERIC(12,3),
    UNIQUE (year_week_number, tpnb, sales_supplier, promotion_reference_number)
);
```

---

### 6. `calculations`
Output of the calculation engine. One row per invoice line.
This is what the agent reads to analyse disputes.

```sql
CREATE TABLE calculations (
    calculation_id              TEXT PRIMARY KEY,       -- e.g. YCCP-41
    internal_id                 INT UNIQUE,
    year_week_number            INT NOT NULL,
    calculation_week_number     INT NOT NULL,

    -- Supplier info
    funded_supplier_number      BIGINT REFERENCES suppliers(supplier_number),
    funded_supplier_name        TEXT,
    nominated_parent_supplier_number BIGINT REFERENCES suppliers(supplier_number),
    nominated_parent_supplier_name   TEXT,
    sales_supplier              BIGINT REFERENCES suppliers(supplier_number),
    sales_supplier_name         TEXT,
    sales_parent_supplier_no    BIGINT REFERENCES suppliers(supplier_number),
    sales_parent_supplier_name  TEXT,
    main_subsidiary_alternate   TEXT CHECK (main_subsidiary_alternate IN ('Main','Subsidiary','Alternate')),
    supplier_currency           CHAR(3),
    supplier_email_contact      TEXT,

    -- Product info
    tpnb                        BIGINT REFERENCES products(tpnb),
    tpnb_description            TEXT,
    category                    TEXT,

    -- Buyer info
    buyer_name                  TEXT,
    buyer_email_id              TEXT,
    junior_buyer                TEXT,
    buyer_hierarchy             TEXT,
    buying_controller           TEXT,
    category_director           TEXT,
    cost_centre_description     TEXT,
    cost_centre_code            TEXT,
    debtor_area                 TEXT,
    oracle_supplier             BIGINT,

    -- Promotion info
    promotion_reference_number  BIGINT REFERENCES promotions(promotion_reference_number),
    promotion_description       TEXT,
    promotion_type              TEXT,
    offer_start_date            DATE,
    offer_end_date              DATE,
    parent_promo_id             TEXT,
    promotion_status            TEXT,
    promotion_api_uuid          UUID,

    -- Funding / agreement info
    funding_method              TEXT,
    funding_start_date          DATE,
    funding_end_date            DATE,
    supplier_promotion_funding_per_unit  NUMERIC(10,4),
    proposed_yccp_promotional_price      NUMERIC(10,2),
    agreement_data_source       TEXT,
    funding_source              TEXT,

    -- Sales actuals (apportioned to this row)
    promo_sales_volume          INT,
    promotion_sales_volume_not_apportioned INT,
    discount_value_not_apportioned         NUMERIC(12,2),
    apportioned_discount_value             NUMERIC(12,2),
    sup_sales_value_inc_vat     NUMERIC(12,2),
    sup_sales_value_xvat        NUMERIC(12,2),
    sup_sales_volume            INT,
    sup_cost_of_goods_sold      NUMERIC(12,3),
    tot_sales_value_inc_vat     NUMERIC(12,2),
    tot_sales_value_xvat        NUMERIC(12,2),
    tot_sales_volume            INT,
    tot_cost_of_goods_sold      NUMERIC(12,3),

    -- Calculated output
    total_supplier_promotion_funding_ex_vat NUMERIC(12,2),
    vat_rate_percent            NUMERIC(5,2),
    vat_code                    TEXT,
    sell_by_weight_ind          CHAR(1),
    sell_by_weight_measure      TEXT,

    -- Deal info
    deal_description            TEXT,
    deal_status                 TEXT CHECK (deal_status IN ('Pending','Approved','Declined','Cancelled')),
    deal_dealref                TEXT,
    deal_created_week           INT,
    deal_approved_week          INT,
    deal_amount_gbp_exvat       NUMERIC(12,2),

    -- Validation checks
    funding_check               TEXT,
    funding_source_check        TEXT,
    promotion_source_check      TEXT,
    supplier_mismatch_check     TEXT,
    sales_volume_check          TEXT,
    missing_cost_center_check   TEXT,
    customer_details_check      TEXT,
    calculation_check           TEXT,
    invoicing_check             TEXT,
    final_check                 TEXT,

    -- Meta
    entry_row_number            INT,
    posted_timestamp            TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Calculation Query

This is the query that populates the `calculations` table.
The logic: join sales + agreements + promotions + supplier hierarchy,
then compute the funding amount.

```sql
INSERT INTO calculations (
    calculation_id,
    internal_id,
    year_week_number,
    calculation_week_number,
    funded_supplier_number,
    funded_supplier_name,
    nominated_parent_supplier_number,
    nominated_parent_supplier_name,
    sales_supplier,
    sales_supplier_name,
    sales_parent_supplier_no,
    sales_parent_supplier_name,
    main_subsidiary_alternate,
    tpnb,
    tpnb_description,
    category,
    promotion_reference_number,
    promotion_description,
    promotion_type,
    offer_start_date,
    offer_end_date,
    funding_method,
    funding_start_date,
    funding_end_date,
    supplier_promotion_funding_per_unit,
    promo_sales_volume,
    total_supplier_promotion_funding_ex_vat,
    deal_amount_gbp_exvat,
    sup_sales_value_inc_vat,
    sup_sales_value_xvat,
    sup_sales_volume,
    vat_rate_percent,
    vat_code,
    deal_status,
    final_check
)
SELECT
    -- IDs
    'YCCP-' || nextval('calculation_id_seq')        AS calculation_id,
    nextval('internal_id_seq')                       AS internal_id,
    s.year_week_number,
    s.year_week_number + 1                           AS calculation_week_number,

    -- Supplier hierarchy
    -- If subsidiary: invoice goes to parent, else invoice goes to sales supplier
    CASE
        WHEN sup.supplier_type = 'Subsidiary'
        THEN sup.parent_supplier_number
        ELSE s.sales_supplier
    END                                              AS funded_supplier_number,

    CASE
        WHEN sup.supplier_type = 'Subsidiary'
        THEN sup.parent_supplier_name
        ELSE sup.supplier_name
    END                                              AS funded_supplier_name,

    sup.parent_supplier_number                       AS nominated_parent_supplier_number,
    sup.parent_supplier_name                         AS nominated_parent_supplier_name,
    s.sales_supplier,
    sup.supplier_name                                AS sales_supplier_name,
    s.sales_parent_supplier_no,
    psup.supplier_name                               AS sales_parent_supplier_name,
    COALESCE(sup.supplier_type, 'Main')              AS main_subsidiary_alternate,

    -- Product
    p.tpnb,
    p.tpnb_description,
    p.category,

    -- Promotion
    pr.promotion_reference_number,
    pr.promotion_description,
    pr.promotion_type,
    pr.offer_start_date,
    pr.offer_end_date,

    -- Agreement / funding
    ag.funding_method,
    ag.funding_start_date,
    ag.funding_end_date,
    ag.supplier_promotion_funding_per_unit,

    -- Sales actuals
    s.sup_sales_volume                               AS promo_sales_volume,

    -- THE CORE CALCULATION
    -- total funding = units sold × agreed rate per unit
    ROUND(s.sup_sales_volume * ag.supplier_promotion_funding_per_unit, 2)
                                                     AS total_supplier_promotion_funding_ex_vat,
    ROUND(s.sup_sales_volume * ag.supplier_promotion_funding_per_unit, 2)
                                                     AS deal_amount_gbp_exvat,

    s.sup_sales_value_inc_vat,
    s.sup_sales_value_xvat,
    s.sup_sales_volume,
    p.vat_rate_percent,
    p.vat_code,

    -- Initial deal status
    'Pending'                                        AS deal_status,

    -- Final check: passes only if sales volume > 0 and agreement exists
    CASE
        WHEN s.sup_sales_volume > 0
         AND ag.agreement_id IS NOT NULL
         AND ag.supplier_promotion_funding_per_unit > 0
        THEN 'READY FOR INVOICING'
        ELSE 'FAILED'
    END                                              AS final_check

FROM sales s

-- Product
JOIN products p
    ON s.tpnb = p.tpnb

-- Promotion
JOIN promotions pr
    ON s.promotion_reference_number = pr.promotion_reference_number
    AND pr.promotion_status = 'approved'

-- Agreement: match on promotion + tpnb + supplier
-- Use sales_supplier OR its parent (handles subsidiary case)
JOIN agreements ag
    ON ag.promotion_reference_number = s.promotion_reference_number
    AND ag.tpnb = s.tpnb
    AND (
        ag.funded_supplier_number = s.sales_supplier
        OR ag.funded_supplier_number = s.sales_parent_supplier_no
    )
    -- Sales week must fall within funding window
    AND s.year_week_number BETWEEN
        EXTRACT(ISOYEAR FROM ag.funding_start_date) * 100 + EXTRACT(WEEK FROM ag.funding_start_date)
        AND
        EXTRACT(ISOYEAR FROM ag.funding_end_date) * 100 + EXTRACT(WEEK FROM ag.funding_end_date)

-- Supplier master
JOIN suppliers sup
    ON s.sales_supplier = sup.supplier_number

-- Parent supplier (optional — may be null for Main type)
LEFT JOIN suppliers psup
    ON s.sales_parent_supplier_no = psup.supplier_number

WHERE s.year_week_number = :target_week   -- parameterised, run weekly
;
```

