# copyright 2003-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.

from yams.buildobjs import (
    EntityType,
    RelationDefinition,
    ComputedRelation,
    SubjectRelation,
    String,
    Int,
    Datetime,
    Boolean,
    Float,
    TZDatetime,
    Bytes,
    RichString,
)
from yams.constraints import IntervalBoundConstraint

from cubicweb import _
from cubicweb.schema import (
    RRQLExpression,
    RQLConstraint,
    RQLVocabularyConstraint,
    WorkflowableEntityType,
)


def rperms(var, read=("managers", "users")):
    return {
        "read": read,
        "add": ("managers", RRQLExpression(f"U has_update_permission {var}")),
        "delete": (
            "managers",
            RRQLExpression(f"U has_delete_permission {var}"),
        ),
    }


class Salesterm(EntityType):
    described_by_test = SubjectRelation(
        "File", cardinality="1*", composite="subject", inlined=True
    )
    amount = Int(constraints=[IntervalBoundConstraint(minvalue=0, maxvalue=100)])
    reason = String(maxsize=20, vocabulary=["canceled", "sold"])


class tags(RelationDefinition):
    subject = "Tag"
    object = ("BlogEntry", "CWUser", "Ami", "Personne", "Note")


class checked_by(RelationDefinition):
    subject = "BlogEntry"
    object = "CWUser"
    cardinality = "?*"
    __permissions__ = {
        "add": ("managers",),
        "read": ("managers", "users"),
        "delete": ("managers",),
    }


class Personne(EntityType):
    __permissions__ = {
        "read": ("managers", "users", "guests"),
        "add": (
            "managers",
            "validators",
            "users",
        ),
        "update": (
            "managers",
            "validators",
            "owners",
        ),
        "delete": (
            "managers",
            "validators",
            "owners",
        ),
    }
    nom = String(fulltextindexed=True, required=True)
    prenom = String(fulltextindexed=True)
    type = String()
    sexe = String(
        maxsize=1,
        default="M",
        __permissions__={
            "read": (
                "managers",
                "users",
                "guests",
            ),
            "add": ("managers", "users"),
            "update": ("managers",),
        },
    )
    promo = String(vocabulary=("bon", "pasbon"))
    titre = String(fulltextindexed=True, maxsize=128)
    ass = String(maxsize=128)
    web = String(maxsize=128)
    tel = Int()
    fax = Int()
    datenaiss = Datetime()
    tzdatenaiss = TZDatetime()
    test = Boolean()
    description = String()
    salary = Float()
    travaille = SubjectRelation("Societe")
    tags = SubjectRelation("BlogEntry")
    evaluee = SubjectRelation(("Note", "Personne"))
    connait = SubjectRelation(
        "Personne",
        symmetric=True,
        constraints=[
            RQLConstraint("NOT S identity O"),
            # conflicting constraints, see cw_unrelated_rql tests in
            # unittest_entity.py
            RQLVocabularyConstraint('NOT (S connait P, P nom "toto")'),
            RQLVocabularyConstraint('S travaille P, P nom "tutu"'),
        ],
    )
    actionnaire = SubjectRelation(
        "Societe",
        cardinality="??",
        constraints=[RQLConstraint("NOT EXISTS(O contrat_exclusif S)")],
    )
    dirige = SubjectRelation(
        "Societe", cardinality="??", constraints=[RQLConstraint("S actionnaire O")]
    )
    associe = SubjectRelation(
        "Personne",
        cardinality="?*",
        constraints=[RQLConstraint("S actionnaire SOC, O actionnaire SOC")],
    )


class connait(RelationDefinition):
    subject = "CWUser"
    object = "Personne"


