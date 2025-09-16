# Agent Builder - GitHub Actions Secrets Guide

This document lists all the secrets you need to configure in your GitHub repository for the CI/CD pipeline to work.

## Required Secrets

Navigate to your repository → Settings → Secrets and variables → Actions → New repository secret

### Docker Hub Secrets

```
Name: DOCKER_USERNAME
Value: your-dockerhub-username

Name: DOCKER_PASSWORD  
Value: your-dockerhub-password-or-access-token
```

**Note**: It's recommended to use Docker Hub access tokens instead of passwords. Generate one at: Docker Hub → Account Settings → Security → Access Tokens

### Digital Ocean Secrets

```
Name: DIGITALOCEAN_ACCESS_TOKEN
Value: your-digitalocean-api-token
```
Generate at: DigitalOcean → API → Personal Access Tokens

```
Name: DIGITALOCEAN_SSH_PRIVATE_KEY
Value: your-private-ssh-key-content
```
This should be the content of your private SSH key (the one you use to connect to your droplet)

```
Name: DIGITALOCEAN_SERVER_IP
Value: your-droplet-ip-address
```
The IP address of your Digital Ocean droplet

### Application Secrets (Optional)

```
Name: REACT_APP_API_URL
Value: https://yourdomain.com
```
The public URL where your API will be accessible

## Setting Up SSH Key

1. **Generate SSH Key** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@yourdomain.com"
   ```

2. **Add Public Key to Digital Ocean**:
   ```bash
   # Copy public key
   cat ~/.ssh/id_rsa.pub
   
   # Add to Digital Ocean → Settings → Security → SSH Keys
   ```

3. **Add Private Key to GitHub Secrets**:
   ```bash
   # Copy entire private key content including headers
   cat ~/.ssh/id_rsa
   
   # Add as DIGITALOCEAN_SSH_PRIVATE_KEY secret
   ```

## Docker Hub Setup

1. **Create Repositories**:
   - Log into Docker Hub
   - Create repository: `yourusername/agentbuilder-backend`  
   - Create repository: `yourusername/agentbuilder-frontend`

2. **Update Workflow File**:
   Edit `.github/workflows/ci-cd.yml` and update the image names:
   ```yaml
   env:
     BACKEND_IMAGE_NAME: yourusername/agentbuilder-backend
     FRONTEND_IMAGE_NAME: yourusername/agentbuilder-frontend
   ```

## Digital Ocean API Token

1. Go to DigitalOcean → API
2. Click "Generate New Token"
3. Choose "Full Access" for deployment capabilities
4. Copy the token and add as `DIGITALOCEAN_ACCESS_TOKEN` secret

## Environment Variables on Server

Make sure your server has the correct environment variables in `/opt/agent-builder/.env`:

```env
# Database
POSTGRES_PASSWORD=your-secure-database-password

# API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-ai-key
SERPAPI_KEY=your-serpapi-key

# Security
SECRET_KEY=your-32-character-secret-key

# Domain Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REACT_APP_API_URL=https://yourdomain.com
```

## Testing the Pipeline

1. **Push to main branch** to trigger the deployment
2. **Check Actions tab** in GitHub to monitor progress  
3. **Verify deployment** by visiting your domain

## Troubleshooting

### Common Issues

**SSH Connection Failed**:
- Verify SSH key is correctly added to GitHub secrets
- Ensure public key is added to your droplet
- Check server IP address is correct

**Docker Push Failed**:
- Verify Docker Hub credentials
- Check repository names match your Docker Hub repositories
- Ensure repositories are public or you have push permissions

**Deployment Failed**:
- Check server has Docker and docker-compose installed
- Verify environment variables are set on server
- Check disk space and memory on server

### Debug Commands

```bash
# On GitHub Actions runner (add to workflow for debugging)
- name: Debug SSH
  run: |
    echo "${{ secrets.DIGITALOCEAN_SSH_PRIVATE_KEY }}" | wc -l
    ssh -o StrictHostKeyChecking=no root@${{ secrets.DIGITALOCEAN_SERVER_IP }} "echo 'Connected successfully'"

# On your server
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
df -h
free -m
```

## Security Best Practices

1. **Use SSH Keys**: Never use passwords for SSH access
2. **Rotate Tokens**: Regularly rotate API tokens and access keys  
3. **Principle of Least Privilege**: Only grant necessary permissions
4. **Monitor Access**: Regularly check DigitalOcean access logs
5. **Backup Keys**: Keep secure backups of your SSH keys

---

After configuring all secrets, your GitHub Actions pipeline will automatically build, test, and deploy your application whenever you push to the main branch.