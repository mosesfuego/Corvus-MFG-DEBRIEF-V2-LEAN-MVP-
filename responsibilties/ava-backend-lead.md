# Ava - Backend Lead

## Owns

- Backend architecture
- Data models
- CSV ingestion
- API structure
- Local backend run path

## Tasks

- Maintain the core production job model in `app/models/`.
- Keep CSV parsing and validation in `app/ingest/`.
- Expose simple FastAPI routes from `app/api/`.
- Make sure sample data can be loaded without manual cleanup.
- Keep backend modules small, testable, and easy to replace later.
- Document any assumptions about required CSV fields.

## Done When

- A developer can load the sample CSV and receive typed production records.
- API routes are thin and delegate business logic to the proper modules.
- Bad input fails with clear validation errors.
