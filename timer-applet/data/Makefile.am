SUBDIRS = glades

serverdir = $(libdir)/matecomponent/servers
server_in_files = TimerApplet.server.in
server_DATA = $(server_in_files:.server.in=.server)

$(server_in_files): $(server_in_files:.server.in=.server.in.in) Makefile
	sed -e "s|\@LIBEXECDIR\@|$(libexecdir)|" $< > $@

schemasdir = /usr/share/glib-2.0/schemas/
schemas_in_files = org.mate.panel.applets.TimerApplet.gschema.xml.in
schemas_DATA = $(schemas_in_files:.xml.in=.xml)

pkgdata_DATA = TimerApplet.xml

EXTRA_DIST = \
	TimerApplet.server.in.in \
	$(pkgdata_DATA) \
	$(schemas_in_files)

CLEANFILES = \
	$(server_DATA) \
	$(server_in_files) \
	$(schemas_DATA)

@INTLTOOL_SERVER_RULE@
@INTLTOOL_SCHEMAS_RULE@
