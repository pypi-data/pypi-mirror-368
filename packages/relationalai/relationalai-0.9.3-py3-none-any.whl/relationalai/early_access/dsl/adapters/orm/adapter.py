from collections import defaultdict

from relationalai.early_access.dsl.adapters.orm.model import ExclusiveInclusiveSubtypeFact, ExclusiveSubtypeFact
from relationalai.early_access.dsl.adapters.orm.parser import ORMParser
from relationalai.early_access.dsl.core.types.standard import Integer, UnsignedInteger, String, DateTime, Date, Decimal
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.dsl.types.entities import AbstractEntityType


class ORMAdapter:

    def __init__(self, orm_file_path: str):
        self._parser = ORMParser(orm_file_path)
        self._relationship_role_value_constraints = defaultdict()
        self.model = self.orm_to_model()

    def orm_to_model(self):
        model = Model(self._parser.model_name())

        self._add_value_types(model)
        self._add_entity_types(model)
        self._add_subtype_relationships(model)
        self._add_relationships(model)
        self._add_external_identifying_relationships(model)
        self._add_role_value_constraints(model)

        return model

    def _add_value_types(self, md):
        for vt in self._parser.value_types().values():
            md.value_type(vt.name, self._map_datatype(vt.data_type))

    def _add_entity_types(self, md):
        for et in self._parser.entity_types().values():
            md.entity_type(et.name, ref_mode=et.ref_mode)

    def _add_subtype_relationships(self, md):
        for parent, children in self._parser.subtype_facts().items():
            supertype = md.lookup_concept(parent)
            subtypes = []
            exclusives = []
            exclusives_and_inclusives = []
            for child in children:
                sub = md.lookup_concept(child.subtype_name)
                if isinstance(child, ExclusiveInclusiveSubtypeFact):
                    exclusives_and_inclusives.append(sub)
                elif isinstance(child, ExclusiveSubtypeFact):
                    exclusives.append(sub)
                else:
                    subtypes.append(sub)
            if len(exclusives_and_inclusives) > 0:
                md.subtype_arrow(supertype, exclusives_and_inclusives, exclusive=True, inclusive=True)
            if len(exclusives) > 0:
                md.subtype_arrow(supertype, exclusives, exclusive=True)
            if len(subtypes) > 0:
                md.subtype_arrow(supertype, subtypes)

    def _add_relationships(self, md):
        object_types = self._parser.object_types()
        unique_roles = self._parser.unique_roles()
        mandatory_roles = self._parser.mandatory_roles()
        role_value_constraints = self._parser.role_value_constraints()
        fact_type_to_roles = self._parser.fact_type_to_roles()
        fact_type_to_internal_ucs = self._parser.fact_type_to_internal_ucs()
        fact_type_to_complex_ucs = self._parser.fact_type_to_complex_ucs()
        identifier_fact_type_to_entity_type = self._parser.identifier_fact_type_to_entity_type()
        for fact_type, reading_orders in self._parser.fact_type_readings().items():
            with md.relationship() as rel:
                role_idx_to_player = list()
                # Use the first reading to add the players
                for role in fact_type_to_roles[fact_type]:
                    role_name = role.name or None
                    role_unique = role.id in unique_roles
                    role_mandatory = role.id in mandatory_roles
                    p = md.lookup_concept(object_types[role.player].name)
                    rel.role(p, name=role_name, unique=role_unique, mandatory=role_mandatory)
                    role_idx_to_player.append(p)
                    if role.id in role_value_constraints:
                        self._relationship_role_value_constraints[rel] = role_value_constraints[role.id]
                # Create the readings
                for rdo in reading_orders:
                    argz = []
                    for rdo_role in rdo.roles:
                        orm_role = rdo_role.role
                        player_id = orm_role.player
                        player_name = object_types[player_id].name
                        player = md.lookup_concept(player_name)
                        role_idx = role_idx_to_player.index(player)
                        role = rel.role_at(role_idx)
                        argz.append(role)
                        if rdo_role.text:
                            argz.append(rdo_role.text)
                        if rdo_role.prefix or rdo_role.postfix:
                            role.verbalization(prefix=rdo_role.prefix, postfix=rdo_role.postfix)
                    entity_type = identifier_fact_type_to_entity_type.get(fact_type)
                    if entity_type:
                        player = md.lookup_concept(entity_type.name)
                        if argz[0].player_type == player:
                            ref_mode = entity_type.ref_mode
                            rel.relation(*argz, name=ref_mode) if ref_mode else rel.relation(*argz)
                        else:
                            rel.relation(*argz)
                    else:
                        rel.relation(*argz)
                # Marking identifying relationships
                if fact_type in fact_type_to_internal_ucs:
                    for uc in fact_type_to_internal_ucs[fact_type]:
                        if uc.identifies:
                            et = md.lookup_concept(object_types[uc.identifies].name)
                            role_name = role_idx_to_player.index(et)
                            md.ref_scheme(rel.relations()[role_name])
                # Add constraint spanning over multiple roles
                if fact_type in fact_type_to_complex_ucs:
                    for uc in fact_type_to_complex_ucs[fact_type]:
                        uc_roles = []
                        for role in fact_type_to_roles[fact_type]:
                            p = md.lookup_concept(object_types[role.player].name)
                            role_idx = role_idx_to_player.index(p)
                            rl = rel.role_at(role_idx)
                            if role.id in uc.roles:
                                uc_roles.append(rl)
                        md.unique(*uc_roles)

    def _add_external_identifying_relationships(self, model):
        roles = self._parser.roles()
        object_types = self._parser.object_types()
        for uc_id, uc in self._parser.external_uniqueness_constraints().items():
            et = model.lookup_concept(object_types[uc.identifies].name)
            identifying_rel = []
            for ro in uc.roles:
                rel_name = roles[ro].relationship_name
                relationship = model.lookup_relationship(rel_name)
                for rl in relationship.roles():
                    if rl.player_type == et:
                        idx = relationship.roles().index(rl)
                        identifying_rel.append(relationship.relations()[idx])
            model.ref_scheme(*identifying_rel)

    def _add_role_value_constraints(self, model):
        for rel, rvc in self._relationship_role_value_constraints.items():
            for rls in rel.relations():
                if isinstance(rls.reading().role_at(0).player(), AbstractEntityType):
                    model.role_value_constraint(rls, values=rvc.values)
                    break

    @staticmethod
    def _map_datatype(dt):
        mapping = {
            "AutoCounterNumericDataType": Integer,
            "UnsignedIntegerNumericDataType": UnsignedInteger,
            "VariableLengthTextDataType": String,
            "DateAndTimeTemporalDataType": DateTime,
            "DecimalNumericDataType": Decimal,
            "DateTemporalDataType": Date
        }
        return mapping.get(dt, String)