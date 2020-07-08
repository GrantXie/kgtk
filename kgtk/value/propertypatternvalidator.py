"""
Validate property patterns..
"""

from argparse import ArgumentParser, Namespace
import attr
import copy
from enum import Enum
from pathlib import Path
import re
import sys
import typing

from kgtk.kgtkformat import KgtkFormat
from kgtk.io.kgtkreader import KgtkReader, KgtkReaderMode, KgtkReaderOptions
from kgtk.io.kgtkwriter import KgtkWriter
from kgtk.value.kgtkvalue import KgtkValue
from kgtk.value.kgtkvalueoptions import KgtkValueOptions

@attr.s(slots=True, frozen=True)
class PropertyPattern:
    class Action(Enum):
        NODE1_COLUMN = "node1_column"
        NODE1_TYPE = "node1_type"
        NODE1_ALLOW_LIST = "node1_allow_list"
        NODE1_VALUES = "node1_values"
        NODE1_PATTERN = "node1_pattern"

        NODE2_COLUMN = "node2_column"
        NODE2_TYPE = "node2_type"
        NODE2_ALLOW_LIST = "node2_allow_list"
        NODE2_VALUES = "node2_values"
        NODE2_PATTERN = "node2_pattern"

        NOT_IN = "not_in"
        # LABEL_COLUM = "label_column"
        MINVAL = "minval"
        MAXVAL = "maxval"
        MINOCCURS = "minoccurs"
        MAXOCCURS = "maxoccurs"
        ISA = "isa"
        MATCHES = "matches"
        LABEL_PATTERN = "label_pattern"
        MINDISTINCT = "mindistinct"
        MAXDISTINCT = "maxdistinct"
        REQUIRED_IN = "required_id"
        MINDATE = "mindate"
        MAXDATE = "maxdate"
        
    # TODO: create validators where missing:
    prop_datatype: str = attr.ib(validator=attr.validators.instance_of(str))
    action: Action = attr.ib()
    pattern: typing.Optional[typing.Pattern] = attr.ib()
    intval: typing.Optional[int] = attr.ib()
    number: typing.Optional[float] = attr.ib()
    column_names: typing.List[str] = attr.ib()
    values: typing.List[str] = attr.ib()
    truth: bool = attr.ib()

    # Even though the object is frozen, we can still alter lists.
    column_idxs: typing.List[int] = attr.ib(factory=list)

    @classmethod
    def new(cls, node1_value: KgtkValue, label_value: KgtkValue, node2_value: KgtkValue)->'PropertyPattern':
        prop_datatype = node1_value.value
        action: PropertyPattern.Action = cls.Action(label_value.value)

        kv: KgtkValue
        
        pattern: typing.Optional[typing.Pattern] = None
        if action in (cls.Action.NODE1_PATTERN,
                      cls.Action.NODE2_PATTERN,
                      cls.Action.LABEL_PATTERN,
                      cls.Action.MATCHES):
            if node2_value.fields is None:
                raise ValueError("%s: Node2 has no fields" % (action.value)) # TODO: better complaint
            if node2_value.fields.text is None:
                raise ValueError("%s: Node2 has no text" % (action.value)) # TODO: better complaint
                
            pattern = re.compile(node2_value.fields.text)

        intval: typing.Optional[int] = None
        if action in (cls.Action.MINOCCURS,
                      cls.Action.MAXOCCURS,
                      cls.Action.MINDISTINCT,
                      cls.Action.MAXDISTINCT):
            if node2_value.fields is None:
                raise ValueError("%s: Node2 has no fields" % (action.value)) # TODO: better complaint
            if node2_value.fields.number is None:
                raise ValueError("%s: Node2 has no number" % (action.value)) # TODO: better complaint
            intval = int(node2_value.fields.number)

        number: typing.Optional[float] = None
        if action in(cls.Action.MINVAL,
                     cls.Action.MAXVAL):
            if node2_value.fields is None:
                raise ValueError("%s: Node2 has no fields" % (action.value)) # TODO: better complaint
            if node2_value.fields.number is None:
                raise ValueError("%s: Node2 has no number" % (action.value)) # TODO: better complaint
            number = float(node2_value.fields.number)

        column_names: typing.List[str] = [ ]
        if action in (cls.Action.NOT_IN,):
            if node2_value.is_symbol():
                column_names.append(node2_value.value)
            elif node2_value.is_list():
                for kv in node2_value.get_list_items():
                    if kv.is_symbol():
                        column_names.append(kv.value)
                    else:
                        raise ValueError("%s: List value is not a symbol" % (action.value)) # TODO: better complaint
            else:
                raise ValueError("%s: Value '%s' is not a symbol or list of symbols" % (action.value, node2_value.value)) # TODO: better complaint
            # TODO: validate that the column names are valid and get their indexes.

        if action in (
                # cls.Action.LABEL_COLUM,
                cls.Action.NODE1_COLUMN,
                cls.Action.NODE2_COLUMN,
                cls.Action.REQUIRED_IN,):
            if label_value.is_symbol():
                column_names.append(node2_value.value)
            else:
                raise ValueError("%s:Value is not a symbol" % (action.value)) # TODO: better complaint
            # TODO: validate that the column names are valid and get their indexes.

        values: typing.List[str] = [ ]
        if action in (cls.Action.NODE1_TYPE,
                      cls.Action.NODE2_TYPE,
                      cls.Action.ISA,):
            if node2_value.is_symbol():
                values.append(node2_value.value)
            elif node2_value.is_list():
                for kv in node2_value.get_list_items():
                    if kv.is_symbol():
                        values.append(kv.value)
                    else:
                        raise ValueError("%s: List value is not a symbol" % (action.value)) # TODO: better complaint
            else:
                raise ValueError("%s: Value '%s' is not a symbol or list of symbols" % (action.value, node2_value.value)) # TODO: better complaint

        if action in (cls.Action.NODE1_VALUES,
                      cls.Action.NODE2_VALUES,):
            if node2_value.is_list():
                for kv in node2_value.get_list_items():
                    values.append(kv.value)
            else:
                values.append(node2_value.value)

        truth: bool = False
        if action in (cls.Action.NODE1_ALLOW_LIST,
                      cls.Action.NODE2_ALLOW_LIST,):
            if node2_value.is_boolean() and node2_value.fields is not None and node2_value.fields.truth is not None:
                truth = node2_value.fields.truth
            else:
                raise ValueError("%s: Value '%s' is not a boolean" % (action.value, node2_value.value)) # TODO: better complaint

        return cls(prop_datatype, action, pattern, intval, number, column_names, values, truth)

