# 🔒 Security Guide for OpenSearch Demos

## Overview

This security guide is essential for all users of the OpenSearch Demos project, including developers, data engineers, ML engineers, and DevOps teams working with managed OpenSearch services.

## ⚠️ NEVER Commit Sensitive Data

This repository contains demo notebooks that require authentication credentials. **NEVER** commit actual credentials to version control.

### 🚨 What NOT to Commit:
- AstraCS tokens (`AstraCS:xxxxx...`)
- Server endpoints/hostnames
- API keys or passwords
- Any personally identifiable information

### ✅ Secure Configuration Methods:

#### Method 1: Environment Variables (Recommended)
1. Copy `.env.template` to `.env`
2. Fill in your actual values in `.env`
3. The `.env` file is automatically ignored by git

#### Method 2: Runtime Configuration
Set environment variables in your shell before running notebooks:
```bash
export OPENSEARCH_HOST="your-cluster-endpoint.astra.datastax.com"
export ASTRA_CS_TOKEN="AstraCS:your-token-here"
export OPENSEARCH_PORT="9200"
```

### 🔄 Token Management:
- **Rotate tokens regularly** (every 30-90 days)
- **Revoke compromised tokens immediately**
- **Use separate tokens for different environments**

### 🚨 If You Accidentally Commit Credentials:

1. **Immediately revoke the exposed token** at astra.com
2. **Clean the git history** using tools like BFG Repo-Cleaner
3. **Generate new credentials**
4. **Force push the cleaned history** (if working with remotes)

### 📚 Additional Resources:
- [Git Secrets Prevention](https://git-secret.io/)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)