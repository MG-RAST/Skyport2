FROM nginx
COPY Services/RetinaDemo /usr/share/nginx/html
COPY Services/RetinaDemo/index.html /usr/share/nginx/html/demos.html
COPY Services/ShockBrowser/js/config.js /usr/share/nginx/html/js/config.js
COPY Services/ShockBrowser/html/shockbrowse.html /usr/share/nginx/html/index.html
COPY data/pictures/donkey.jpg /usr/share/nginx/html/images/MGRAST_logo.png