@attr.s(slots=True, frozen=True)
class PropertyPatternFactory:
    # Indices in the property pattern file:
    node1_idx: int = attr.ib(validator=attr.validators.instance_of(int))
    label_idx: int = attr.ib(validator=attr.validators.instance_of(int))
    node2_idx: int = attr.ib(validator=attr.validators.instance_of(int))

    value_options: KgtkValueOptions = attr.ib(validator=attr.validators.instance_of(KgtkValueOptions))

    verbose: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    very_verbose: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)

    def from_row(self, row: typing.List[str])->'PropertyPattern':
        node1_value: KgtkValue = KgtkValue(row[self.node1_idx], options=self.value_options, parse_fields=True)
        label_value: KgtkValue = KgtkValue(row[self.label_idx], options=self.value_options, parse_fields=True)
        node2_value: KgtkValue = KgtkValue(row[self.node2_idx], options=self.value_options, parse_fields=True)

        node1_value.validate()
        label_value.validate()
        node2_value.validate()

        return PropertyPattern.new(node1_value, label_value, node2_value)

@attr.s(slots=True, frozen=True)
class PropertyPatterns:
    patterns: typing.Mapping[str, typing.Mapping[PropertyPattern.Action, PropertyPattern]] = attr.ib()

    matches: typing.Mapping[str, typing.Pattern] = attr.ib()

    @classmethod
    def load(cls, kr: KgtkReader,
             value_options: KgtkValueOptions,
             error_file: typing.TextIO = sys.stderr,
             verbose: bool = False,
             very_verbose: bool = False,
    )->'PropertyPatterns':
        patmap: typing.MutableMapping[str, typing.MutableMapping[PropertyPattern.Action, PropertyPattern]] = { }
        matches: typing.MutableMapping[str, typing.Pattern] = { }
        
        if kr.node1_column_idx < 0:
            raise ValueError("node1 column missing from property pattern file")
        if kr.label_column_idx < 0:
            raise ValueError("label column missing from property pattern file")
        if kr.node2_column_idx < 0:
            raise ValueError("node2 column missing from property pattern file")

        ppf: PropertyPatternFactory = PropertyPatternFactory(kr.node1_column_idx,
                                                             kr.label_column_idx,
                                                             kr.node2_column_idx,
                                                             value_options,
                                                             verbose=verbose,
                                                             very_verbose=very_verbose,
        )

        row: typing.List[str]
        for row in kr:
            pp: PropertyPattern = ppf.from_row(row)
            prop_datatype: str = pp.prop_datatype
            if prop_datatype not in patmap:
                patmap[prop_datatype] = { }
            action: PropertyPattern.Action = pp.action
            if action in patmap[prop_datatype]:
                raise ValueError("Duplicate action record in (%s)" % "|".join(row))
            patmap[prop_datatype][action] = pp
            if very_verbose:
                print("loaded %s->%s" % (prop_datatype, action.value), file=error_file, flush=True)
            if action == PropertyPattern.Action.MATCHES and pp.pattern is not None:
                matches[prop_datatype] = pp.pattern

        return cls(patmap, matches)

    def lookup(self, prop: str, action: PropertyPattern.Action)->typing.Optional[PropertyPattern]:
        if prop in self.patterns:
            if action in self.patterns[prop]:
                return self.patterns[prop][action]
        return None
        

