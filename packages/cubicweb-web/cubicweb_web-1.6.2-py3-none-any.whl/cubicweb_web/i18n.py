import os

from cubicweb.cwvreg import CWRegistryStore
from cubicweb.i18n import add_msg
from cubicweb.devtools.devctl import (
    I18nCubeMessageExtractor,
    _iter_vreg_objids,
    DevConfiguration,
    clean_sys_modules,
)

from cubicweb_web.webconfig import WebAllInOneConfiguration


class WebI18nCubeMessageExtractor(I18nCubeMessageExtractor):
    def schemapot(self) -> str:
        """append uicfg related pot to the generated ``schema.pot``"""
        schemapot_path = super().schemapot()
        print("schema(cubicweb_web)", end=" ")

        # append to the existing pot file
        schemapotstream = open(schemapot_path, "a")
        generate_schema_pot(schemapotstream.write, self.cubedir)
        schemapotstream.close()

        return schemapot_path


class WebDevConfiguration(WebAllInOneConfiguration, DevConfiguration):
    pass


def generate_schema_pot(w, cubedir=None):
    """generate a pot file with schema specific i18n messages
    notice that relation definitions description and static vocabulary
    should be marked using '_' and extracted using xgettext
    """

    cube = os.path.split(cubedir)[-1]
    if cube.startswith("cubicweb_"):
        cube = cube[len("cubicweb_") :]

    # XXX Cube `web` must be installed in order for i18ncube to work as we
    # use appobjects registered by it in _generate_schema_pot.
    config = WebDevConfiguration("web", cube)
    depcubes = list(config._cubes)
    depcubes.remove(cube)
    if "web" not in depcubes:
        depcubes.insert(0, "web")
    libconfig = WebDevConfiguration(*depcubes)

    clean_sys_modules(config.appobjects_modnames())
    schema = config.load_schema(remove_unused_relation_types=False)
    vreg = CWRegistryStore(config)
    # set_schema triggers objects registrations
    vreg.set_schema(schema)
    _generate_schema_pot(w, vreg, schema, libconfig=libconfig)


def _generate_schema_pot(w, vreg, schema, libconfig=None):
    afss = vreg["uicfg"]["autoform_section"]
    aiams = vreg["uicfg"]["actionbox_appearsin_addmenu"]

    libschema = libconfig.load_schema(remove_unused_relation_types=False)
    clean_sys_modules(libconfig.appobjects_modnames())
    libvreg = CWRegistryStore(libconfig)
    libvreg.set_schema(libschema)  # trigger objects registration

    libafss = libvreg["uicfg"]["autoform_section"]
    libaiams = libvreg["uicfg"]["actionbox_appearsin_addmenu"]

    for eschema in sorted(schema.entities()):
        if eschema.final:
            continue

        for rschema, targetschemas, role in eschema.relation_definitions(True):
            if rschema.final:
                continue
            for tschema in targetschemas:
                for afs in afss:
                    fsections = afs.etype_get(eschema, rschema, role, tschema)
                    if "main_inlined" in fsections and not _is_in_lib(
                        libafss,
                        eschema,
                        rschema,
                        role,
                        tschema,
                        lambda x: "main_inlined" in x,
                    ):
                        add_msg(
                            w,
                            "add a %s" % tschema,
                            "inlined:%s.%s.%s" % (eschema.type, rschema, role),
                        )
                        add_msg(
                            w,
                            str(tschema),
                            "inlined:%s.%s.%s" % (eschema.type, rschema, role),
                        )
                        break
                for aiam in aiams:
                    if aiam.etype_get(
                        eschema, rschema, role, tschema
                    ) and not _is_in_lib(libaiams, eschema, rschema, role, tschema):
                        if role == "subject":
                            label = "add %s %s %s %s" % (
                                eschema,
                                rschema,
                                tschema,
                                role,
                            )
                            label2 = "creating %s (%s %%(linkto)s %s %s)" % (
                                tschema,
                                eschema,
                                rschema,
                                tschema,
                            )
                        else:
                            label = "add %s %s %s %s" % (
                                tschema,
                                rschema,
                                eschema,
                                role,
                            )
                            label2 = "creating %s (%s %s %s %%(linkto)s)" % (
                                tschema,
                                tschema,
                                rschema,
                                eschema,
                            )
                        add_msg(w, label)
                        add_msg(w, label2)
                        break
    vregdone = set()
    # fill vregdone with already processed registry
    list(_iter_vreg_objids(libvreg, vregdone))
    for objid in _iter_vreg_objids(vreg, vregdone):
        add_msg(w, f"{objid}_description")
        add_msg(w, objid)


def _is_in_lib(rtags, eschema, rschema, role, tschema, predicate=bool):
    return any(
        predicate(rtag.etype_get(eschema, rschema, role, tschema)) for rtag in rtags
    )
