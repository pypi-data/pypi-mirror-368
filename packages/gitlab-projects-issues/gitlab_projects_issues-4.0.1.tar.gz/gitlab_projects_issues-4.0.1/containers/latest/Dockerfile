ARG IMAGE_BASE=python:3-alpine
FROM $IMAGE_BASE

# Install dependencies
RUN apk add -q --no-cache  \
      coreutils

# Install package
COPY --from='dist' ./*.whl /tmp/
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 \
 && pip3 install -q --no-cache-dir --upgrade /tmp/*.whl \
 && rm -f /tmp/*.whl

 # Configure entrypoint
ENTRYPOINT []
CMD ["/bin/sh"]
