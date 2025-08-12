from dataclasses import dataclass
import re
from typing import Union
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.native.core.engine import Component
from wowool.document.analysis.document import AnalysisDocument
import logging
from locale import atof
from wowool.annotation import Token, Concept
from wowool.annotation.token import TokenNone
from wowool.native.core import Domain
from wowool.native.core.engine import Engine
from wowool.utility.numbers import to_float
from enum import Enum
from wowool.native.core.analysis import (
    remove_pos,
    get_internal_concept,
    add_internal_concept,
    get_internal_concept_args,
    remove_internal_concept_attribute,
)
from itertools import product
from wowool.numbers.currency import currency_data, normalize_currency_data
from wowool.numbers.units import is_unit
from wowool.numbers.app_id import APP_ID

from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)


logger = logging.getLogger("wowool_numbers")


class InvalidFloatConversion(ValueError):
    pass


def literal_to_value(literal):
    return to_float(literal)


def find_reverse_index(parts):
    for i in range(len(parts), 0):
        if parts[i] != "Num-Writ":
            return i
    return 0


def iterate_prv_nxt(my_list):
    """
    create a iterator that returns.
    prev, current and the  next
    """
    prv, cur, nxt = None, iter(my_list), iter(my_list)
    next(nxt, None)

    while True:
        try:
            if prv:
                yield next(prv), next(cur), next(nxt, None)
            else:
                yield None, next(cur), next(nxt, None)
                prv = iter(my_list)
        except StopIteration:
            break


number_parts = re.compile("""[.,]""")


def unique(seq):
    retval = []
    for word in seq:
        if word not in retval:
            retval.append(word)
    return retval


def _digit_separator(comma_separator: str) -> str:
    return "." if comma_separator == "," else ","


def localize_number(literal: str, comma_separator: str = ".") -> str:
    try:
        if len(literal) > 0 and (literal[0].isdigit() or literal[0] == "-"):
            sep_sequence = number_parts.findall(literal)
            sep_sequence = sep_sequence[-2:]
            if len(sep_sequence) == 2 and sep_sequence[0] == sep_sequence[1]:
                return literal.replace(sep_sequence[0], "")
            else:
                separators = unique(sep_sequence)
                if len(sep_sequence) == 2:
                    # print(f"{separators}")
                    literal = literal.replace(separators[0], "")
                    if separators[-1] == ",":
                        literal = literal.replace(separators[-1], ".")
                elif len(sep_sequence) == 1:
                    pos = literal.rfind(sep_sequence[0])
                    size_end = len(literal) - (pos + 1)
                    _cs = comma_separator
                    if size_end != 3:
                        _cs = sep_sequence[0]
                    else:
                        # we really don't know but as the last part is size 3
                        # w assume it is a 18.001 = 18001 and not 18,001
                        _cs = "," if sep_sequence[0] == "." else "."

                    if _cs == ",":
                        literal = literal.replace(".", "")
                        literal = literal.replace(",", ".")
                    else:
                        literal = literal.replace(",", "")
    except Exception as ex:
        logger.warning(f"Exception localize_number:{literal}, {ex}")
    return literal


class Str2NrHookReturnValues(Enum):
    Continue = 1
    KeepGoing = 2


DEFAULT_CURRENCY_UNIT_RULE = """
rule:{ MoneyAmount[{ <>? +currency}=CurrencyUnit Number]};
rule:{ MoneyAmount[ Number { +currency}=CurrencyUnit]};
"""


class base_numbers:
    def str2nr(self, prv, cur, nxt, result_stack, nrof_adds):
        return Str2NrHookReturnValues.KeepGoing

    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord") or token.lemma == "-"
        else:
            return token.pos == "Conj-Coord" or token.lemma == "-"

    def is_number_1(self, token):
        return False

    def wowool_source(self) -> str:
        return f"""rule:{{ Num+ (("and"|"-") Num+ )*}} = Number;
{DEFAULT_CURRENCY_UNIT_RULE}"""


class spanish_numbers(base_numbers):
    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord")
        else:
            return token.pos == "Conj-Coord"

    def is_number_1(self, token):
        return token.literal == "uno" or token.literal == "un"

    def wowool_source(self):
        return f"""rule:{{ Num+ (("y"|"-"|"un")+ Num+ )*}} = Number;
{DEFAULT_CURRENCY_UNIT_RULE}"""


