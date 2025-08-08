#!/bin/bash

# Build the Vue.js application
npm run build

# Ensure the _redirects file is in the dist directory
cp public/_redirects dist/_redirects 2>/dev/null || echo "_redirects file already exists or not needed"

# Ensure other redirect files are copied
cp public/netlify.toml dist/netlify.toml 2>/dev/null || echo "netlify.toml copied"
cp public/vercel.json dist/vercel.json 2>/dev/null || echo "vercel.json copied"

echo "Build completed with SPA redirect support"
