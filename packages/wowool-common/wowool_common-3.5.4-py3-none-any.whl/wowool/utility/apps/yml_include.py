import yaml
import csv


class CustomLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super(CustomLoader, self).__init__(stream)

    def include(self, node):
        filename = node.value
        with open(filename, "r") as f:
            return yaml.load(f, CustomLoader)

    def cvs_load(self, node):
        filename = node.value
        retval = []
        with open(filename, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)
            for row in csv_reader:
                retval.append({name: row[i] for i, name in enumerate(header)})
        return retval


CustomLoader.add_constructor("!include", CustomLoader.include)
CustomLoader.add_constructor("!csv", CustomLoader.cvs_load)


def custom_yaml_load(stream):
    return yaml.load(stream, Loader=CustomLoader)
