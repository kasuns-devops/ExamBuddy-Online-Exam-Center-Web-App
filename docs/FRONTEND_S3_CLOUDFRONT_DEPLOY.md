# Frontend Deployment (Recommended): S3 + CloudFront

This is the best deployment option for this Vite/React frontend: cheaper, faster, and simpler than containers.

## 1) One-time AWS setup

- Create an S3 bucket for frontend artifacts (for example `exambuddy-frontend-prod`).
- Create a CloudFront distribution with this S3 bucket as origin.
- Configure CloudFront for SPA routing:
  - **Default root object**: `index.html`
  - **Custom error responses**:
    - `403` -> `/index.html` (HTTP 200)
    - `404` -> `/index.html` (HTTP 200)

## 2) Configure frontend production env

In `frontend`, copy:

- `.env.production.example` -> `.env.production.local`

Then update these values:

- `VITE_API_URL`
- `VITE_COGNITO_REDIRECT_URI`
- `VITE_COGNITO_LOGOUT_URI`
- Cognito values if needed

## 3) Deploy using script (Windows PowerShell)

From repo root:

```powershell
.\infrastructure\deploy-frontend-s3.ps1 -BucketName exambuddy-frontend-prod -DistributionId E1234567890ABC -Region eu-north-1
```

Optional profile:

```powershell
.\infrastructure\deploy-frontend-s3.ps1 -BucketName exambuddy-frontend-prod -DistributionId E1234567890ABC -Region eu-north-1 -AwsProfile default
```

## 4) What the script does

- Runs `npm ci`
- Builds production bundle (`npm run build:prod`)
- Uploads assets to S3 with long cache headers
- Uploads `index.html` with no-cache headers
- Invalidates CloudFront (`/*`) when distribution id is provided

## 5) Verify

- Open your CloudFront domain
- Refresh once (hard refresh)
- Log in through Cognito and confirm API calls go to `VITE_API_URL`

## 6) Notes

- No Docker needed for frontend on this path.
- Keep `.env.production.local` out of git (already ignored by `*.local`).

## 7) GitHub Actions deployment

A workflow is added at:

- `.github/workflows/deploy-frontend-s3.yml`

Configured bucket:

- `exambuddy-front`

Trigger behavior:

- Runs on push to `main` when `frontend/**` changes
- Can also be run manually via **workflow_dispatch**

Required repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `VITE_API_URL`
- `VITE_COGNITO_USER_POOL_ID`
- `VITE_COGNITO_CLIENT_ID`
- `VITE_COGNITO_REGION`
- `VITE_COGNITO_DOMAIN`
- `VITE_COGNITO_REDIRECT_URI`
- `VITE_COGNITO_LOGOUT_URI`
- `CLOUDFRONT_DISTRIBUTION_ID` (optional, for cache invalidation)
