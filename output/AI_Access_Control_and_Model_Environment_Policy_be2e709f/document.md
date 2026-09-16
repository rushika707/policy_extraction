## AI Development Access and Model Environment Control Policy

Policy ID: AI-SEC-AC-014 | Version: 3.1 | Effective Date: 15 September 2026

## 1. Policy Metadata

Owner:

AI Security and Governance

Applies to: Employees, contractors, service accounts and automated agents accessing AI development environments.

Review: Annual and following a material security or regulatory change.

## 2. Purpose

This policy establishes controls for granting, reviewing, monitoring and revoking access to environments used to develop, test, fine-tune and operate artificial intelligence models. Access decisions must consider identity, environment sensitivity, privilege level, authentication strength and approved business justification.

## 3. Scope

The policy covers development workstations, shared notebooks, model training clusters, evaluation environments, staging systems, production inference services, model registries and associated service accounts. It applies to interactive users and non-human identities.

## 4. Access Classification Matrix

| Environment   | Minimum Authentication   | Maximum Privilege   | Approval                 |
|---------------|--------------------------|---------------------|--------------------------|
| Development   | MFA                      | Developer           | Team lead                |
| Evaluation    | MFA + managed device     | Developer           | Model owner              |
| Staging       | MFA + managed device     | Operator            | Model owner + Security   |
| Production    | Phishing-resistant MFA   | Operator            | Service owner + Security |

## 5. Mandatory Controls

AC-01 - Unique identity: Shared human accounts must not be used to access model development or production environments. Every human user must authenticate using an individually assigned identity.

AC-02 - MFA: Multi-factor authentication is mandatory for all interactive access. Production access requires phishing-resistant MFA.

AC-03 - Least privilege: Access must use the lowest privilege necessary for the approved task. Administrative privileges require separate approval.

AC-04 - Time-bound elevation: Privileged elevation must have an expiry time. Elevation lasting longer than 8 hours requires explicit security approval.

AC-05 - Service accounts: Non-human identities must have a named owner, documented purpose and credential rotation interval not exceeding 90 days.

AC-06 - Access review: Access to production and staging must be reviewed at least every 90 days. Development access must be reviewed at least every 180 days.

AC-07 - Inactive access: An account with no successful authentication for 60 consecutive days must be suspended unless an approved exception exists.

AC-08 - Termination: Access for a departing worker must be revoked no later than the end of the worker's final authorized working period.

AC-09 - Logging: Authentication, privilege elevation, access grants, access revocations and failed production access attempts must be retained for at least 12 months.

## 6. Elevated Access Conditions

An elevation request is approved only when the requester has a valid business justification, the target environment is identified, the requested privilege is specified and an accountable approver is recorded. Emergency elevation may be granted by the on-call security authority for up to 4 hours. The emergency action must be reviewed by Security within 1 business day.

## 7. Exceptions

Exceptions must identify the affected identity or group, environment, control being bypassed, business justification, risk assessment, compensating control, approver and expiry date. An exception without an expiry date is invalid. Security may revoke an exception immediately when the associated risk materially changes.

## 8. Decision Outcomes

| Outcome   | Condition                                              | Action                                           |
|-----------|--------------------------------------------------------|--------------------------------------------------|
| ALLOW     | All applicable controls are satisfied.                 | Grant or retain the requested access.            |
| DENY      | A mandatory control is not satisfied.                  | Do not grant access.                             |
| SUSPEND   | Existing access violates an active control.            | Suspend access until the issue is resolved.      |
| EXCEPTION | An approved exception is active and within its expiry. | Permit access only within documented conditions. |

## 9. Monitoring and Enforcement

Security monitoring must identify repeated failed production authentication, unauthorized privilege elevation, expired exceptions and access that remains active after required review. Where a mandatory control is violated, access may be suspended pending investigation. Repeated or material violations may result in escalation to the service owner, Security leadership or the relevant risk committee.

## 10. Required Audit Evidence

- Identity or service-account identifier and owner
- Environment and privilege requested
- Business justification and approver
- Authentication method
- Grant, review, elevation, suspension and revocation timestamps
- Exception reference and expiry where applicable
- Relevant security event or investigation reference

## 11. Non-Compliance

Failure to comply with this policy may result in access suspension, mandatory remediation, security investigation and escalation according to organisational procedures. No application team may permanently bypass a mandatory access control by changing application configuration without an approved policy exception.

## 12. Document Control

Version:

3.1

Change summary: Added service-account rotation, inactivity suspension and emergency elevation controls.

Next review:

September 2027.