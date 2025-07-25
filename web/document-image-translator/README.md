
## About This Project


This is the frontend for the Document Image Translator solution. It is built with Next.js and TypeScript, and communicates with a Python backend (see `api/lamba_entrypoint.py` and `src/` in the main project root) that provides:

---

## Live Demo

**Deployed Web App:** [https://doc-translate.hifeyinc.com](https://doc-translate.hifeyinc.com)

---

- Presigned S3 upload URLs for document images
- Upload status recording and retrieval via DynamoDB
- Document translation processing (backend logic in Python)

The backend is not included in this directory. See the main project root for backend code and deployment.

## How It Works

1. **Upload**: The frontend requests a presigned S3 URL from the backend, then uploads the image directly to S3.
2. **Status**: The frontend notifies the backend of the upload and can poll for translation status.
3. **Translation**: The backend processes the image and updates status in DynamoDB.


## Project Structure

- `src/app/` – Main Next.js app code
- `public/` – Static assets
- `package.json` – Project dependencies (Next.js 15, React 19, Tailwind CSS 4, ESLint 9, TypeScript strict)
- `tsconfig.json` – TypeScript configuration (strict mode, modern paths)

## Development

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Lint: `npm run lint`
4. Build: `npm run build`

## Backend Reference

- Python backend: see `api/lamba_entrypoint.py` and `src/` in the main project root
- Backend handles S3, DynamoDB, and translation logic

---

*Last updated: July 7, 2025*
