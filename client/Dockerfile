FROM node:16.14

WORKDIR /app

COPY . /app

RUN yarn global add serve

RUN yarn && yarn build

EXPOSE 3000

ENTRYPOINT ["serve", "-l", "3000", "-s", "build", "--cors"]

# developmenet
# ENTRYPOINT ["yarn", "start"]
