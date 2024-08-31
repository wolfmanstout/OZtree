FROM python:3.10-alpine as compile_web2py

RUN apk --update --no-cache add autoconf automake curl g++ gcc git linux-headers make nasm nodejs npm openssh-client optipng perl ruby ruby-ffi zlib-dev
RUN gem install compass --no-document
RUN npm_config_unsafe_perm=true npm install -g grunt-cli sass

WORKDIR /opt/tmp
RUN git clone --recursive https://github.com/web2py/web2py.git --depth 1 --branch v2.27.1 --single-branch web2py
WORKDIR /opt
ENV WEB2PY_MIN=1
RUN if [ "${WEB2PY_MIN}" == true ]; then \
      cd tmp/web2py; \
      python3 scripts/make_min_web2py.py ../../tmp/web2py-min; \
      mv ../../tmp/web2py-min ../../web2py; \
      cd ../../; \
    else \
      mv tmp/web2py web2py; \
    fi; \
    rm -rf tmp
WORKDIR web2py/applications
COPY . OZtree
WORKDIR OZtree
RUN cp _COPY_CONTENTS_TO_WEB2PY_DIR/routes.py ../../
COPY --from=us-central1-docker.pkg.dev/onezoom-433004/my-docker-repo/oztree-with-iucn /opt/web2py/applications/OZtree/private/appconfig.ini /opt/web2py/applications/OZtree/private/appconfig.ini
# install node modules outside of current dir, so they aren't copied over
RUN mkdir /tmp/node_modules && ln -s /tmp/node_modules ./node_modules
RUN npm install
# Compile dev instead of prod to avoid pyc compatibility issues.
RUN grunt dev

FROM us-central1-docker.pkg.dev/onezoom-433004/my-docker-repo/oztree-with-iucn
RUN rm -rf /opt/web2py/applications/* && find /opt/web2py -mindepth 1 -maxdepth 1 ! -name 'applications' -exec rm -rf {} +
RUN echo "Contents after rm: " $(ls -l -R /opt/web2py | wc -l)
COPY --from=compile_web2py /opt/web2py /opt/web2py
RUN rm -f /opt/web2py/applications/OZtree/databases/*.table
COPY --from=us-central1-docker.pkg.dev/onezoom-433004/my-docker-repo/oztree-with-iucn /opt/web2py/applications/OZtree/databases/*.table /opt/web2py/applications/OZtree/databases/
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY uwsgi.runit /etc/service/uwsgi/run
RUN chmod 777 /etc/service/uwsgi/run
RUN /sbin/my_init & \
    ( \
      until curl -N -i -s -L http://localhost/OZtree | head -n 1  | cut -d ' ' -f2 | grep -q 200; \
      do \
        sleep 10; \
        echo 'Waiting for server to update database schema... '; \
      done; \
      echo 'Schema updated.'; \
    )
CMD tail -F /tmp/uwsgi.log >>/var/log/uwsgi/uwsgi.log & \
    ( \
      until curl -N -i -s -L http://localhost/OZtree | head -n 1  | cut -d ' ' -f2 | grep -q 200; \
      do \
        sleep 10; \
        echo 'Waiting for server... '; \
      done; \
      echo 'Server active.'; \
    ) & \
    exec /sbin/my_init
