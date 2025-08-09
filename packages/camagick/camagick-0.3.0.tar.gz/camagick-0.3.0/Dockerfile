FROM python:3.12

ARG PACKAGE_PYPI_NAME=caspy
ARG PACKAGE_EXEC=caspy
ARG PACKAGE_SRC=/package_src
ARG PACKAGE_FROM_PIP=yes
ARG PACKAGE_FLAVOR=all,test

RUN useradd -u 9999 cthulhu && mkdir /home/cthulhu && chown cthulhu /home/cthulhu

RUN if [ -d "$PACKAGE_SRC" ]; then \
        echo "Installing from local directory: $PACKAGE_SRC" ;\
        pip install "$PACKAGE_SRC"["$PACKAGE_FLAVOR"] ;\
    elif [ "$PACKAGE_FROM_PIP" = "yes" ]; then \
        echo "Installing from pip" ;\
        pip install "$PACKAGE_PYPI_NAME"["$PACKAGE_FLAVOR"] ;\
    else \
        echo "\n  ***\n  *** Source not found at \$PACKAGE_SRC ($PACKAGE_SRC) -- failing build now. \n  ***\n" ;\
        /bin/false ;\
    fi

USER cthulhu

ENV IOC_EXEC=$PACKAGE_EXEC

ENTRYPOINT "$IOC_EXEC"
