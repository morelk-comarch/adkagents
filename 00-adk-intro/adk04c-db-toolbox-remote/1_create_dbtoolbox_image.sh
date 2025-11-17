export IMAGE=gcr.io/genai-app-builder/custodbtoolboximage
gcloud builds submit --tag $IMAGE .