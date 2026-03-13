#!/bin/bash
# Pfula — Azure Container Apps Deployment (alternative to App Service)
# Uses Azure Container Apps for a more modern, scalable deployment
#
# Prerequisites:
#   1. Azure CLI installed with containerapp extension
#   2. Docker installed locally
#   3. Logged in: az login
#
# Usage:
#   chmod +x azure-container-deploy.sh
#   ./azure-container-deploy.sh

set -e

# Configuration
RESOURCE_GROUP="pfula-rg"
LOCATION="southafricanorth"
ACR_NAME="pfuaacr"  # Azure Container Registry (must be globally unique)
APP_NAME="pfula-app"
ENV_NAME="pfula-env"

echo "=================================================="
echo "  Pfula — Azure Container Apps Deployment"
echo "=================================================="

# Install containerapp extension if needed
az extension add --name containerapp --upgrade 2>/dev/null || true

# Create resource group
echo ""
echo ">> Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo ""
echo ">> Creating container registry: $ACR_NAME..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Build and push image
echo ""
echo ">> Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image pfula:latest \
    .

# Get ACR credentials
ACR_SERVER="${ACR_NAME}.azurecr.io"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Create Container Apps environment
echo ""
echo ">> Creating Container Apps environment..."
az containerapp env create \
    --name $ENV_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Deploy container app
echo ""
echo ">> Deploying container app..."
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --image "${ACR_SERVER}/pfula:latest" \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "HOST=0.0.0.0" "PORT=8000" "ENV=production"

# Get the app URL
APP_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "=================================================="
echo "  Deployment complete!"
echo ""
echo "  App URL: https://${APP_URL}"
echo ""
echo "  Set your Anthropic API key:"
echo "  az containerapp update \\"
echo "    --name $APP_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --set-env-vars ANTHROPIC_API_KEY=your-key-here"
echo "=================================================="