class portuguese_numbers(base_numbers):
    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord")
        else:
            return token.pos == "Conj-Coord"

    def is_number_1(self, token):
        return token.literal == "umo" or token.literal == "um"

    def wowool_source(self):
        return f"""rule:{{ ("um")? Num+ (("e"|"-"|"um")+ Num+ )*}} = Number;
{DEFAULT_CURRENCY_UNIT_RULE}"""


class french_numbers(base_numbers):
    def str2nr(self, prv, cur, nxt, result_stack, nrof_adds):
        if cur == "4" and nxt and nxt == "20":
            return Str2NrHookReturnValues.Continue

        if cur and cur == "20" and prv and prv == "4":
            result_stack.append(80)
            return Str2NrHookReturnValues.Continue
        return Str2NrHookReturnValues.KeepGoing

    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord")
        else:
            return token.pos == "Conj-Coord"

    def is_number_1(self, token):
        return token.literal == "un"

    def wowool_source(self):
        return """rule:{ Num+ (("et"|"-")+ Num+ )*} = Number;"""


class danish_numbers(base_numbers):
    def wowool_source(self):
        return """rule:{ (Num)+ ("og" Num+ )* } = Number;"""

    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord")
        else:
            return token.pos == "Conj-Coord"


class norwegian_numbers(base_numbers):
    def wowool_source(self):
        return """rule:{ (Num)+ ("og" Num+ )* } = Number;"""

    def is_conj_coord(self, token):
        if isinstance(token, Token):
            return token.has_pos("Conj-Coord")
        else:
            return token.pos == "Conj-Coord"


class dutch_numbers(base_numbers):
    def wowool_source(self):
        return f"""rule:{{ Num+ (("en"|"-") Num+ )* }} = Number;
{DEFAULT_CURRENCY_UNIT_RULE}"""


def str2nr(number, language_hooks=None, comma_separator: str = "."):
    """convert a string to a number.
    input format of the string :
    "3#0#60#x1000#4#x100#1#0#50" will result in a value of 63451
    The written number is first converted using general morphological dictionaries,
    to convert the written string into this input format:
    ((number|multipliers)#)+
    multipliers are : x[10,100,1000,....]
    When facing big numbers we need to first add(sum) all the values that have smaller multipliers then de one we are
    currently processing.
    ex   : 50 tn four thousand three hundred bn
         : ['50', 'x1000000000000', '4', 'x1000', '3', 'x100', 'x1000000000']
        50                              [ 50 ]
        x1000000000000                  [ 50000000000000 ]
        4                               [ 50000000000000, 4 ]
        x1000                           [ 50000000000000, (4x1000) = 4000  ]
        3                               [ 50000000000000, 4000 , 3  ]
        x100                            [ 50000000000000, 4000 , (3x100) = 300  ]
        x1000000000                     [ 50000000000000, (4000 + 300) x1000000000  = 4300000000000 ] --> this is the case we need to go back until
                                                                                                          we have values the smaller then the multiplier
        total                           sum ([ 50000000000000, 4300000000000 ])
                                        = 54300000000000

    """  # noqa

    # dbg: logger.debug(f"number: {number}")
    number = localize_number(number, comma_separator)
    number = re.sub("#en", "#0", number)

    result = 0.0
    chunks = number.split("#")
    # dbg: logger.debug(f"chunks: {chunks}")

    intermediate_result = 0
    ignore_next = False
    nrof_adds = 0

    result_stack = []
    sum_stack = []
    if len(chunks) > 0:
        if chunks[0][0] == "x":
            chunks.insert(0, "1")

    for prv, cur, nxt in iterate_prv_nxt(chunks):
        if len(cur) <= 0 or cur == "0" or cur[0] == "-" or cur[0] == ":":
            continue

        if ignore_next:
            ignore_next = False
            continue

        # dbg: logger.debug(f"part: {cur} ")

        if language_hooks:
            if language_hooks.str2nr(prv, cur, nxt, sum_stack, nrof_adds) == Str2NrHookReturnValues.Continue:
                continue

        if cur and cur[0].isdigit():
            # we have directly a digit , so we can convert it directly
            try:
                if cur[-1] == "%":
                    cur = cur[:-1]
                sum_stack.append(float(cur))
            except ValueError:
                raise InvalidFloatConversion

            # dbg: logger.debug(f" - digit: {sum_stack}")

        elif cur and cur[0] == "x":
            # dbg: logger.debug(f" - multiply: {result_stack=} {sum_stack=}")
            multiplier = float(cur[1:])
            # x100#x1000
            # if multiplier > multiplier_prv:
            # dbg: logger.debug(f" - bigger multiplier: {multiplier=} {nrof_adds=} {result_stack=}")
            new_stack = []
            for value_ in reversed(result_stack):
                if value_ < multiplier:
                    new_stack.append(result_stack.pop())
            new_stack.extend(sum_stack)
            if not new_stack:
                new_stack = [1]
            intermediate_result = sum(new_stack) * multiplier
            sum_stack = []
            result_stack.append(intermediate_result)
            # dbg: logger.debug(f" - result_stack: {result_stack}")
            intermediate_result = 0
        elif cur and cur[0] == "^":
            result = sum(sum_stack)
            sum_stack = []
            result = pow(result, atof(cur[1:]))
            logger.debug(f" = result_stack: {result} , {cur[1:]=}")
            sum_stack = [result]
        else:
            raise RuntimeError(f"Could not resolve part '{cur}' ")

    result_stack.extend(sum_stack)
    # dbg: logger.debug(f" = result_stack: {result_stack}")
    result = sum(result_stack)
    # dbg: logger.debug(f"result: {number} = {result}")

    return result


