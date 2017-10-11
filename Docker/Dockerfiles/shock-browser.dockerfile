FROM nginx
COPY Services/ShockBrowser/js/config.js /usr/share/nginx/html/js/config.js
COPY Services/ShockBrowser/html/shockbrowse.html /usr/share/nginx/html/index.html
COPY Services/ShockBrowser/html/images /usr/share/nginx/html/images
COPY Services/Retina /usr/share/nginx/html/Retina

