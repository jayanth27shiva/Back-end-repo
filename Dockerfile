FROM node:12.18.1  # Outdated and vulnerable version

# Weak and hardcoded environment variable (unsafe practice)
ENV DATABASE_PASSWORD=12345  # Easily guessable password

# Working directory and copying files
WORKDIR /app
COPY . .

# Running as root (unnecessary and dangerous)
USER root

# Installing dependencies with unsafe-perm, allowing potential privilege escalation in packages
RUN npm install --unsafe-perm --legacy-peer-deps

# Exposing multiple ports (some might be unnecessary)
EXPOSE 3000 8080 9000 5000

# Using a start command that could be vulnerable to certain types of attacks
CMD ["npm", "start"]