@attr.s(slots=True, frozen=True)
class PropertyPatternValidator:
    pps: PropertyPatterns = attr.ib()

    column_names: typing.List[str] = attr.ib()
    column_name_map: typing.Mapping[str, int] = attr.ib()

    # These are the indexes in the input file:
    node1_idx: int = attr.ib()
    label_idx: int = attr.ib()
    node2_idx: int = attr.ib()

    value_options: KgtkValueOptions = attr.ib()

    error_file: typing.TextIO = attr.ib(default=sys.stderr)
    verbose: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    very_verbose: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)

    # We clear this set, getting around frozen attribute.
    isa_scoreboard: typing.Set[str] = attr.ib(factory=set)

    def validate_not_in(self, rownum: int, row: typing.List[str])->bool:
        """
        Check each column of the row to see if the contents violates a not_in relationship.
        """
        result: bool = True
        idx: int
        column_name: str
        for idx, column_name in enumerate(self.column_names):
            thing: str = row[idx]
            # print("Row %d: idx=%d column_name=%s thing=%s" % (rownum, idx, column_name, thing), file=self.error_file, flush=True)
            if thing in self.pps.patterns:
                thing_patterns: typing.Mapping[PropertyPattern.Action, PropertyPattern] = self.pps.patterns[thing]
                # print("len(thing_patterns) = %d" % len(thing_patterns), file=self.error_file, flush=True)
                if PropertyPattern.Action.NOT_IN in thing_patterns:
                    column_names: typing.List[str] = thing_patterns[PropertyPattern.Action.NOT_IN].column_names
                    # print("NOT_IN columns: %s" % " ".join(column_names), file=self.error_file, flush=True)
                    if column_name in column_names:
                        print("Row %d: Found '%s' in column '%s', which is prohibited." % (rownum, thing, column_name), file=self.error_file, flush=True)
                        result = False
        return result

    def validate_type(self, rownum: int, value: KgtkValue, prop: str, allowed_types: typing.List[str], who: str)->bool:
        if value.data_type is None:
            print("Row %d: the %s value '%s' KGTK type is missing." % (rownum, who, value.value), file=self.error_file, flush=True)
            return False
        else:
            type_name: str = value.data_type.lower()
            if type_name not in allowed_types:
                print("Row %d: the %s KGTK datatype '%s' is not in the list of allowed %s types for %s: %s" % (rownum, who, type_name, who, prop,
                                                                                                               KgtkFormat.LIST_SEPARATOR.join(allowed_types)),
                      file=self.error_file, flush=True)
                return False
            return True

    def validate_value(self, rownum: int, value: KgtkValue, prop: str, allowed_values: typing.List[str], who: str)->bool:
        if value.value not in allowed_values:
            print("Row %d: the %s value '%s' is not in the list of %s values for %s: %s" % (rownum, who, value.value, who, prop,
                                                                                            KgtkFormat.LIST_SEPARATOR.join(allowed_values)),
                  file=self.error_file, flush=True)
            return False
        return True        

    def validate_pattern(self, rownum: int, item: str, prop: str, pattern: typing.Optional[typing.Pattern], who: str)->bool:
        if pattern is None:
            raise ValueError("Missing %s pattern for %s" % (who, prop))

        match: typing.Optional[typing.Match] = pattern.fullmatch(item)
        if match:
            return True

        print("Row %d: the %s value '%s' does not match the %s pattern for %s" % (rownum, who, item, who, prop), file=self.error_file, flush=True)
        return False

    def validate_minval(self, rownum: int, prop: str, minval: typing.Optional[float], node2_value: KgtkValue)->bool:
        if minval is None:
            return True

        if not node2_value.is_number_or_quantity():
            return True
        
        if node2_value.fields is None:
            return True
        
        if node2_value.fields.number is None:
            return True
        number: float = float(node2_value.fields.number)

        if number >= minval:
            return True

        print("Row: %d: prop %s value %f is less than minval %f." % (rownum, prop, number, minval), file=self.error_file, flush=True)
        return False

    def validate_maxval(self, rownum: int, prop: str, maxval: typing.Optional[float], node2_value: KgtkValue)->bool:
        if maxval is None:
            return True

        if not node2_value.is_number_or_quantity():
            return True
        
        if node2_value.fields is None:
            return True
        
        if node2_value.fields.number is None:
            return True
        number: float = float(node2_value.fields.number)

        if number <= maxval:
            return True

        print("Row: %d: prop %s value %f is greater than maxval %f." % (rownum, prop, number, maxval), file=self.error_file, flush=True)
        return False

    def validate_node1(self,
                       rownum: int,
                       node1: str,
                       prop: str,
                       pats: typing.Mapping[PropertyPattern.Action, PropertyPattern])->bool:
        node1_value = KgtkValue(node1, options=self.value_options, parse_fields=True)
        if node1_value.validate():
            return self.validate_node1_value(rownum, node1_value, prop, pats)
        else:
            print("Row %d: the node1 value '%s' is not valid KGTK." % (rownum, node1_value.value), file=self.error_file, flush=True)
            return False

    def validate_node1_value(self,
                             rownum: int,
                             node1_value: KgtkValue,
                             prop: str,
                             pats: typing.Mapping[PropertyPattern.Action, PropertyPattern])->bool:
        result: bool = True

        if node1_value.is_list():
            if PropertyPattern.Action.NODE1_ALLOW_LIST in pats and pats[PropertyPattern.Action.NODE1_ALLOW_LIST].truth:
                # Validate each item on the list seperately.
                list_item: KgtkValue
                for list_item in node1_value.get_list_items():
                    result &= self.validate_node1_value(rownum, list_item, prop, pats)
                return result
            else:
                print("Row %d: The node1 value '%s' is not allowed to be a list." % (rownum, node1_value.value), file=self.error_file, flush=True)
                return False

        if PropertyPattern.Action.NODE1_TYPE in pats:
            result &= self.validate_type(rownum, node1_value, prop, pats[PropertyPattern.Action.NODE1_TYPE].values, "node1")

        if PropertyPattern.Action.NODE1_VALUES in pats:
            result &= self.validate_value(rownum, node1_value, prop, pats[PropertyPattern.Action.NODE1_VALUES].values, "node1")

        if PropertyPattern.Action.NODE1_PATTERN in pats:
            result &= self.validate_pattern(rownum, node1_value.value, prop, pats[PropertyPattern.Action.NODE1_PATTERN].pattern, "node1")

        return result

    def validate_node2(self,
                       rownum: int,
                       node2: str,
                       prop: str,
                       pats: typing.Mapping[PropertyPattern.Action, PropertyPattern])->bool:
        node2_value = KgtkValue(node2, options=self.value_options, parse_fields=True)
        if node2_value.validate():
            return self.validate_node2_value(rownum, node2_value, prop, pats)
        else:
            print("Row %d: the node2 value '%s' is not valid KGTK." % (rownum, node2_value.value), file=self.error_file, flush=True)
            return False

    def validate_node2_value(self,
                             rownum: int,
                             node2_value: KgtkValue,
                             prop: str,
                             pats: typing.Mapping[PropertyPattern.Action, PropertyPattern])->bool:
        result: bool = True

        if node2_value.is_list():
            if PropertyPattern.Action.NODE2_ALLOW_LIST in pats and pats[PropertyPattern.Action.NODE2_ALLOW_LIST].truth:
                # Validate each item on the list seperately.
                list_item: KgtkValue
                for list_item in node2_value.get_list_items():
                    result &= self.validate_node2_value(rownum, list_item, prop, pats)
                return result
            else:
                print("Row %d: The node2 value '%s' is not allowed to be a list." % (rownum, node2_value.value), file=self.error_file, flush=True)
                return False

        if PropertyPattern.Action.NODE2_TYPE in pats:
            result &= self.validate_type(rownum, node2_value, prop, pats[PropertyPattern.Action.NODE2_TYPE].values, "node2")

        if PropertyPattern.Action.NODE2_VALUES in pats:
            result &= self.validate_value(rownum, node2_value, prop, pats[PropertyPattern.Action.NODE2_VALUES].values, "node2")

        if PropertyPattern.Action.NODE2_PATTERN in pats:
            result &= self.validate_pattern(rownum, node2_value.value, prop, pats[PropertyPattern.Action.NODE2_PATTERN].pattern, "node2")

        if PropertyPattern.Action.MINVAL in pats:
            result &= self.validate_minval(rownum, prop, pats[PropertyPattern.Action.MINVAL].number, node2_value)

        if PropertyPattern.Action.MAXVAL in pats:
            result &= self.validate_maxval(rownum, prop, pats[PropertyPattern.Action.MAXVAL].number, node2_value)

        return result

    def validate_isa(self, rownum: int, row: typing.List[str], prop: str, newprops: typing.List[str])->bool:
        result: bool = True # Everying's good until we discover otherwise.
        self.isa_scoreboard.add(prop)
        newprop: str
        for newprop in newprops:
            if newprop in self.isa_scoreboard:
                print("Row %d: isa loop detected with %s." % (rownum, newprop), file=self.error_file, flush=True)
            else:
                result &= self.validate_prop(rownum, row, newprop)
        return result

    def get_idx(self,
                rownum: int,
                prop: str,
                action: PropertyPattern.Action,
                pats: typing.Mapping[PropertyPattern.Action, PropertyPattern],
                default_idx: int,
                who: str,
    )->int:
        if action in pats:
            column_name: str = pats[action].column_names[0]
            if column_name in self.column_name_map:
                return self.column_name_map[column_name]
            else:
                print("Row %d: prop '%s' %s column name '%s' not found in input file." % (rownum, prop, who, column_name), file=self.error_file, flush=True)
                return -1
        else:
            return default_idx        

    def validate_prop(self, rownum: int, row: typing.List[str], prop: str)->bool:
        result: bool = True # Everying's good until we discover otherwise.

        if prop in self.pps.patterns:
            pats: typing.Mapping[PropertyPattern.Action, PropertyPattern] = self.pps.patterns[prop]
            node1_idx: int = self.get_idx(rownum, prop, PropertyPattern.Action.NODE1_COLUMN, pats, self.node1_idx, "node1")
            if node1_idx >= 0:
                result &= self.validate_node1(rownum, row[node1_idx], prop, pats)
            else:
                result = False

            node2_idx: int = self.get_idx(rownum, prop, PropertyPattern.Action.NODE2_COLUMN, pats, self.node2_idx, "node2")
            if node2_idx >= 0:
                result &= self.validate_node2(rownum, row[node2_idx], prop, pats)
            else:
                result = False
                
            if PropertyPattern.Action.ISA in pats:
                result &= self.validate_isa(rownum, row, prop, pats[PropertyPattern.Action.ISA].values)

            if PropertyPattern.Action.LABEL_PATTERN in pats:
                result &= self.validate_pattern(rownum, row[self.label_idx], prop, pats[PropertyPattern.Action.LABEL_PATTERN].pattern, "label")

        return result

    def validate(self, rownum: int, row: typing.List[str])->bool:
        result: bool = True # Everying's good until we discover otherwise.

        self.isa_scoreboard.clear()

        result &= self.validate_not_in(rownum, row)
        prop: str = row[self.label_idx]
        result &= self.validate_prop(rownum, row, prop)

        prop2: str
        for prop2 in sorted(self.pps.matches.keys()):
            if self.pps.matches[prop2].fullmatch(prop):
                result &= self.validate_prop(rownum, row, prop2)

        return result

    @classmethod
    def new(cls,
            pps: PropertyPatterns,
            kr: KgtkReader,
            value_options: KgtkValueOptions,
            error_file: typing.TextIO,
            verbose: bool,
            very_verbose: bool)->'PropertyPatternValidator':
        return PropertyPatternValidator(pps,
                                        kr.column_names.copy(),
                                        copy.copy(kr.column_name_map),
                                        kr.node1_column_idx,
                                        kr.label_column_idx,
                                        kr.node2_column_idx,
                                        value_options=value_options,
                                        error_file=error_file,
                                        verbose=verbose,
                                        very_verbose=very_verbose)

