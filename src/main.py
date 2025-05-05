from typing import Optional, Union, Tuple
from src.models import AssetAdministrationShell, Submodel, Property, ValueType, SubmodelElementCollection

from basyx.aas.adapter import aasx
from basyx.aas import model


def aas_metamodel_converter(filepath: str) -> AssetAdministrationShell: 
    asset_administration_shell: Optional[AssetAdministrationShell] = None

    obj_store: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
    file_store = aasx.DictSupplementaryFileContainer()

    with aasx.AASXReader(filepath) as reader:
        reader.read_into(object_store=obj_store,
                         file_store=file_store)

    # Criação do AAS
    for el in [e for e in obj_store if isinstance(e, model.aas.AssetAdministrationShell)]:
        assert el.id, "no empty id"
        assert el.id_short, "no empty id_short"

        print(el.display_name)

        asset_administration_shell = AssetAdministrationShell(
            id=el.id,
            id_short=el.id_short,
            data_elements=[]
        )

    assert asset_administration_shell, "No AAS in aasx file."

    # Populando metamodelos
    for sm in [e for e in obj_store if isinstance(e, model.Submodel)]:
        asset_administration_shell.data_elements.append(submodel_converter(sm))


    print(asset_administration_shell.model_dump_json(indent=2))

    return asset_administration_shell


def converter(valor) -> Tuple[ValueType, Union[int, float, str]]:
    try:
        return (ValueType.INT, int(valor))

    except (ValueError, TypeError):
        try:
            return (ValueType.FLOAT, float(valor))

        except (ValueError, TypeError):
            return (ValueType.STRING, str(valor))


def property_builder(prop: model.Property) -> Property:
    assert prop.id_short, f"prop {prop} has no id_short"
    assert prop.category is not None, f"prop {prop} has no category"
    assert prop.value is not None, f"prop {prop} has no value"
    assert prop.value_type is not None, f"prop {prop} has no value_type"

    description: Optional[str] = None

    if prop.description:
        description = next(iter(prop.description.values()), None)

    typ, value = converter(prop.value)

    return Property(
        id_short=prop.id_short,
        category=prop.category,
        description=description,
        value=value, # type: ignore
        value_type=typ
    )


def smc_builder(smc: model.SubmodelElementCollection) -> SubmodelElementCollection:
    assert smc.id_short, "no id_short in collection"
    assert smc.category, "no category set"

    description: Optional[str] = None

    if smc.description:
        description = next(iter(smc.description.values()), None)

    submodel_collection = SubmodelElementCollection(
        id_short=smc.id_short,
        category=smc.category,
        description=description,
        value=[]
    )

    for element in smc.value:
        if isinstance(element, model.Property):
            submodel_collection.value.append(property_builder(element))

        elif isinstance(element, model.SubmodelElementCollection):
            submodel_collection.value.append(smc_builder(element))

        else:
            continue

    return submodel_collection


def submodel_converter(sm: model.Submodel) -> Submodel:
    assert sm.id, "no id in submodel"
    assert sm.id_short, "no id_short in submodel"

    submodel = Submodel(
        id=sm.id,
        id_short=sm.id_short,
        submodel_elements=[]
    )

    for e in sm.submodel_element:
        if isinstance(e, model.SubmodelElementCollection):
            submodel.submodel_elements.append(smc_builder(e))
        
        elif isinstance(e, model.Property):
            try:
                submodel.submodel_elements.append(property_builder(e))
            except Exception as e:
                print(e)

        else:
            continue
    
    return submodel


aas_metamodel_converter("./aas-static/FishTankAAS.aasx")

