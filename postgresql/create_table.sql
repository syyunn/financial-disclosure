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


