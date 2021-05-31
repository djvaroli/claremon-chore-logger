# build stage - here we build the actual frontend app
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN yarn install
COPY . .
RUN yarn build

# production stage - set up nginx as the web-server and run the start script
FROM nginx:stable-alpine as production-build
COPY --from=build-stage /app/dist /usr.share/nginx/html
CMD ["/scripts/start.sh"]