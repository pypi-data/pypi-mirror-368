# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2018 Linaro Ltd.
# Copyright 2018-2023 Arm Ltd.
# Python library for Devicetree schema validation
import sys
import os
import re
import copy
import jsonschema

import dtschema

from jsonschema.exceptions import RefResolutionError

schema_base_url = "http://devicetree.org/"
schema_basedir = os.path.dirname(os.path.abspath(__file__))


def path_to_obj(tree, path):
    for pc in path:
        tree = tree[pc]
    return tree


def get_line_col(tree, path, obj=None):
    import ruamel.yaml

    if isinstance(obj, ruamel.yaml.comments.CommentedBase):
        return obj.lc.line, obj.lc.col
    obj = path_to_obj(tree, path)
    if isinstance(obj, ruamel.yaml.comments.CommentedBase):
        return obj.lc.line, obj.lc.col
    if len(path) < 1:
        return -1, -1
    obj = path_to_obj(tree, list(path)[:-1])
    if isinstance(obj, ruamel.yaml.comments.CommentedBase):
        if path[-1] == '$nodename':
            return -1, -1
        return obj.lc.key(path[-1])
    return -1, -1

def _is_node_schema(schema):
    return isinstance(schema, dict) and \
           (('type' in schema and schema['type'] == 'object') or
            schema.keys() & {'properties', 'patternProperties', 'additionalProperties', 'unevaluatedProperties'})


def _schema_allows_no_undefined_props(schema):
    if _is_node_schema(schema):
        return True

    additional_props = schema.get("additionalProperties", True)
    uneval_props = schema.get("unevaluatedProperties", True)

    return not additional_props or isinstance(additional_props, dict) or \
           not uneval_props or isinstance(uneval_props, dict)

