from typing import Optional, Union, Tuple, Any, Dict
from src.models import AssetAdministrationShell, Submodel, Property, ValueType, SubmodelElementCollection, DataElementCategory

from basyx.aas.adapter import aasx
from basyx.aas import model
from basyx.aas.model import Property as AASProperty, SubmodelElementCollection as AASSMC, Submodel as AASSubmodel


def extract_first_description(desc_dict: Optional[Dict[str, str]]) -> Optional[str]:
    return next(iter(desc_dict.values()), None) if desc_dict else None

def guess_and_cast_value_type(value: Any) -> Tuple[ValueType, Union[int, float, str]]:
    try:
        return ValueType.INT, int(value)
    except (ValueError, TypeError):
        try:
            return ValueType.FLOAT, float(value)
        except (ValueError, TypeError):
            return ValueType.STRING, str(value)

def build_property(prop: AASProperty) -> Property:
    assert prop.id_short, "Property missing id_short"
    assert prop.category, "Property missing category"
    assert prop.value is not None, "Property missing value"

    value_type, value = guess_and_cast_value_type(prop.value)

    return Property(
        id_short=prop.id_short,
        category=DataElementCategory(prop.category),
        description=extract_first_description(prop.description), # type: ignore
        value=value,
        value_type=value_type
    )

def build_smc(smc: AASSMC) -> SubmodelElementCollection:
    assert smc.id_short, "SMC missing id_short"
    assert smc.category, "SMC missing category"

    elements = []
    for element in smc.value:
        if isinstance(element, AASProperty):
            elements.append(build_property(element))
        elif isinstance(element, AASSMC):
            elements.append(build_smc(element))

    return SubmodelElementCollection(
        id_short=smc.id_short,
        category=DataElementCategory(smc.category),
        description=extract_first_description(smc.description), # type: ignore
        value=elements
    )

def convert_submodel(sm: AASSubmodel) -> Submodel:
    assert sm.id, "Submodel missing id"
    assert sm.id_short, "Submodel missing id_short"

    elements = []
    for e in sm.submodel_element:
        if isinstance(e, AASSMC):
            elements.append(build_smc(e))
        elif isinstance(e, AASProperty):
            try:
                elements.append(build_property(e))
            except Exception as err:
                print(f"Error parsing property {e.id_short}: {err}")

    return Submodel(
        id=sm.id,
        id_short=sm.id_short,
        submodel_elements=elements
    )

def aas_metamodel_converter(filepath: str) -> AssetAdministrationShell: 
    obj_store: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
    file_store = aasx.DictSupplementaryFileContainer()

    with aasx.AASXReader(filepath) as reader:
        reader.read_into(object_store=obj_store, file_store=file_store)

    aas_instance: Optional[AssetAdministrationShell] = None

    for el in obj_store:
        if isinstance(el, model.aas.AssetAdministrationShell):
            assert el.id, "AAS missing id"
            assert el.id_short, "AAS missing id_short"

            aas_instance = AssetAdministrationShell(
                id=el.id,
                id_short=el.id_short,
                data_elements=[]
            )

    assert aas_instance, "No AssetAdministrationShell found in AASX file."

    for sm in obj_store:
        if isinstance(sm, model.Submodel):
            aas_instance.data_elements.append(convert_submodel(sm))

    return aas_instance


aas = aas_metamodel_converter("./aas-static/FishTankAAS.aasx")
print(aas.model_dump_json(indent=2))