language_hooks = {
    "french": french_numbers(),
    "spanish": spanish_numbers(),
    "portuguese": portuguese_numbers(),
    "danish": danish_numbers(),
    "norwegian": norwegian_numbers(),
    "dutch": dutch_numbers(),
}

main_si_names = ["m", "g", "l", "b"]
prefix_si_names = ["", "d", "c", "k", "n", "m", "μ"]

know_si_names = set([item[0] + item[1] for item in product(prefix_si_names, main_si_names)])
known_currencies = set(["dollar", "euro", "yen"])

interesting_stuff_list = set(["Number", "CurrencyUnit", "MoneyAmount", "Unit"])


def interesting_stuff(concept) -> bool:
    return concept.uri in interesting_stuff_list


@dataclass
class Context:
    document: AnalysisDocument
    diagnostics: Diagnostics


@dataclass
class Number:
    value: str
    initial_token: Token
    last_token: Token


def contains(text, chars):
    for special in chars:
        if special in text:
            return True
    return False


number_split = re.compile(r"\.|,")


def is_invalid_number(number) -> bool:
    # if contains(number, " "):
    #     for part in number.split(" "):
    #         if part.isdigit():
    #             return True
    #     return False

    if contains(number, ":") or len(number) == 1:
        return True

    parts = number_split.split(number)
    if len(parts) >= 3:
        if len(parts[0]) >= 3:
            return True

        for part in parts[1:-1]:
            if len(part) != 3:
                return True

    return False


def get_currency_unit_index(concepts, idx):
    nrof_concepts = len(concepts)
    _idx = idx + 1
    if _idx < nrof_concepts and concepts[_idx] is None:
        _idx += 1
    if _idx < nrof_concepts and (concepts[_idx].uri == "CurrencyUnit"):
        return _idx
    else:
        _idx = idx - 1
        if _idx > 0 and (concepts[_idx].uri == "CurrencyUnit" or concepts[_idx].uri == "MoneyAmount"):
            return _idx
    return None


def fix_invalid_money_amount(document: AnalysisDocument, concepts, idx):
    nrof_concepts = len(concepts)
    ma_idx = idx + 1
    if ma_idx < nrof_concepts and concepts[ma_idx].uri == "MoneyAmount" and concepts[idx].begin_offset < concepts[ma_idx].begin_offset:
        currency_idx = ma_idx + 1
        if currency_idx < nrof_concepts and (
            concepts[currency_idx].uri == "CurrencyUnit" or concepts[currency_idx].uri == "CurrencySumbol"
        ):
            internal_concept = add_internal_concept(
                document.analysis,
                concepts[idx].begin_offset,
                concepts[currency_idx].end_offset,
                "MoneyAmount",
            )
            concepts[ma_idx] = None
            return internal_concept


def in_range(value, start, end):
    return start <= value <= end


def get_money_amount_annotation(concepts, number_idx, currency_idx):
    nrof_concepts = len(concepts)
    assert number_idx < nrof_concepts
    assert currency_idx < nrof_concepts

    _number = concepts[number_idx]
    _currency = concepts[currency_idx]

    retval = []
    if _currency.begin_offset < _number.begin_offset:
        # euro 200
        if in_range(_number.begin_offset, _currency.end_offset, _currency.end_offset + 4):
            retval.append(_currency.begin_offset)
            retval.append(_number.end_offset)
            return retval
    else:
        # 200 euro
        if in_range(_currency.begin_offset, _number.end_offset, _number.end_offset + 4):
            retval.append(_number.begin_offset)
            retval.append(_currency.end_offset)
            return retval

    return []


