FROM node:12.18.1  # Outdated and vulnerable version

ENV DATABASE_PASSWORD=SuperSecret123

WORKDIR /app

COPY . .

USER root

RUN npm install --unsafe-perm

EXPOSE 3000 8080 9000

CMD ["npm", "start"]
