#!/bin/bash

echo "========================================="
echo "Product Importer - Railway Deployment"
echo "========================================="
echo

# Check if npm is available for Railway CLI installation
if command -v npm >/dev/null 2>&1; then
    echo "Installing Railway CLI using npm..."
    npm install -g @railway/cli
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Railway CLI via npm"
        echo "Please install manually from: https://docs.railway.app/develop/cli"
        exit 1
    fi
else
    echo "Installing Railway CLI using curl..."
    bash <(curl -fsSL https://railway.app/install.sh)
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Railway CLI"
        echo "Please install manually from: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI installed"
echo

echo "🚀 Starting Railway deployment..."
echo

echo "Step 1: Login to Railway"
railway login
if [ $? -ne 0 ]; then
    echo "❌ Railway login failed"
    exit 1
fi

echo
echo "Step 2: Link GitHub repository (recommended)"
railway link
echo

echo "Step 3: Deploy application"
railway up
if [ $? -ne 0 ]; then
    echo "❌ Deployment failed"
    exit 1
fi

echo
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo
echo "Your app is now deployed on Railway!"
echo
echo "Next steps:"
echo "1. Check Railway dashboard for your app URL"
echo "2. Railway will auto-add PostgreSQL and Redis"
echo "3. Your webhook workers will start automatically"
echo
echo "To view your app:"
echo "  railway open"
echo
echo "To view logs:"
echo "  railway logs"
echo
echo "To add database (if not auto-added):"
echo "  railway add postgresql"
echo "  railway add redis"
echo