def get_currency_code(currency_words: list):
    for currency in currency_words:
        key = currency.lower()
        if key in normalize_currency_data:
            return normalize_currency_data[key]


def resolve_currency_symbol(currency: Concept) -> None | list:
    if currency.uri == "CurrencyUnit":
        if "canonical" in currency._attributes:
            return [currency._attributes["canonical"][0]]
        else:
            return [currency.literal, currency.lemma]
    elif currency.uri == "MoneyAmount":
        # AU$ or A$
        tokens = []

        for token in Token.iter(currency):
            if token.has_pos("Num"):
                tokens = []
                break
            tokens.append(token.lemma)
            if "currency" in token.properties:
                break

        if tokens:
            return ["".join(tokens).upper()]
        else:
            #  lets look from the back
            for token in reversed([t for t in Token.iter(currency)]):
                if token.has_pos("Num"):
                    break
                tokens.append(token.lemma)
            return [" ".join(tokens[::-1])]


def get_concept_unit(concepts, number_idx) -> Union[str, None]:
    nrof_concepts = len(concepts)
    assert number_idx < nrof_concepts
    _idx = number_idx + 1
    if _idx < nrof_concepts and concepts[_idx].uri == "Unit":
        concept = concepts[_idx]
        if "canonical" in concept.attributes:
            return concept.canonical
        else:
            for tk in Token.iter(concept):
                for prop in tk.properties:
                    if is_unit(prop):
                        return prop

            return concept.lemma
    return None


def find_currency_tokens(concept: Concept) -> list:
    for token in Token.iter(concept):
        if "currency" in token.properties:
            return [token.literal, token.lemma, token.lemma.title()]


