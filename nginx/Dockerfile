FROM nginx

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./static /usr/share/nginx/static-files
RUN chown -R www-data:www-data /usr/share/nginx/static-files
RUN chmod -R 755 /usr/share/nginx/static-files
