FROM nginx:1.25-alpine

# Удаляем ВСЕ существующие конфиги
RUN rm -f /etc/nginx/conf.d/*.conf
RUN rm -f /etc/nginx/nginx.conf

# Копируем наш полный nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Создаем необходимые директории
RUN mkdir -p /app/staticfiles /var/cache/nginx
RUN chown -R nginx:nginx /app/staticfiles /var/cache/nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]