def main():
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-i", "--input-file", dest="input_file", help="The input file to validate. (default stdin)", type=Path, default="-")
    parser.add_argument(      "--pattern-file", dest="pattern_file", help="The property pattern file to load.", type=Path, required=True)
    parser.add_argument("-o", "--output-file", dest="output_file", help="The output file for good records. (optional)", type=Path)
    parser.add_argument(      "--reject-file", dest="reject_file", help="The output file for bad records. (optional)", type=Path)

    KgtkReader.add_debug_arguments(parser, expert=True)
    KgtkReaderOptions.add_arguments(parser, expert=True)
    KgtkValueOptions.add_arguments(parser)
    args: Namespace = parser.parse_args()

    error_file: typing.TextIO = sys.stdout if args.errors_to_stdout else sys.stderr

    # Build the option structures.
    reader_options: KgtkReaderOptions = KgtkReaderOptions.from_args(args)
    value_options: KgtkValueOptions = KgtkValueOptions.from_args(args)

    pkr: KgtkReader = KgtkReader.open(args.pattern_file,
                                     error_file=error_file,
                                     mode=KgtkReaderMode.EDGE,
                                     options=reader_options,
                                     value_options=value_options,
                                     verbose=args.verbose,
                                     very_verbose=args.very_verbose)

    pps: PropertyPatterns = PropertyPatterns.load(pkr,
                                                  value_options,
                                                  error_file=error_file,
                                                  verbose=args.verbose,
                                                  very_verbose=args.very_verbose,
    )

    ikr: KgtkReader = KgtkReader.open(args.input_file,
                                      error_file=error_file,
                                      mode=KgtkReaderMode.EDGE,
                                      options=reader_options,
                                      value_options=value_options,
                                      verbose=args.verbose,
                                      very_verbose=args.very_verbose)

    ppv: PropertyPatternValidator = PropertyPatternValidator.new(pps,
                                                                 ikr,
                                                                 value_options=value_options,
                                                                 error_file=error_file,
                                                                 verbose=args.verbose,
                                                                 very_verbose=args.very_verbose)

    input_row_count: int = 0
    valid_row_count: int = 0
    output_row_count: int = 0
    reject_row_count: int = 0

    okw: KgtkWriter = None
    if args.output_file is not None:
        okw = KgtkWriter.open(ikr.column_names, args.output_file)
        

    rkw: KgtkWriter = None
    if args.reject_file is not None:
        rkw = KgtkWriter.open(ikr.column_names, args.reject_file)
        

    row: typing.List[str]
    for row in ikr:
        input_row_count += 1
        result: bool = ppv.validate(input_row_count, row)
        if result:
            valid_row_count += 1
            if okw is not None:
                okw.write(row)
                output_row_count += 1
        else:
            if rkw is not None:
                rkw.write(row)
                reject_row_count += 1
                

    print("Read %d input rows, %d valid." % (input_row_count, valid_row_count), file=error_file, flush=True)
    if okw is not None:
        print("Wrote %d output rows." % (output_row_count), file=error_file, flush=True)
    if rkw is not None:
        print("Wrote %d reject rows." % (reject_row_count), file=error_file, flush=True)

    ikr.close()
    pkr.close()
    if okw is not None:
        okw.close()
    if rkw is not None:
        rkw.close()

if __name__ == "__main__":
    main()
