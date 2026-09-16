package policy

# ------------------------------------------------------------------
# Rule definitions extracted from the policy JSON
# ------------------------------------------------------------------

# Direct identifier rules
direct_rules := [
    {"id": "PII-01", "fields": ["first_name", "last_name", "full_name", "customer_name"], "outcome": "FLAG"},
    {"id": "PII-02", "fields": ["email", "personal_email", "contact_email"], "outcome": "FLAG"},
    {"id": "PII-03", "fields": ["mobile", "telephone", "phone_number"], "outcome": "FLAG"},
    {"id": "PII-04", "fields": ["address", "home_address", "street", "postcode"], "outcome": "FLAG"},
    {"id": "PII-05", "fields": ["ni_number", "nino"], "outcome": "BLOCK"},
    {"id": "PII-06", "fields": ["passport_number"], "outcome": "BLOCK"},
    {"id": "PII-07", "fields": ["driving_licence_number"], "outcome": "BLOCK"},
    {"id": "PII-08", "fields": ["bank_account", "sort_code", "credit_card_number"], "outcome": "BLOCK"},
    {"id": "PII-09", "fields": ["ip_address", "device_id", "cookie_id", "user_id"], "outcome": "FLAG"}
]

# Sensitive personal data rules
sensitive_rules := [
    {"id": "SPII-01", "fields": ["medical_condition", "diagnosis", "treatment", "disability_information"], "outcome": "BLOCK"},
    {"id": "SPII-02", "fields": ["ethnicity", "race", "racial_origin"], "outcome": "BLOCK"},
    {"id": "SPII-03", "fields": ["religion", "belief"], "outcome": "BLOCK"},
    {"id": "SPII-04", "fields": ["political_view", "party_preference"], "outcome": "BLOCK"},
    {"id": "SPII-05", "fields": ["union_member", "trade_union"], "outcome": "BLOCK"},
    {"id": "SPII-06", "fields": ["faceprint", "fingerprint", "iris_scan", "dna_profile"], "outcome": "BLOCK"}
]

# Combination rules
combination_rules := [
    {"id": "CPII-01", "combination": ["full_name", "date_of_birth"], "outcome": "FLAG"},
    {"id": "CPII-02", "combination": ["full_name", "address", "postcode"], "outcome": "FLAG"},
    {"id": "CPII-03", "combination": ["full_name", "phone_number"], "outcome": "FLAG"},
    {"id": "CPII-04", "combination": ["full_name", "email", "personal_email", "contact_email"], "outcome": "FLAG"},
    {"id": "CPII-05", "combination": ["date_of_birth", "postcode", "gender"], "outcome": "FLAG"},
    {"id": "CPII-06", "combination": ["employee_id", "department", "role"], "outcome": "FLAG"},
    {"id": "CPII-07", "combination": ["customer_id", "account_event_details"], "outcome": "FLAG"},
    {"id": "CPII-08", "combination": ["comments"], "outcome": "FLAG"}
]

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

# Check if any of the specified fields exist in the record
field_present(record, fields) := present if {
    some f in fields
    record[f]
}

# Check if all of the specified fields exist in the record
all_fields_present(record, fields) := present if {
    all f in fields {
        record[f]
    }
}

# ------------------------------------------------------------------
# Rule outcome determination
# ------------------------------------------------------------------

# Determine outcome for a single rule
rule_outcome(rule, record) := outcome if {
    rule["outcome"] = outcome
    (
        # Direct or sensitive rules
        (rule["fields"] != null
         field_present(record, rule["fields"])
        )
        # Combination rules
        ;
        (rule["combination"] != null
         all_fields_present(record, rule["combination"])
        )
    )
}

# ------------------------------------------------------------------
# Decision logic
# ------------------------------------------------------------------

# Collect all triggered rule outcomes
triggered_outcomes := outcomes if {
    some r in direct_rules {
        o := rule_outcome(r, input.record)
        outcomes := outcomes + [o]
    }
    some r in sensitive_rules {
        o := rule_outcome(r, input.record)
        outcomes := outcomes + [o]
    }
    some r in combination_rules {
        o := rule_outcome(r, input.record)
        outcomes := outcomes + [o]
    }
}

# Determine final decision based on priority: BLOCK > EXCEPTION APPROVED > FLAG > PASS
decision := final if {
    # If any BLOCK outcome, decision is BLOCK
    some o in triggered_outcomes {
        o == "BLOCK"
    }
    final = "BLOCK"
}
decision := final if {
    # If any EXCEPTION APPROVED outcome and no BLOCK, decision is EXCEPTION APPROVED
    not some o in triggered_outcomes { o == "BLOCK" }
    some o in triggered_outcomes { o == "EXCEPTION APPROVED" }
    final = "EXCEPTION APPROVED"
}
decision := final if {
    # If any FLAG outcome and no BLOCK or EXCEPTION APPROVED, decision is FLAG
    not some o in triggered_outcomes { o == "BLOCK" }
    not some o in triggered_outcomes { o == "EXCEPTION APPROVED" }
    some o in triggered_outcomes { o == "FLAG" }
    final = "FLAG"
}
decision := "PASS" if {
    # No triggered outcomes
    not some o in triggered_outcomes { true }
}

# ------------------------------------------------------------------
# Evidence metadata (non-executable)
# ------------------------------------------------------------------
# The following data elements are retained for audit purposes but do not influence decision logic.

evidence_items := [
    {"item": "Dataset name", "requirement": "Name and version of the dataset assessed."},
    {"item": "Scan date", "requirement": "Date when the dataset was scanned."},
    {"item": "Triggered rule IDs", "requirement": "List of policy rules triggered by each flagged record."},
    {"item": "Decision", "requirement": "PASS, FLAG, BLOCK or EXCEPTION APPROVED."},
    {"item": "Remediation status", "requirement": "Not required, pending, completed or exception approved."},
    {"item": "Reviewer or approver", "requirement": "Named reviewer or approval reference where required."}
]