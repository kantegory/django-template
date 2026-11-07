FROM nginx:1.27-alpine

ENV NGINX_CLIENT_MAX_BODY_SIZE=100M \
    NGINX_ENVSUBST_FILTER=NGINX_

COPY default.conf.template /etc/nginx/templates/default.conf.template
