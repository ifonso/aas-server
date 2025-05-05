from basyx.aas.adapter import aasx
from basyx.aas import model


new_object_store: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
new_file_store = aasx.DictSupplementaryFileContainer()

# read file then show data
with aasx.AASXReader("./aas-static/FishTankAAS.aasx") as reader:
    reader.read_into(object_store=new_object_store,
                     file_store=new_file_store)

for thing in new_object_store:
    if not isinstance(thing, model.Submodel):
        continue

    print(thing._id_short)

