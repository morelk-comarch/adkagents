export IMAGE="gcr.io/genai-app-builder/custodbtoolboximage"
export PROJECT_ID="genai-app-builder"

gcloud run deploy dbtoolbox \
 --image $IMAGE \
 --service-account toolbox-identity \
 --region us-central1 \
 --args="--tools-file=/app/tools.yaml","--address=0.0.0.0","--port=8080" \
 --allow-unauthenticated