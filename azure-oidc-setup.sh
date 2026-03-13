#!/bin/bash
# Pfula — Azure OIDC Setup for GitHub Actions
#
# This creates a federated credential so GitHub Actions can deploy
# to Azure without storing any secrets — just uses OIDC tokens.
#
# Prerequisites:
#   1. Azure CLI installed and logged in: az login
#   2. GitHub CLI installed and logged in: gh auth login
#
# Usage:
#   chmod +x azure-oidc-setup.sh
#   ./azure-oidc-setup.sh

set -e

# ── Configuration ──────────────────────────────────────────────
GITHUB_ORG="bytezn"           # Your GitHub org/username
GITHUB_REPO="vula"            # Your GitHub repo name
APP_NAME="pfula-github-deploy" # Azure AD app registration name
RESOURCE_GROUP="pfula-rg"
# ───────────────────────────────────────────────────────────────

echo "=================================================="
echo "  Pfula — Azure OIDC Setup for GitHub Actions"
echo "=================================================="

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo ""
echo "  Subscription: $SUBSCRIPTION_ID"
echo "  Tenant:       $TENANT_ID"

# Step 1: Create Azure AD App Registration
echo ""
echo ">> Step 1: Creating Azure AD app registration..."
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
echo "   App ID: $APP_ID"

# Step 2: Create Service Principal
echo ""
echo ">> Step 2: Creating service principal..."
SP_OBJECT_ID=$(az ad sp create --id $APP_ID --query id -o tsv)
echo "   Service Principal Object ID: $SP_OBJECT_ID"

# Step 3: Assign Contributor role on the resource group
echo ""
echo ">> Step 3: Assigning Contributor role..."
az role assignment create \
    --assignee $APP_ID \
    --role "Contributor" \
    --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}" \
    2>/dev/null || echo "   (Role assignment may already exist)"

# Step 4: Create federated credential for main branch
echo ""
echo ">> Step 4: Creating federated credential (main branch)..."
az ad app federated-credential create \
    --id $APP_ID \
    --parameters "{
        \"name\": \"github-main-branch\",
        \"issuer\": \"https://token.actions.githubusercontent.com\",
        \"subject\": \"repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/main\",
        \"audiences\": [\"api://AzureADTokenExchange\"]
    }"

# Step 5: Create federated credential for pull requests (optional but useful)
echo ""
echo ">> Step 5: Creating federated credential (pull requests)..."
az ad app federated-credential create \
    --id $APP_ID \
    --parameters "{
        \"name\": \"github-pull-requests\",
        \"issuer\": \"https://token.actions.githubusercontent.com\",
        \"subject\": \"repo:${GITHUB_ORG}/${GITHUB_REPO}:pull_request\",
        \"audiences\": [\"api://AzureADTokenExchange\"]
    }"

# Step 6: Set GitHub secrets
echo ""
echo ">> Step 6: Setting GitHub repository secrets..."
gh secret set AZURE_CLIENT_ID --body "$APP_ID" --repo "${GITHUB_ORG}/${GITHUB_REPO}"
gh secret set AZURE_TENANT_ID --body "$TENANT_ID" --repo "${GITHUB_ORG}/${GITHUB_REPO}"
gh secret set AZURE_SUBSCRIPTION_ID --body "$SUBSCRIPTION_ID" --repo "${GITHUB_ORG}/${GITHUB_REPO}"

echo ""
echo "=================================================="
echo "  OIDC Setup Complete!"
echo ""
echo "  GitHub Secrets configured:"
echo "    AZURE_CLIENT_ID:       $APP_ID"
echo "    AZURE_TENANT_ID:       $TENANT_ID"
echo "    AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
echo ""
echo "  Push to 'main' branch to trigger deployment."
echo "  No passwords or certificates stored anywhere."
echo "=================================================="
