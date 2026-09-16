## AI Training Data PII Policy

Student version | Policy document for conversion into Policy-as-Code

| Policy metadata   | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| Policy ID         | AI-DP-PII-001                                                                        |
| Policy name       | AI Training Data PII Policy                                                          |
| Version           | 1.0                                                                                  |
| Classification    | Internal                                                                             |
| Policy owner      | Data Protection Office                                                               |
| Applies to        | Training, testing, fine-tuning and evaluation datasets used for AI, ML and analytics |
| Review cycle      | Annual or upon material change to privacy, AI or data governance requirements        |

## 1. Purpose

This policy defines mandatory requirements for identifying, flagging and remediating personal data in datasets used for artificial intelligence, machine learning, model fine-tuning, model evaluation and analytics activities.

## 2. Scope

This policy applies to all datasets that are proposed for AI or machine learning use, including raw data, curated training data, labelled data, test data, validation data, embeddings, logs, prompts, responses and synthetic data derived from personal data.

## 3. Policy Objective

Datasets must be assessed before use. Records containing personal data must be flagged. Records containing unresolved personal data must not be used for AI training, fine-tuning or evaluation unless an approved exception is recorded.

## 4. Definitions

| Term                    | Policy definition                                                                                                                      |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Personal data / PII     | Information that identifies, or can reasonably identify, a living individual either directly or in combination with other information. |
| Direct identifier       | A data item that can identify an individual on its own.                                                                                |
| Indirect identifier     | A data item that may identify an individual when combined with other information.                                                      |
| Sensitive personal data | More sensitive information such as health, ethnicity, religion, political opinion, biometric or genetic information.                   |
| Training data           | Any dataset used to train, fine-tune, evaluate or improve an AI, ML or analytics model.                                                |
| Flagged record          | A dataset record where one or more policy rules identify personal data or suspected personal data.                                     |
| Remediation             | Action taken to remove, mask, tokenise, generalise or anonymise personal data before dataset use.                                      |

## 5. PII Classification Catalogue

## 5.1 Direct identifiers

The following fields are treated as personal data when present in training data and must be flagged.

| Rule ID   | PII type                            | Examples                                                             | Required policy outcome         |
|-----------|-------------------------------------|----------------------------------------------------------------------|---------------------------------|
| PII-01    | Full name                           | first_name, last_name, full_name, customer_name                      | Flag record                     |
| PII-02    | Personal email address              | email, personal_email, contact_email                                 | Flag record                     |
| PII-03    | Phone or mobile number              | mobile, telephone, phone_number                                      | Flag record                     |
| PII-04    | Postal or home address              | address, home_address, street, postcode with address                 | Flag record                     |
| PII-05    | National Insurance number           | ni_number, nino                                                      | Block until removed or approved |
| PII-06    | Passport number                     | passport_number                                                      | Block until removed or approved |
| PII-07    | Driving licence number              | driving_licence_number                                               | Block until removed or approved |
| PII-08    | Bank account or payment card number | bank_account, sort_code, credit_card_number                          | Block until removed or approved |
| PII-09    | Online identifier                   | IP address, device ID, cookie ID, user ID where linkable to a person | Flag record                     |

## 5.2 Sensitive personal data

The following fields are treated as sensitive personal data when present in training data and must be blocked unless a documented approval exists.

| Rule ID   | Sensitive data type           | Examples                                                        | Required policy outcome   |
|-----------|-------------------------------|-----------------------------------------------------------------|---------------------------|
| SPII-01   | Health or medical information | medical_condition, diagnosis, treatment, disability information | Block record              |
| SPII-02   | Ethnicity or racial origin    | ethnicity, race, racial_origin                                  | Block record              |
| SPII-03   | Religion or belief            | religion, belief                                                | Block record              |
| SPII-04   | Political opinion             | political_view, party_preference                                | Block record              |
| SPII-05   | Trade union membership        | union_member, trade_union                                       | Block record              |
| SPII-06   | Biometric or genetic data     | faceprint, fingerprint, iris_scan, DNA profile                  | Block record              |

## 5.3 Indirect identifiers and combination rules

Some fields may not identify a person on their own but can identify a person when combined with other attributes. The following combinations must be flagged as personal data.

