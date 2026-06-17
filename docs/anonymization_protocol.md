Anonymization Protocol
1. Purpose

This protocol defines how sensitive materials are handled in the Remote ERP Onboarding Workflow Case Study.

The purpose is to protect individuals, companies, customers, credentials, project details, and confidential information while preserving the analytical value of the case.

2. Public Repository Rule

The public GitHub repository must contain only:

anonymized analysis
reconstructed summaries
synthetic datasets
self-authored diagrams
self-authored code
generic workflow structures
generalized case interpretations

The public repository must not contain raw internal files.

3. Materials Not to Upload

The following materials must not be uploaded publicly.

raw meeting recordings
raw meeting notes containing identifiable names
customer project files
real company documents
account or credential files
screenshots containing private data
email records
customer names when unnecessary
employee names when unnecessary
phone numbers
addresses
login information
passwords
API keys
tokens
original ERP templates containing customer data
raw Excel files from real projects
raw PDFs or PPTs from company training materials
4. Naming Policy

The original company may be referred to privately, but the public repository should use anonymized labels.

Recommended public labels:

ERP Consulting Firm A
Client N
Client U
Client E
Client G
New Employee A
Senior Consultant A
Customer Contact A
External Developer A
5. Date Handling

Exact dates may be used when they are necessary for workflow timeline analysis.

However, dates should be used to describe process sequence, not to expose confidential project details.

When exact dates are unnecessary, month-level labels may be used.

Example:

January 2023
February 2023
March 2023
6. Data Handling

Synthetic datasets should be clearly labeled.

Every synthetic file should include a data_origin field when possible.

Recommended values:

synthetic
reconstructed
anonymized_summary

Real customer data should not be mixed with synthetic data.

7. Credential and Access-Control Handling

Any material related to login IDs, passwords, security codes, account access, API credentials, or system permissions must remain private.

If such materials are analytically relevant, describe them only at a structural level.

Correct public wording:

“Access-related artifacts appeared in the onboarding material set, indicating a need for clearer separation between training files and credential governance.”

Incorrect public wording:

Directly showing credentials, accounts, URLs, codes, or identifiable access information.

8. Ethical Framing

This project analyzes workflow and onboarding structure.

It should not be written as personal revenge, public accusation, or defamation.

The public language should focus on:

onboarding design
knowledge transfer
workflow scaffolding
artifact fragmentation
role ambiguity
operational risk
CWI interpretation
9. Private Archive

Raw materials may be preserved privately for personal record, research traceability, or future non-public review.

Private materials should be stored in ignored folders such as:

raw/
private/
originals/
credentials/

These folders should be excluded through .gitignore.

10. Final Principle

The public version should preserve the structure of the case while removing the identity of the people and organizations involved.

The goal is to transform a difficult onboarding experience into a reusable workflow and knowledge-transfer case study.
