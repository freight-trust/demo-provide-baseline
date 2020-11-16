FROM node:14-alpine

WORKDIR /deployer

RUN apk update && \
  apk add --no-cache git bash make gcc g++ python3 zip rsync && \
  mkdir contract && \
  chown -R node /deployer

USER root

ENV NPM_CONFIG_PREFIX=/home/root/.npm-global
ENV PATH=/home/root/.npm-global/bin:$PATH

RUN npm install --global --verbose \
  chai \
  mocha \
  pino \
  pino-pretty \
  md5 \
  truffle \
  @truffle/hdwallet-provider \
  aws-sdk \
  lodash \
  @babel/core@^7.0.0-0

COPY ./ ./

ENTRYPOINT ["/deployer/docker/entrypoint.sh"]

CMD ["-d"]
