# FIXME: VID_BY_MIMETYPE is unfortunately a bit too naive since
#        some browsers (e.g. FF2) send a bunch of mimetypes in
#        the Accept header, for instance:
#          text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,
#          text/plain;q=0.8,image/png,*/*;q=0.5
VID_BY_MIMETYPE = {
    # 'text/xml': 'xml',
    # XXX rss, owl...
}


# this constant is exported to an external module to avoid bugs where the
# backward compatibility in CubicWeb does a lot of import and we end up with
# multiple instances of VID_BY_MIMETYPE while we only want one
