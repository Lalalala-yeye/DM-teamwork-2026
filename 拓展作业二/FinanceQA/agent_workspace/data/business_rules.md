# Data Usage and Business Rules

This document and the data dictionary are publicly provided and may be read by the Agent, Skills, and memory components. They establish a shared basis for interpreting the data; they do not provide question-specific mappings or solutions.

## Companies, Metrics, and Units

- CIK is a company identifier represented as a string. Use it to join tables rather than relying on the spelling of company names.
- fact_name identifies a financial concept. Companies may use different tags; do not assume that a single natural-language term maps to the same English tag for every company.
- fact_category identifies the source taxonomy of a concept. Do not mix similarly named tags without explaining their definitions.
- Interpret fact_value together with unit. USD denotes US dollar amounts, and USD/shares denotes US dollars per share. Values are stored in their original units; do not assume they have been scaled to millions or billions.
- Net income, net income attributable to the parent, operating income, and pretax income are distinct metrics. State the definition used and do not substitute them arbitrarily. A negative IncomeTaxExpenseBenefit usually indicates an income tax benefit.
- NULL is not zero. A missing tag does not mean the corresponding business amount is zero. Look for an applicable equivalent concept or explicitly state that the data are insufficient.

## Reporting Periods

- Determine the analysis period from the original question and the filing and date information in the database. A company's fiscal year does not necessarily end on December 31.
- fiscal_year, filed_date, and end_date have different meanings. A filing may contain comparative figures for earlier years. Do not treat fiscal_year or filed_date as the year to which a metric belongs without checking.
- Revenue, profit, and expenses are flows over a period; assets and liabilities are balances at a point in time. Do not present quarterly flows as full-year figures or sum repeated disclosures.
- frame can help identify annual periods, quarters, and point-in-time observations. For non-calendar fiscal years, the year in frame may differ from the fiscal year; check the actual end_date.
- An empty frame does not mean that data are absent, nor does it establish that a record is annual. Year-end balances may be used after confirming the date and reporting basis; flow records also require checking the period length. This database does not provide complete start_date information. Do not guess when the period of a flow cannot be reliably determined.
- The source database retains annual and subsequent quarterly data. Select the period appropriate to the original question rather than automatically treating the latest-dated row as the annual figure requested.

## Duplicate Disclosures and Revisions

- The same metric, unit, and period may appear in multiple filings. Do not sum these repeated disclosures.
- Confirm that the concept, unit, period, and dimensions match before handling duplicates. Once a common reporting basis is established, give preference to the latest available applicable annual disclosure within the database snapshot. If records conflict, explain the selection rather than inferring business priority from record IDs.
- Use accession_number, filed_date, form_type, and record IDs to trace sources. Comparing different versions is allowed.
- dimension_segment and dimension_geography describe business segments and geographic dimensions. Distinguish consolidated figures from segment figures to avoid double counting. Empty dimensions do not by themselves establish comparability across companies.

## Calculations

- Year-over-year growth = (current-period value / prior-year comparable-period value - 1) × 100%. This formula cannot be applied directly when the denominator is zero.
- Profit margin = profit under a stated definition / revenue on a consistent basis × 100%. Express differences between margins in percentage points; this is different from the percentage growth of the margin itself.
- For applicable businesses, operating ratio means operating expenses / operating revenue. A decrease usually indicates a lower expense share. Do not mix reported and adjusted measures.
- Expense line items may already be included in a total. Do not add components to a total that already includes them.
- Necessary metrics may be derived using accounting identities, but label them as derived, list the operands, and verify their definitions. Do not claim that a calculated value is a directly disclosed field.
- Co-movement does not establish causality. When the original question asks for reasons, provide sufficient support rather than filling gaps with unverified industry knowledge.

## Source Completeness

The source filings table contains the filing metadata collected by the original database. It may not contain a matching filing entry for every historical financial fact. The package preserves these original gaps, as in the source snapshot. Trace facts using financial_facts IDs, accession numbers, and dates, but do not fabricate missing metadata.

The local data/filings/ directory contains SEC primary-report HTML snapshots. Read filings/README.md for the company, report-period, and local-file catalog. Text, tables, and notes can supplement the structured financial facts. Separate exhibits and external images referenced by the HTML are not bundled. A source URL is provenance, not permission to expand the main experiment's data sources.

Keep report identity and location when extracting evidence. Distinguish historical results from hypothetical sensitivity analyses, risk statements, future intentions, and forecasts. A planned action does not establish that an expense has already been recognized. If documents and numerical data conflict, check definitions, periods, and units and describe unresolved differences.

Do not use external internet sources to supplement the factual basis of answers in this task. If external information is explored, report it separately and exclude it from the main comparison based on the provided database and local reports.
