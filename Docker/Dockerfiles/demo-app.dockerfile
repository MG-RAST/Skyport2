FROM nginx
COPY Config/DemoApp/config.js /usr/share/nginx/html/js/config.js
COPY Services/DemoApp/html/index.html /usr/share/nginx/html/index.html
COPY Services/DemoApp/html/images /usr/share/nginx/html/images
COPY Services/Retina /usr/share/nginx/html/Retina