class DTSchema(dict):
    DtValidator = jsonschema.validators.extend(
        jsonschema.Draft201909Validator,
        format_checker=jsonschema.FormatChecker(),
        version='DT')

    def __init__(self, schema_file, line_numbers=False):
        self.paths = [(schema_base_url, schema_basedir + '/')]
        with open(schema_file, 'r', encoding='utf-8') as f:
            import ruamel.yaml

            if line_numbers:
                rtyaml = ruamel.yaml.YAML(typ='rt')
                rtyaml.allow_duplicate_keys = False
                rtyaml.preserve_quotes = True

                schema = rtyaml.load(f.read())
            else:
                yaml = ruamel.yaml.YAML(typ='safe')
                yaml.allow_duplicate_keys = False
                schema = yaml.load(f.read())

        self.filename = os.path.abspath(schema_file)
        self._validator = None

        id = schema['$id'].rstrip('#')
        match = re.search('(.*/schemas/)(.+)$', id)
        self.base_path = os.path.abspath(schema_file)[:-len(match[2])]

        super().__init__(schema)

    def validator(self):
        if not self._validator:
            resolver = jsonschema.RefResolver.from_schema(self,
                                handlers={'http': self.http_handler})
            meta_schema = resolver.resolve_from_url(self['$schema'])
            self._validator = self.DtValidator(meta_schema, resolver=resolver)

        return self._validator

    def http_handler(self, uri):
        '''Custom handler for http://devicetree.org references'''
        uri = uri.rstrip('#')
        missing_files = ''
        for p in self.paths:
            filename = uri.replace(p[0], p[1])
            if not os.path.isfile(filename):
                missing_files += f"\t{filename}\n"
                continue
            with open(filename, 'r', encoding='utf-8') as f:
                import ruamel.yaml
                yaml = ruamel.yaml.YAML(typ='safe')
                yaml.allow_duplicate_keys = False
                return yaml.load(f.read())

        raise RefResolutionError(f'Error in referenced schema matching $id: {uri}\n\tTried these paths (check schema $id if path is wrong):\n{missing_files}')

    def annotate_error(self, error, schema, path):
        error.note = None
        error.schema_file = None

        for e in error.context:
            self.annotate_error(e, schema, path + e.schema_path)

        scope = self.validator().ID_OF(schema)
        self.validator().resolver.push_scope(scope)
        ref_depth = 1

        for p in path:
            while p not in schema and '$ref' in schema and isinstance(schema['$ref'], str):
                ref = self.validator().resolver.resolve(schema['$ref'])
                schema = ref[1]
                self.validator().resolver.push_scope(ref[0])
                ref_depth += 1

            if '$id' in schema and isinstance(schema['$id'], str):
                error.schema_file = schema['$id']

            schema = schema[p]

            if isinstance(schema, dict):
                if 'description' in schema and isinstance(schema['description'], str):
                    error.note = schema['description']

        while ref_depth > 0:
            self.validator().resolver.pop_scope()
            ref_depth -= 1

        if isinstance(error.schema, dict) and 'description' in error.schema:
            error.note = error.schema['description']

    def iter_errors(self):
        meta_schema = self.validator().resolver.resolve_from_url(self['$schema'])

        for error in self.validator().iter_errors(self):
            scherr = jsonschema.exceptions.SchemaError.create_from(error)
            self.annotate_error(scherr, meta_schema, scherr.schema_path)
            scherr.linecol = get_line_col(self, scherr.path)
            yield scherr

    def is_valid(self, strict=False):
        ''' Check if schema passes validation against json-schema.org schema '''
        if strict:
            for error in self.iter_errors():
                raise error
        else:
            # Using the draft7 metaschema because 2019-09 with $recursiveRef seems broken
            # Probably fixed with referencing library
            for error in self.DtValidator(jsonschema.Draft7Validator.META_SCHEMA).iter_errors(self):
                scherr = jsonschema.exceptions.SchemaError.create_from(error)
                raise scherr

    def fixup(self):
        processed_schema = copy.deepcopy(dict(self))
        dtschema.fixups.fixup_schema(processed_schema)
        return processed_schema

    def _check_schema_refs(self, schema, parent=None, is_common=False, has_constraint=False):
        if not parent:
            is_common = not _schema_allows_no_undefined_props(schema)
        if isinstance(schema, dict):
            if parent in {'if', 'select', 'definitions', '$defs', 'then',
                          'else', 'dependencies', 'dependentSchemas'}:
                return

            if _is_node_schema(schema):
                has_constraint = _schema_allows_no_undefined_props(schema)

            ref_has_constraint = True
            if '$ref' in schema:
                ref = schema['$ref']
                url, ref_sch = self.validator().resolver.resolve(ref)
                ref_has_constraint = _schema_allows_no_undefined_props(ref_sch)

            if not (is_common or ref_has_constraint or has_constraint or
               (schema.keys() & {'additionalProperties', 'unevaluatedProperties'})):
                print(f"{self.filename}: {parent}: Missing additionalProperties/unevaluatedProperties constraint\n",
                      file=sys.stderr)

            for k, v in schema.items():
                self._check_schema_refs(v, parent=k, is_common=is_common,
                                        has_constraint=has_constraint)
        elif isinstance(schema, (list, tuple)):
            for i in range(len(schema)):
                self._check_schema_refs(schema[i], parent=parent, is_common=is_common,
                                        has_constraint=has_constraint)

    def check_schema_refs(self):
        id = self['$id'].rstrip('#')
        base1 = re.search('schemas/(.+)$', id)[1]
        base2 = self.filename.replace(self.filename[:-len(base1)], '')
        if not base1 == base2:
            print(f"{self.filename}: $id: Cannot determine base path from $id, relative path/filename doesn't match actual path or filename\n",
                  f"\t $id: {id}\n",
                  f"\tfile: {self.filename}",
                  file=sys.stderr)
            return

        scope = self.validator().ID_OF(self)
        if scope:
            self.validator().resolver.push_scope(scope)

        self.paths = [
            (schema_base_url + 'schemas/', self.base_path),
            (schema_base_url + 'schemas/', schema_basedir + '/schemas/'),
        ]

        try:
            self._check_schema_refs(self)
        except jsonschema.RefResolutionError as exc:
            print(f"{self.filename}:\n\t{exc}", file=sys.stderr)
