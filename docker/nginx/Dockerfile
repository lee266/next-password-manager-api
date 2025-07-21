FROM ubuntu:22.04 as builder

ENV NGINX_VERSION=1.27.2

# Install dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    git \
    libbrotli-dev \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    libzstd1 \
    libzstd-dev \
    make \
    openssl \
    wget \
    zlib1g \
    zlib1g-dev \
    # && apt-get clean \  ※check: /etc/apt/apt.conf.d/docker-clean
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download and extract nginx source
RUN wget -q https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -zxf nginx-${NGINX_VERSION}.tar.gz \
    && rm nginx-${NGINX_VERSION}.tar.gz

# Clone ngx_brotli and zstd-nginx-module sources
# RUN git clone --depth=1 --recurse-submodules https://github.com/google/ngx_brotli \
#     && git clone --depth=1 --recurse-submodules https://github.com/tokers/zstd-nginx-module

# Build ngx_brotli and zstd-nginx-module
# RUN cd nginx-${NGINX_VERSION} \
#     && ./configure --with-compat \
#         --add-dynamic-module=../ngx_brotli \
#         --add-dynamic-module=../zstd-nginx-module \
#     && make modules

FROM nginx:latest

# COPY --from=builder /app/nginx-${NGINX_VERSION}/objs/ngx_http_brotli_static_module.so /etc/nginx/modules/
# COPY --from=builder /app/nginx-${NGINX_VERSION}/objs/ngx_http_brotli_filter_module.so /etc/nginx/modules/
# COPY --from=builder /app/nginx-${NGINX_VERSION}/objs/ngx_http_zstd_static_module.so /etc/nginx/modules/
# COPY --from=builder /app/nginx-${NGINX_VERSION}/objs/ngx_http_zstd_filter_module.so /etc/nginx/modules/

# main setting
COPY config/nginx.conf /etc/nginx/nginx.conf
# default setting
# COPY ./config/default.conf /etc/nginx/conf.d/default.conf
# ssl setting
# COPY ./config/ssl.conf /etc/nginx/conf.d/ssl.conf
# virtual host setting
# COPY ./config/virtual_host.conf /etc/nginx/conf.d/virtual_host.conf

EXPOSE 80