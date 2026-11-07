#!/usr/bin/env bash
# Quick deployment helper for Vercel

echo "======================================================="
echo "🚀 DEPLOYING LUMINARY NEURO-IQ TO VERCEL"
echo "======================================================="

# Check if Vercel CLI is installed
if command -v vercel &> /dev/null; then
    echo "Deploying via Vercel CLI..."
    vercel --prod
elif command -v npx &> /dev/null; then
    echo "Deploying via npx vercel..."
    npx vercel --prod
else
    echo "Vercel CLI not found locally. You have two instant options:"
    echo ""
    echo "👉 OPTION 1 (Recommended - 1-Click via GitHub):"
    echo "   1. Create a repo on GitHub: https://github.com/new"
    echo "   2. Run:"
    echo "      git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "      git push -u origin main"
    echo "   3. Go to https://vercel.com/new, click 'Import', and click 'Deploy'!"
    echo ""
    echo "👉 OPTION 2 (Install Vercel CLI):"
    echo "   npm install -g vercel"
    echo "   vercel"
    echo "======================================================="
fi