class Societe(EntityType):
    nom = String(fulltextindexed=True)
    web = String(maxsize=128)
    type = String(maxsize=128)  # attribute in common with Note
    tel = Int()
    fax = Int()
    rncs = String(maxsize=128)
    ad1 = String(maxsize=128)
    ad2 = String(maxsize=128)
    ad3 = String(maxsize=128)
    cp = String(maxsize=12)
    ville = String(maxsize=32)
    evaluee = SubjectRelation("Note")
    fournit = SubjectRelation(("Service", "Produit"), cardinality="1*")
    contrat_exclusif = SubjectRelation("Personne", cardinality="??")


# enough relations to cover most reledit use cases
class Project(EntityType):
    __permissions__ = {
        "read": ("managers", "users", "guests"),
        "add": ("managers", "validators", "contributors"),
        "update": ("managers", "validators", "contributors"),
        "delete": ("managers", "owners"),
    }
    title = String(maxsize=32, required=True, fulltextindexed=True)
    long_desc = SubjectRelation("Blog", composite="subject", cardinality="?*")
    manager = SubjectRelation("Personne", cardinality="?*", __permissions__=rperms("O"))


class composite_card11_2ttypes(RelationDefinition):
    subject = "Project"
    object = ("File", "Blog")
    composite = "subject"
    cardinality = "?*"


class Ticket(EntityType):
    title = String(maxsize=32, required=True, fulltextindexed=True)
    concerns = SubjectRelation("Project", composite="object")
    in_version = SubjectRelation(
        "Version", composite="object", cardinality="?*", inlined=True
    )


class Version(EntityType):
    name = String(required=True)


class Filesystem(EntityType):
    name = String()


class DirectoryPermission(EntityType):
    value = String()


class parent_fs(RelationDefinition):
    name = "parent"
    subject = "Directory"
    object = "Filesystem"


class Directory(EntityType):
    name = String(required=True)
    has_permission = SubjectRelation(
        "DirectoryPermission", cardinality="*1", composite="subject"
    )


class parent_directory(RelationDefinition):
    name = "parent"
    subject = "Directory"
    object = "Directory"
    composite = "object"


class Folder(EntityType):
    name = String(required=True)
    filed_under = SubjectRelation("Folder", description=_("parent folder"))


class TreeNode(EntityType):
    name = String(required=True)
    parent = SubjectRelation("TreeNode", cardinality="?*")


class Note(EntityType):
    type = String()
    ecrit_par = SubjectRelation("Personne")


class SubNote(Note):
    __specializes_schema__ = True
    description = String()


class buddies(ComputedRelation):
    rule = "S in_group G, O in_group G"


class Ami(EntityType):
    """A Person, for which surname is not required"""

    prenom = String()
    nom = String()


class Ville(EntityType):
    insee = Int(required=True)


class Service(EntityType):
    fabrique_par = SubjectRelation("Personne", cardinality="1*")


class Produit(EntityType):
    fabrique_par = SubjectRelation("Usine", cardinality="1*", inlined=True)


class Usine(EntityType):
    lieu = String(required=True)


class evaluee(RelationDefinition):
    subject = "CWUser"
    object = "Note"


class StateFull(WorkflowableEntityType):
    name = String()


class Reference(EntityType):
    nom = String(unique=True)
    ean = String(unique=True, required=True)


class FakeFile(EntityType):
    title = String(fulltextindexed=True, maxsize=256)
    data = Bytes(required=True, fulltextindexed=True, description=_("file to upload"))
    data_format = String(
        required=True,
        maxsize=128,
        description=_(
            "MIME type of the file. Should be dynamically set at upload time."
        ),
    )
    data_encoding = String(
        maxsize=32,
        description=_(
            "encoding of the file when it applies (e.g. text). "
            "Should be dynamically set at upload time."
        ),
    )
    data_name = String(
        required=True,
        fulltextindexed=True,
        description=_("name of the file. Should be dynamically set at upload time."),
    )
    description = RichString(
        fulltextindexed=True, internationalizable=True, default_format="text/rest"
    )


class Company(EntityType):
    order = Int()
    name = String()
    description = RichString()
