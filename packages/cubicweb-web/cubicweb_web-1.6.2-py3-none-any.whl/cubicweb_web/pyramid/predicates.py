from cubicweb._exceptions import UnknownEid


class HasCWPermissionRoutePredicate:
    """A route predicate that matches if the current user has given permission
    on the entity given by its eid, using cubicweb.predicates.has_permission.

    The main purpose of this predicate is to restrain access on specific pages,
    based on the permission of the current user.
    """

    def __init__(self, permission, config):
        self.permission = permission

    def text(self):
        return f"has_cw_permission = {self.permission}"

    phash = text

    def __call__(self, info, request):
        eid = self._get_eid(info, request)
        if not eid:
            return False

        if request.cw_cnx is None:
            return False

        try:
            entity = request.cw_cnx.entity_from_eid(eid)
        except UnknownEid:
            return False

        return entity.cw_has_perm(self.permission)

    def _get_eid(self, info, request):
        try:
            eid = int(info["match"]["eid"])
        except (KeyError, ValueError):
            return None
        return eid


class HasCWPermissionViewPredicate(HasCWPermissionRoutePredicate):
    """This predicate is quite the same as its route pendant, but for
    view.

    The main purpose of this predicate is to have different views for a
    single route, but with different features according to current user
    permissions on the entity.
    """

    def _get_eid(self, info, request):
        try:
            eid = int(request.matchdict["eid"])
        except (KeyError, ValueError):
            return None
        return eid


def includeme(config):
    config.add_route_predicate("has_cw_permission", HasCWPermissionRoutePredicate)
    config.add_view_predicate("has_cw_permission", HasCWPermissionViewPredicate)
