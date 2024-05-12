FROM homeassistant/home-assistant:dev

ENV DEVCONTAINER=true

COPY ./container /container
COPY ./install /install

RUN \
    bash /install/init.sh \
    && bash /install/container.sh \
    && bash /install/cleanup.sh

CMD ["bash"]
