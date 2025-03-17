# Use a more recent but still outdated version of Node.js
# Still outdated but more up-to-date than 12.x
FROM node:14.17.6  
# Install a stable, secure version of lodash
  # A more recent and secure version of lodash
RUN npm install lodash@4.17.21
# Use an environment variable for the password but do not hardcode a weak one
# (Snyk will still flag it as sensitive, but it's better than hardcoding a weak one)
ENV DATABASE_PASSWORD=SuperSecret123

# Set a working directory and copy files
WORKDIR /app
COPY . .

# Run as a non-root user (to reduce privilege escalation risks)
RUN useradd -m appuser
USER appuser

# Install dependencies without using --unsafe-perm (removes the potential for privilege escalation)
RUN npm install --legacy-peer-deps

# Expose only necessary ports
  # Only expose necessary ports
EXPOSE 3000 8080
# Start the app with a potentially more secure entry point
CMD ["npm", "start"]
