## Alternative AI Training Data Privacy Policy

Policy ID: AI-DP-PII-002 Version: 1.0 Classification: Internal

Purpose: Test document containing a different set of PII, SPII and CPII rules for the Policy-as-Code extraction pipeline.

## 1. Decision Definitions

PASS:

No PII, SPII or CPII is detected.

FLAG: Personal data is detected and the record requires remediation before permitted use.

BLOCK: Sensitive or high-risk personal data is detected and the record must be excluded unless an approved exception exists.

## 2. PII Rules

| Rule ID   | Data Type                   | Trigger / Fields                                          | Outcome   |
|-----------|-----------------------------|-----------------------------------------------------------|-----------|
| PII-101   | Username / account handle   | username, account_handle, screen_name                     | FLAG      |
| PII-102   | Date of birth               | date_of_birth, dob, birth_date                            | FLAG      |
| PII-103   | Personal URL                | personal_website, profile_url linked to an individual     | FLAG      |
| PII-104   | Vehicle registration number | vehicle_registration, registration_plate                  | FLAG      |
| PII-105   | Geolocation information     | precise_location, GPS coordinates linked to an individual | FLAG      |
| PII-106   | Emergency contact details   | emergency_contact_name, emergency_contact_phone           | FLAG      |
| PII-107   | Tax identification number   | tax_id, taxpayer_number                                   | BLOCK     |
| PII-108   | Travel document reference   | passport_reference, travel_document_id                    | BLOCK     |

## 3. SPII Rules

| Rule ID   | Data Type                            | Trigger / Fields                                          | Outcome   |
|-----------|--------------------------------------|-----------------------------------------------------------|-----------|
| SPII-101  | Mental health information            | mental_health_status, psychiatric_history, therapy_record | BLOCK     |
| SPII-102  | Sexual orientation                   | sexual_orientation, orientation                           | BLOCK     |
| SPII-103  | Criminal record information          | criminal_record, conviction, alleged_offence              | BLOCK     |
| SPII-104  | Financial hardship information       | debt_status, insolvency, financial_hardship               | BLOCK     |
| SPII-105  | Immigration status                   | visa_status, immigration_status, asylum_status            | BLOCK     |
| SPII-106  | Religious practice details           | worship_attendance, religious_practice, faith_activity    | BLOCK     |
| SPII-107  | Disability accommodation information | reasonable_adjustment, accommodation_need                 | BLOCK     |

## 4. CPII Rules

| Rule ID   | Combination                                           | Trigger                                               | Outcome   |
|-----------|-------------------------------------------------------|-------------------------------------------------------|-----------|
| CPII-101  | Name + employer + job title                           | full_name + employer + job_title                      | FLAG      |
| CPII-102  | Date of birth + city + gender                         | dob + city + gender                                   | FLAG      |
| CPII-103  | Username + email domain + organisation                | username + email_domain + organisation                | FLAG      |
| CPII-104  | Vehicle registration + postcode                       | registration_plate + postcode                         | FLAG      |
| CPII-105  | Employee number + manager + work location             | employee_number + manager_name + work_location        | FLAG      |
| CPII-106  | Customer reference + transaction timestamp + merchant | customer_reference + transaction_time + merchant_name | FLAG      |

| Rule ID   | Combination                                        | Trigger                                                       | Outcome   |
|-----------|----------------------------------------------------|---------------------------------------------------------------|-----------|
| CPII-107  | Free text containing multiple indirect identifiers | free_text containing two or more linkable personal attributes | FLAG      |
| CPII-108  | Location history + device identifier               | location_history + device_id                                  | FLAG      |

## 5. Remediation Requirements

For FLAG records, permitted remediation methods include removal, masking, tokenisation, generalisation, pseudonymisation, or anonymisation, as appropriate to the data.

For BLOCK records, the personal data must be removed or transformed sufficiently before use. An approved exception may permit controlled use where explicitly authorised.

For PASS records, no remediation is required.

## 6. Testing Notes

This document intentionally uses different rule IDs and data types from the original policy. It is designed to test whether the extraction pipeline detects new rules, categories, combinations, decisions and remediation guidance rather than relying on hardcoded rules.