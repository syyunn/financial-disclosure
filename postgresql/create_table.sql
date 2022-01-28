create schema if not exists financial_disclosures;

drop table if exists financial_disclosures.senate;

create table if not exists financial_disclosures.senate(
   first_name text,
   last_name text,
   office text,
   report_type text,
   report_type_url text,
   date_received date,
   PRIMARY KEY(first_name, last_name, office, report_type, report_type_url, date_received)
)


drop table if exists financial_disclosures.senate_periodic_transaction_report;

create table if not exists financial_disclosures.senate_periodic_transaction_report(
   transaction_date	date,
   owner text,
   ticker text,
   ticker_url text,
   asset_name text,
   asset_type text,
   type text,
   amount int4range,
   PRIMARY KEY(transaction_date, owner, ticker, ticker_url, asset_name, asset_type, type, amount)
)