| Rule ID   | Combination rule                                                            | Required policy outcome   |
|-----------|-----------------------------------------------------------------------------|---------------------------|
| CPII-01   | Full name + date of birth                                                   | Flag record               |
| CPII-02   | Full name + postal address or postcode                                      | Flag record               |
| CPII-03   | Full name + phone number                                                    | Flag record               |
| CPII-04   | Full name + personal email address                                          | Flag record               |
| CPII-05   | Date of birth + postcode + gender                                           | Flag record               |
| CPII-06   | Employee ID + department + role where linkable to a person                  | Flag record               |
| CPII-07   | Customer ID + account event details where the customer can be re-identified | Flag record               |
| CPII-08   | Free-text comments containing personal identifiers                          | Flag record               |

## 6. Mandatory Policy Requirements

| Rule ID   | Policy requirement         | Policy statement                                                                                                            |
|-----------|----------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| DP-01     | Pre-use scan               | Training data must be scanned for personal data before it is used for model training, fine-tuning, testing or evaluation.   |
| DP-02     | Record-level flagging      | Each record containing direct, sensitive or combination-based personal data must be flagged.                                |
| DP-03     | Direct identifier handling | Direct identifiers must be removed, masked, tokenised or replaced before the record is approved for training use.           |
| DP-04     | Sensitive data handling    | Sensitive personal data must be blocked from training data unless a documented approval and control justification exists.   |
| DP-05     | Combination rule handling  | Records matching combination rules must be reviewed and remediated before use.                                              |
| DP-06     | Free-text scanning         | Free-text fields such as comments, notes, feedback and descriptions must be scanned for personal data patterns.             |
| DP-07     | Remediation evidence       | Every remediated record must retain evidence of the remediation method applied.                                             |
| DP-08     | Approved dataset output    | Only records with no unresolved personal data findings may be included in the approved training dataset.                    |
| DP-09     | Exception handling         | Exceptions must be documented, risk-assessed, time-bound and approved by the Data Protection Office or delegated authority. |
| DP-10     | Audit trail                | The scan result, triggered rule, decision, remediation status and approver must be retained for audit purposes.             |

## 7. Dataset Decision Outcomes

| Decision           | Meaning                                                            | Required action                                                   |
|--------------------|--------------------------------------------------------------------|-------------------------------------------------------------------|
| PASS               | No personal data or suspected personal data has been detected.     | Record may be included in the approved training dataset.          |
| FLAG               | Direct or combination-based personal data has been detected.       | Record must be remediated before training use.                    |
| BLOCK              | Sensitive personal data or high-risk identifier has been detected. | Record must be excluded unless approved exception exists.         |
| EXCEPTION APPROVED | A documented approval allows controlled use of the record.         | Use only under the approved conditions and retain audit evidence. |

## 8. Remediation Requirements

| Remediation method   | Policy expectation                                                                        |
|----------------------|-------------------------------------------------------------------------------------------|
| Removal              | Delete the personal data field or remove the record where the field is not required.      |
| Masking              | Replace part of the value while preserving limited analytical utility, where appropriate. |
| Tokenisation         | Replace the identifier with a non-identifying token.                                      |
| Generalisation       | Reduce precision, such as replacing exact date of birth with age band.                    |
| Anonymisation        | Transform data so individuals are no longer reasonably identifiable.                      |

## 9. Minimum Evidence Required

| Evidence item        | Requirement                                             |
|----------------------|---------------------------------------------------------|
| Dataset name         | Name and version of the dataset assessed.               |
| Scan date            | Date when the dataset was scanned.                      |
| Triggered rule IDs   | List of policy rules triggered by each flagged record.  |
| Decision             | PASS, FLAG, BLOCK or EXCEPTION APPROVED.                |
| Remediation status   | Not required, pending, completed or exception approved. |
| Reviewer or approver | Named reviewer or approval reference where required.    |

## 10. Non-compliance

Datasets with unresolved personal data findings must not be used for AI training, fine-tuning, testing or evaluation. Non-compliance may result in suspension of dataset use, removal of system access, escalation to the data owner, supplier remediation or other action determined by the organisation.

## 11. Policy Review

This policy must be reviewed at least annually or when there is a material change to privacy, AI governance, data use, model development or regulatory requirements.

## Document control

|   Version | Date         | Summary of change                                                         | Owner                  |
|-----------|--------------|---------------------------------------------------------------------------|------------------------|
|       1.0 | 24 July 2026 | Initial student version for AI training data PII policy-as-code exercise. | Data Protection Office |

## Formatting specification used for this PDF

A4 page size with approximately 18 mm side margins; dark blue section hierarchy; light blue alternating table rows; clean sans-serif typography; compact 7-8 pt table text; 9.2 pt body text; 14 pt section headings; 21 pt title; consistent footer and page numbering.