class Numbers(Component):
    """ExchangeRates component that can be use in a Pipeline"""

    ID = APP_ID

    def __init__(
        self,
        source: Union[str, None] = None,
        language: str = "english",
        comma_separator: str = ".",
        engine: Union[Engine, None] = None,
    ):
        """Initialize the Numbers application."""
        super(Numbers, self).__init__(engine)
        self.language_hook = language_hooks.get(language, base_numbers())
        wowool_source = self.language_hook.wowool_source() if source is None else source
        self.number_domain = Domain(source=wowool_source, engine=self.engine, cache=(source is not None))
        self.comma_separator = comma_separator

    def get_number_parts(self, number):
        number_parts = ""
        initial_token = TokenNone
        last_token = TokenNone

        for token in Token.iter(number):
            if not initial_token:
                initial_token = token
            last_token = token

            md = token.get_morphology("Num-Writ")
            if md:
                if md.morphology:
                    for component in md.morphology:
                        if component.pos == "Num-Writ":
                            number_parts += "#" + component.lemma
                else:
                    number_parts += "#" + md.lemma
            else:
                md = token.get_morphology("Num")
                if md:
                    number_parts += "#" + md.lemma
                else:
                    if self.language_hook.is_conj_coord(token):
                        number_parts += "#0"
                    elif self.language_hook.is_number_1(token):
                        number_parts += "#1"
                    # ex : quarante-deux
                    elif token.literal == "-":
                        pass
                    else:
                        return None, None, None
        return number_parts, initial_token, last_token

    def make_number(self, context: Context, number, number_parts, initial_token, last_token):
        number_value = str2nr(number_parts[1:], self.language_hook, self.comma_separator)
        internal_concept = get_internal_concept(context.document.analysis, number)
        if internal_concept:
            internal_concept.add_attribute("canonical", str(number_value))
            remove_pos(
                context.document.analysis,
                number.begin_offset,
                number.end_offset,
                "Num-Writ",
            )

        return Number(number_value, initial_token, last_token)

    def resolve_numbers(self, context: Context, number):
        number_parts, initial_token, last_token = self.get_number_parts(number)
        if number_parts:
            try:
                return self.make_number(context, number, number_parts, initial_token, last_token)
            except InvalidFloatConversion:
                # ignore this exception, this can happen when trying to
                pass
            except Exception as parts_missing:
                logger.exception(parts_missing)
                context.diagnostics.add(
                    Diagnostic(
                        context.document.id,
                        f"Could not resolve sections '{number.literal}', Check if you have the 'number.language' in your pipeline",
                        DiagnosticType.Warning,
                    )
                )
        else:
            return None

    @property
    def concepts(self):
        return interesting_stuff_list

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        Normalize money amounts collect numbers and unit's

        :param document:  The document we want to enrich with phone number information.
        :type document: AnalysisDocument

        :returns: The given document with the new annotations. See the :ref:`json format <json_apps_numbers>`
        """
        context = Context(document, diagnostics)
        document = self.number_domain(document)
        assert document.analysis is not None, f"Missing analysis for {document.id}"
        document.analysis.reset()

        results = []
        for sentence in document.analysis:
            concepts = [c for c in Concept.iter(sentence, interesting_stuff)]

            nrof_concepts = len(concepts)
            idx = 0
            while idx < nrof_concepts:
                concept = concepts[idx]
                if concept is None:
                    idx += 1
                    continue

                if concept.uri == "Number":
                    clean_nr = concept.literal
                    if clean_nr.isdigit():
                        tokens = concept.tokens
                        nr = Number(int(clean_nr), tokens[0], tokens[-1])
                    else:
                        if is_invalid_number(clean_nr):
                            idx += 1
                            internal_concept = get_internal_concept(document.analysis, concept)
                            if internal_concept:
                                remove_internal_concept_attribute(document.analysis, internal_concept)
                            continue

                        nr = self.resolve_numbers(context, concept)

                    if not nr:
                        if "-" not in concept.literal:
                            logger.warning(
                                f"Could not resolve number, check if you have the numbers.language in your pipeline, '{concept.literal}'"
                            )
                            context.diagnostics.add(
                                Diagnostic(
                                    document.id,
                                    "Could not resolve number, check if you have the numbers.language in your pipeline",
                                    DiagnosticType.Warning,
                                )
                            )
                        idx += 1
                        continue

                    unit_canonical = get_concept_unit(concepts, idx)
                    token_behind_the_number = Token.next(sentence, nr.last_token)
                    if token_behind_the_number and "unit" in token_behind_the_number.properties or unit_canonical:
                        unit_concept = get_internal_concept_args(
                            document.analysis,
                            nr.initial_token.begin_offset,
                            token_behind_the_number.end_offset,
                            "Unit",
                        )
                        if not unit_concept:
                            unit_concept = add_internal_concept(
                                document.analysis,
                                nr.initial_token.begin_offset,
                                token_behind_the_number.end_offset,
                                "Unit",
                            )

                        unit_concept.add_attribute("amount", str(nr.value))
                        has_been_added = False
                        if unit_canonical:
                            unit_concept.add_attribute("si", unit_canonical)
                        else:
                            for property in token_behind_the_number.properties:
                                if property in know_si_names:
                                    unit_concept.add_attribute("si", property)
                                    has_been_added = True
                            if not has_been_added:
                                unit_concept.add_attribute("si", token_behind_the_number.lemma)

                    # internal_currency_concept = fix_invalid_money_amount(document, concepts, idx)
                    internal_currency_concept = None

                    currency_idx = get_currency_unit_index(concepts, idx)
                    values = currency_words = None
                    if currency_idx is not None:
                        # found a currency concept.
                        currency = concepts[currency_idx]
                        currency_words = resolve_currency_symbol(currency)
                        values = get_money_amount_annotation(concepts, idx, currency_idx)
                    else:
                        if len(concepts) > 0 and concepts[0].uri == "MoneyAmount":
                            currency_words = find_currency_tokens(concepts[0])
                            values = get_money_amount_annotation(concepts, idx, 0)
                    if currency_words and values:
                        # logger.debug(f"currency : {nr.value} {currency_words}")
                        begin_offset, end_offset = values
                        # logger.debug(f"currency : {begin_offset=} {end_offset=}")
                        if not internal_currency_concept:
                            # print(document)
                            internal_currency_concept = get_internal_concept_args(
                                document.analysis,
                                begin_offset,
                                end_offset,
                                "MoneyAmount",
                            )
                        if not internal_currency_concept:
                            internal_currency_concept = add_internal_concept(
                                document.analysis,
                                begin_offset,
                                end_offset,
                                "MoneyAmount",
                            )

                            if internal_currency_concept:
                                # safty net in case we could not add the concept in the cpp layer
                                continue
                        internal_currency_concept.add_attribute("amount", str(nr.value))

                        cc = get_currency_code(currency_words)
                        if cc:
                            internal_currency_concept.add_attribute("code", cc)
                            if cc in currency_data:
                                internal_currency_concept.add_attribute("name", currency_data[cc]["name"])
                        elif currency_words and len(currency_words) > 0:
                            internal_currency_concept.add_attribute("currency", currency_words[0])

                idx += 1

        # invalidate the document data, this will make sure we request the data back from the cpp layer
        document.analysis.reset()
        document.add_results(self.ID, results)

        return document


if __name__ == "__main__":
    print("---------->>>>>>>: ", localize_number("123,80"))
