# Database Structure

finance.db is a read-only SQLite dataset for six companies. Company CIK values are strings. Use the company table or companies.json to resolve names, and keep the supplied database unchanged when creating derived views or indexes.

## Table overview

| Table | Rows | Purpose |
|---|---:|---|
| companies | 6 | Company identity and registration information. The description field is empty in this dataset. |
| company_tickers | 6 | Stock ticker and exchange information. |
| company_addresses | 12 | Business and mailing addresses. |
| filings | 5,889 | SEC filing metadata: accession, form, dates, and primary-document filename. This table contains no report body. |
| financial_facts | 86,306 | Numeric financial facts, units, period metadata, and source filing references. |
| table_comments | 9 | Imported short table descriptions. |
| column_comments | 60 | Imported short column descriptions. |
| table_documentation | 9 | Imported detailed table descriptions. |
| column_documentation | 8 | Imported detailed column descriptions. |

## Interpreting the core fields

- companies.cik identifies a company. Join company-related tables by cik, not by display names.
- financial_facts.fact_name is a financial concept; fact_category is its taxonomy namespace. Standard namespaces may include us-gaap, dei, and srt (SEC Reporting Taxonomy).
- fact_value is numeric and must be interpreted with unit. USD values are in dollars unless the original unit says otherwise. NULL and missing facts are not zero.
- fiscal_year and fiscal_period are source disclosure labels. A filing can repeat earlier-year comparative figures. Check end_date, frame, filed_date, and form_type before selecting a period; complete start_date information is not available.
- accession_number identifies a submission and normally has the form ##########-YY-######. Its prefix need not equal the company's CIK. Combine cik and accession_number when relating facts to filings; some fact references have no matching metadata row.
- dimension_segment and dimension_geography are empty in the provided records. A field's presence does not establish that dimensional detail is available; some fact names can nevertheless describe specific categories.
- filings.primary_document is a filename, and primary_doc_description is a short label. Neither contains report text. Bundled HTML reports are listed separately in filings/README.md; most filing metadata rows have no corresponding local document.
- The same value can be disclosed in several submissions. Do not sum repeated disclosures. See business_rules.md for units, period selection, duplicates, and calculation conventions.

## Complete table definitions

The definitions below reflect the actual database structure. The four documentation tables contain imported descriptions for discovery; they are not company report text. SQLite also maintains sqlite_sequence for autoincrement keys.

### companies

```sql
CREATE TABLE companies (
            cik TEXT PRIMARY KEY,
            entity_type TEXT,
            sic TEXT,
            sic_description TEXT,
            owner_org TEXT,
            insider_transaction_for_owner_exists INTEGER,
            insider_transaction_for_issuer_exists INTEGER,
            name TEXT NOT NULL,
            ein TEXT,
            lei TEXT,
            description TEXT,
            website TEXT,
            investor_website TEXT,
            category TEXT,
            fiscal_year_end TEXT,
            state_of_incorporation TEXT,
            state_of_incorporation_description TEXT,
            phone TEXT,
            flags TEXT,
            former_names TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
```

### company_tickers

```sql
CREATE TABLE company_tickers (
            cik TEXT NOT NULL,
            ticker TEXT NOT NULL,
            exchange TEXT,
            PRIMARY KEY (cik, ticker),
            FOREIGN KEY (cik) REFERENCES companies(cik)
        )
```

### company_addresses

```sql
CREATE TABLE company_addresses (
            cik TEXT NOT NULL,
            address_type TEXT NOT NULL, -- 'mailing' or 'business'
            street1 TEXT,
            street2 TEXT,
            city TEXT,
            state_or_country TEXT,
            zip_code TEXT,
            state_or_country_description TEXT,
            is_foreign_location INTEGER,
            foreign_state_territory TEXT,
            country TEXT,
            country_code TEXT,
            PRIMARY KEY (cik, address_type),
            FOREIGN KEY (cik) REFERENCES companies(cik)
        )
```

### filings

```sql
CREATE TABLE filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT NOT NULL,
            accession_number TEXT NOT NULL,
            filing_date DATE,
            report_date DATE,
            acceptance_date_time TEXT,
            act TEXT,
            form TEXT,
            file_number TEXT,
            film_number TEXT,
            items TEXT,
            core_type TEXT,
            size INTEGER,
            is_xbrl INTEGER,
            is_inline_xbrl INTEGER,
            primary_document TEXT,
            primary_doc_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (cik, accession_number),
            FOREIGN KEY (cik) REFERENCES companies(cik)
        )
```

### financial_facts

```sql
CREATE TABLE financial_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cik TEXT NOT NULL,
                fact_name TEXT NOT NULL,
                fact_value REAL,
                unit TEXT NOT NULL,
                fact_category TEXT NOT NULL,
                fiscal_year INTEGER,
                fiscal_period TEXT,
                end_date DATE,
                accession_number TEXT,
                form_type TEXT,
                filed_date DATE,
                frame TEXT,
                dimension_segment TEXT,
                dimension_geography TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cik) REFERENCES companies(cik)
            )
```

### table_comments

```sql
CREATE TABLE table_comments (
            table_name TEXT PRIMARY KEY,
            comment TEXT NOT NULL
        )
```

### column_comments

```sql
CREATE TABLE column_comments (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            comment TEXT NOT NULL,
            PRIMARY KEY (table_name, column_name)
        )
```

### table_documentation

```sql
CREATE TABLE table_documentation (
            table_name TEXT PRIMARY KEY,
            documentation TEXT NOT NULL
        )
```

### column_documentation

```sql
CREATE TABLE column_documentation (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            documentation TEXT NOT NULL,
            PRIMARY KEY (table_name, column_name)
        )
```
