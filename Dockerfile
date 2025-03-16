# Use an old and unsupported version of Node.js
FROM node:12.18.1  # Deprecated Node.js version

# Vulnerable package installation (e.g., a known vulnerable version of lodash)
RUN npm install lodash@4.17.19  # Known vulnerable version of lodash

# Weak hardcoded password (this will be detected as sensitive information)
ENV DATABASE_PASSWORD=12345  # Hardcoded weak password

# Setting a working directory and copying files
WORKDIR /app
COPY . .

# Running as root (unnecessary and can cause security issues)
USER root

# Install dependencies with --unsafe-perm (vulnerable practice)
RUN npm install --unsafe-perm --legacy-peer-deps

# Expose multiple unnecessary ports, which Snyk might flag as misconfigured
EXPOSE 3000 8080 9000 5000

# Exposed start command that may trigger runtime vulnerabilities if insecure code is in place
CMD ["npm", "start"]
