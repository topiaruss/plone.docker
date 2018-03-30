FROM python:2.7-slim-stretch

ENV PLONE_MAJOR=4.3 \
    PLONE_VERSION=4.3.15 \
    PLONE_MD5=c3ce5488684d4204d64668de7977a1e2

LABEL plone=$PLONE_VERSION \
    os="debian" \
    os.version="9" \
    name="Plone 4.3" \
    description="Plone image, based on Unified Installer" \
    maintainer="Plone Community"

RUN useradd --system -m -d /plone -U -u 500 plone \
 && mkdir -p /plone/instance/

COPY requirements.txt /plone/instance/

RUN buildDeps="wget gcc libc6-dev libpcre3-dev libxml2-dev libxslt1-dev zlib1g-dev" \
 && runDeps="gosu libxml2 libxslt1.1 poppler-utils wv" \
 && apt-get update \
 && apt-get install -y --no-install-recommends $buildDeps \
 && pip install zc.buildout \
 && wget -O Plone.tgz https://launchpad.net/plone/$PLONE_MAJOR/$PLONE_VERSION/+download/Plone-$PLONE_VERSION-UnifiedInstaller.tgz \
 && echo "$PLONE_MD5 Plone.tgz" | md5sum -c - \
 && tar -xzf Plone.tgz \
 && mkdir /Plone-buildout/ \
 && cp -rv ./Plone-$PLONE_VERSION-UnifiedInstaller/base_skeleton/* /Plone-buildout/ \
 && cp -v ./Plone-$PLONE_VERSION-UnifiedInstaller/buildout_templates/buildout.cfg /Plone-buildout/ \
 && cd /Plone-buildout \
 && buildout annotate | sed -n -e '1,/^\[versions\]$/d' -e '/^\[/,$d' -e '/^ /d' -e 's/= /==/' -e 'p' > /plone/instance/constraints.txt \
 && cd /plone/instance \
 && sed -i "s|setuptools=27.3.0||g" constraints.txt \
 && sed -i "s|zc.buildout=2.5.3||g" constraints.txt \
 && pip install -r requirements.txt \
 && apt-get purge -y --auto-remove $buildDeps \
 && apt-get install -y --no-install-recommends $runDeps \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /Plone* \
 && chown -R plone:plone /plone \
 && cd /plone/instance \
 && gosu plone mkzopeinstance -d . -u admin:admin


VOLUME /data

COPY docker-initialize.py docker-entrypoint.sh /

EXPOSE 8080
WORKDIR /plone/instance

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["fg"]
