# Deployment Guidelines

RHOS is designed to be easily deployable in containerized cloud environments like Google Cloud Run or AWS ECS.

## Docker Compose Production Run

Deploy the entire stack locally in production mode using Docker Compose:

```bash
docker-compose up --build
```

This starts:
1. **Backend**: FastAPI running inside a Python container on port `8000`.
2. **Frontend**: React client built and served by Nginx on port `3000`.

## Cloud Run Deployment (GCP)

Deploy to Google Cloud Run for a serverless, highly scalable environment.

### 1. Build and push container images
Use Google Cloud Build:

```bash
# Push Backend to Artifact Registry
gcloud builds submit --tag gcr.io/your-project-id/rhos-backend ./backend

# Push Frontend to Artifact Registry
gcloud builds submit --tag gcr.io/your-project-id/rhos-frontend ./frontend
```

### 2. Deploy Backend
Deploy the backend first, configuring API keys as environment secrets:

```bash
gcloud run deploy rhos-backend \
    --image gcr.io/your-project-id/rhos-backend \
    --platform managed \
    --region us-central1 \
    --set-env-vars="AUTH_MODE=firebase,GEMINI_API_KEY=secret_key,FIREBASE_STORAGE_BUCKET=bucket_name" \
    --allow-unauthenticated
```

### 3. Deploy Frontend
Deploy the frontend, directing requests to your backend URL:

```bash
gcloud run deploy rhos-frontend \
    --image gcr.io/your-project-id/rhos-frontend \
    --platform managed \
    --region us-central1 \
    --set-env-vars="VITE_API_URL=https://rhos-backend-xyz.a.run.app" \
    --allow-unauthenticated
```
