# Vulnerable Dockerfile
FROM node:12.18.1  # Outdated and vulnerable version

# Hardcoded sensitive data
ENV DATABASE_PASSWORD=SuperSecret123

WORKDIR /app

COPY . .

# Running as root user (unsafe)
USER root

# Insecure package installation
RUN npm install --unsafe-perm

# Exposing excessive and unnecessary ports
EXPOSE 3000 8080 9000

CMD ["npm", "start"]
