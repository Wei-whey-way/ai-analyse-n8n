FROM docker.n8n.io/n8nio/n8n:latest

# Set environment variables (optional)
ENV GENERIC_TIMEZONE="Asia/Singapore"
ENV TZ="Asia/Singapore"
ENV N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
ENV N8N_RUNNERS_ENABLED=true

# Expose n8n port
EXPOSE 5678

# n8n already has an ENTRYPOINT that runs n8n automatically
