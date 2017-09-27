FROM nginx
COPY Services/RetinaDemo /usr/share/nginx/html
COPY Services/ShockBrowser/js/config.js /usr/share/nginx/html/js/config.js