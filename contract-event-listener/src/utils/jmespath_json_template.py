import copy
import jmespath


class JMESPathJSONTemplate:

    class JMESPathTemplateValueGetter:
        def __init__(self, path, expression):
            self.expression = jmespath.compile(expression)
            self.path = path

        def update(self, target_json, data_json):
            value = self.expression.search(data_json)
            if not self.path:
                return value
            target_value = target_json
            for p in self.path[:-1]:
                target_value = target_value[p]
            target_value[self.path[-1]] = value
            return target_json

    def _add_jmespath_template_value_getter(self, path, json_template):
        if isinstance(json_template, dict):
            for dict_value_key, dict_value in json_template.items():
                dict_path = path + [dict_value_key]
                self._add_jmespath_template_value_getter(dict_path, dict_value)
        elif isinstance(json_template, list):
            for list_index in range(len(json_template)):
                list_value = json_template[list_index]
                list_path = path + [list_index]
                self._add_jmespath_template_value_getter(list_path, list_value)
        else:
            self.jmespath_template_values_getters.append(self.JMESPathTemplateValueGetter(path, json_template))

    def __init__(self, json_template):
        self.jmespath_template_values_getters = []
        self.json_template = copy.deepcopy(json_template)
        self._add_jmespath_template_value_getter([], json_template)

    def render(self, data):
        template = copy.deepcopy(self.json_template)
        for jmespath_template_value_getter in self.jmespath_template_values_getters:
            template = jmespath_template_value_getter.update(template, data)
        return template
