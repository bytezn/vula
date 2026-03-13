#!/bin/bash
# Pfula — Azure App Service Deployment Script
# Deploys to Azure App Service using Azure CLI
#
# Prerequisites:
#   1. Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
#   2. Logged in: az login
#   3. Set your API key in Azure after deployment
#
# Usage:
#   chmod +x azure-deploy.sh
#   ./azure-deploy.sh

set -e

# Configuration — change these to match your Azure setup
RESOURCE_GROUP="pfula-rg"
APP_NAME="pfula-app"
LOCATION="southafricanorth"  # Azure South Africa North (Johannesburg)
SKU="B1"                     # Basic tier — sufficient for demo

echo "=================================================="
echo "  Pfula — Azure Deployment"
echo "  AI That Opens Government for Every South African"
echo "=================================================="

# Create resource group
echo ""
echo ">> Creating resource group: $RESOURCE_GROUP in $LOCATION..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan
echo ""
echo ">> Creating App Service plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux

# Create web app
echo ""
echo ">> Creating web app: $APP_NAME..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --name $APP_NAME \
    --runtime "PYTHON:3.11"

# Configure startup command
echo ""
echo ">> Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "python run.py"

# Set environment variables
echo ""
echo ">> Setting app configuration..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        HOST=0.0.0.0 \
        PORT=8000 \
        ENV=production \
        WEBSITES_PORT=8000

# Deploy the code
echo ""
echo ">> Deploying code..."
az webapp up \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --runtime "PYTHON:3.11"

echo ""
echo "=================================================="
echo "  Deployment complete!"
echo ""
echo "  App URL: https://${APP_NAME}.azurewebsites.net"
echo ""
echo "  IMPORTANT: Set your Anthropic API key:"
echo "  az webapp config appsettings set \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --name $APP_NAME \\"
echo "    --settings ANTHROPIC_API_KEY=your-key-here"
echo ""
echo "  Without the API key, the app runs in demo mode"
echo "  with pre-crafted responses (perfect for the stage demo)."
echo "=================================================="
