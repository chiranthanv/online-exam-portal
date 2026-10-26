# Requirements traceability — all 35 SRS requirements

The authoritative sources are the committed SRS/SAD/Test Plan PDFs. Status distinguishes backend execution from full team acceptance. Test implementation: `backend/portal/tests/test_api.py` and `test_postgres.py`. Execution details: [SPRINT1_REPORT.md](SPRINT1_REPORT.md).

| Requirement | Stories | Status | Evidence / planned verification |
|---|---|---|---|
| OEP-F-001 | #1 | Backend automated tests pass; React/system acceptance pending | login/hash/role/cookie; unknown credentials |
| OEP-F-002 | #1 | Backend automated tests pass; React/system acceptance pending | five failures; expiry; success reset; PostgreSQL parallel failures |
| OEP-F-003 | #2 | Backend automated tests pass; React/system acceptance pending | all-admin-route JWT role matrix |
| OEP-F-004 | #3 | Backend automated tests pass; React/system acceptance pending | single use/expiry/old-link invalidation/revocation/SMTP rollback |
| OEP-F-005 | #4 | Backend automated tests pass; React/system acceptance pending | question CRUD/options/marks/in-use/partial-update tests |
| OEP-F-006 | #5 | Backend automated tests pass; React/system acceptance pending | combined filter and invalid difficulty tests |
| OEP-F-007 | #10 | Sprint 1 API subset passes; future attempt paths and browser pending | Role matrix and available-exam response contains no options/keys |
| OEP-F-008 | #7 | Backend automated tests pass; React/system acceptance pending | exam schedule/partial validation/read-only totals/freeze |
| OEP-F-009 | #8 | Backend automated tests pass; React/system acceptance pending | manual order/random mix/insufficient pool rollback/concurrent selection |
| OEP-F-010 | #9 | Backend automated tests pass; React/system acceptance pending | atomic assignment replacement tests |
| OEP-F-011 | #6 | Backend automated tests pass; React/system acceptance pending | CSV/XLSX/row errors/duplicates/formulas/limits |
| OEP-F-012 | #6 | Backend automated tests pass; React/system acceptance pending | batch create/membership/idempotence/atomic invalid IDs |
| OEP-F-013 | #9 | Backend automated tests pass; React/system acceptance pending | assigned/unassigned/time boundary/dedup/empty-exam tests |
| OEP-F-014 | #11 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-015 | #12 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-016 | #13 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-017 | #14 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-018 | #15 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-019 | #16 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-020 | #17 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-021 | #17 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-F-022 | #18 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-001 | #21 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-002 | #21 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-003 | #22 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-004 | #12 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-005 | #23 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-NF-006 | #24 | Current backend coverage measured; unimplemented exam/evaluation engine acceptance pending | coverage report and CI artifact; see SPRINT1_REPORT.md |
| OEP-SR-001 | #1 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-002 | #19 | TLS/container CI evidence recorded in report; integrated/public deployment pending | scripts/tls_smoke.py verifies CA/hostname/TLS 1.2/Secure/HttpOnly/HSTS |
| OEP-SR-003 | #10 | Sprint 1 API subset passes; future attempt paths and browser pending | Role matrix and available-exam response contains no options/keys |
| OEP-SR-004 | #2 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-005 | #11 | Planned — Sprint 2; not implemented/tested | Future implementation and execution required |
| OEP-SR-006 | #17 | Question/admin audit subset passes; Sprint 2 overrides pending | Audit events; ORM and raw SQL UPDATE/DELETE rejection |
| OEP-SR-007 | #20 | Backend validation/ORM tests pass; browser stored-XSS/system tests pending | Injection-as-data, parameterized filters, input/import validation |
