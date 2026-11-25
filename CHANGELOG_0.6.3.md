# MedFlow ERP Foundation 0.6.3 — CRUD and draft-friendly forms

This source revision builds on the supplied 0.6.2 archive.

## Changes
- Added edit/delete actions for CRM opportunities, counterparties, equipment, contacts, cost lines, and tasks; commercial offers already supported edit/delete.
- Added backend delete endpoints and safe conflict responses when a record is still referenced by other records.
- Added contact editing/deletion endpoints and a Contacts tab.
- Marked key required fields in the UI and clarified that optional data can be filled later.
- Made commercial-offer unit price and cost-line amount default to zero so an initial record can be saved before the exact amount is known.
- Docker Compose default image tag is now 0.6.3.

## Important
- The `.env` file is intentionally excluded from this package. Create your own from `.env.example`; never share or commit secrets.
- The demo accounts/password are still present in this MVP. Do not enter real customer data or expose the demo instance to unrestricted public access.
- Database schema was not changed; this revision is intended to use the existing PostgreSQL volume.

## Build and publish
Build the new image from the project root and push it to your Docker Hub namespace with tag `0.6.3`. Then update the VPS compose image to `mmaxa/medflow-erp:0.6.3` and recreate only the app service. Keep the PostgreSQL container and named volume.
