import json
import operator
import re
from enum import Enum
from functools import reduce
from typing import Annotated, Self

from pyrand48.rand48 import Rand48

BETANUMERIC = list("0123456789bcdfghjkmnpqrstvwxz")
BETANUMERIC_COUNT = len(BETANUMERIC)


def betanumeric_decode(c):
    if c in BETANUMERIC:
        return BETANUMERIC.index(c)
    else:
        return 0


class MissingConfigurationException(Exception):
    pass


class MinterExhaustedException(Exception):
    pass


class MintOrder(Enum):
    RANDOM = 1
    SEQUENTIAL = 2
    GROWING = 3


class Response:
    DATA_FIELDS = [
        "ark",
    ]

    def __init__(self, value: dict):
        if "errors" in value:
            self.errors = value["errors"]
        if "data" in value:
            self.data = value["data"]

    def __getattr__(self, name):
        if name in self.DATA_FIELDS:
            return self.data[name]
        else:
            return None


class Minter:
    def __init__(self, configuration: dict = None):
        if configuration is None:
            raise MissingConfigurationException
        if "template" not in configuration:
            raise MissingConfigurationException
        self.template: str = configuration["template"]
        self.naan: str = configuration.get("naan")

        self.prefix: str = None
        self.premask: str = None
        self.prefix, self.premask = self.template.split(".")
        self.order_marker = self.premask[0:1]
        self.requires_checkchar: bool = self.premask[-1:] == "k"
        if self.requires_checkchar:
            self.mask: str = self.premask[1:-1]
        else:
            self.mask: str = self.premask[1:]

        self.counter: int = 0
        if "counter" in configuration:
            self.counter = configuration["counter"]
        self.total: int = self._get_total(self.mask)
        self.order: str = None
        self.active_buckets: list = []
        if self.order_marker == "r":
            self.order = MintOrder.RANDOM
            self.prng = Rand48()
            self.prng_identifier = "rand48"
            if "max_buckets_count" in configuration:
                self.max_buckets_count = configuration["max_buckets_count"]
            else:
                self.max_buckets_count = 293
            self.arks_per_bucket = int(self.total / self.max_buckets_count + 1)

            if "active_buckets" in configuration:
                self.active_buckets = configuration["active_buckets"]
            else:
                n = 0
                t = self.total
                pctr = self.arks_per_bucket
                # self.active_buckets = []
                while t > 0:
                    self.active_buckets.append(
                        {"base": n * pctr, "offset": 0, "top": min(pctr, t)}
                    )
                    t -= pctr
                    n += 1
        elif self.order_marker == "s":
            self.order = MintOrder.SEQUENTIAL
        elif self.order_marker == "z":
            self.order = MintOrder.GROWING

    def _get_weight(self, c):
        return 10 if c == "d" else BETANUMERIC_COUNT

    def _get_total(self, mask):
        return reduce(operator.mul, [self._get_weight(c) for c in list(mask)])

    def _advance_counter(self):
        if self.is_exhausted():
            raise MinterExhaustedException
        self.counter += 1

    def _get_checkchar(self, ark):
        position = 1
        total = 0
        for c in list(ark):
            total += position * betanumeric_decode(c)
            position += 1
        return BETANUMERIC[total % BETANUMERIC_COUNT]

    def _get_ark(self, number):
        pieces = []
        if self.naan is not None:
            pieces.append(self.naan + "/")
        if self.prefix is not None:
            pieces.append(self.prefix)
        pieces.append(self._get_blade(number))
        ark = "".join(pieces)
        if self.requires_checkchar:
            ark += self._get_checkchar(ark)
        return ark

    def _get_blade(self, number):
        mask = self.mask
        if self.order == MintOrder.GROWING:
            while self.counter >= self._get_total(mask):
                mask = mask[0:1] + mask

        weightable = list(mask)
        weightable.reverse()

        accu: int = 1
        weights = [accu]
        for c in weightable[:-1]:
            accu *= self._get_weight(c)
            weights.append(accu)
        weights.reverse()

        blade_pieces = []
        for weight in weights:
            blade_pieces.append(BETANUMERIC[number // weight])
            number = number % weight

        return "".join(blade_pieces)

    def mint(self):
        try:
            counter = self.counter
            if self.order == MintOrder.RANDOM:
                self.prng.srand48(self.counter)
                the_bucket = self.active_buckets[
                    int(self.prng.drand48() * len(self.active_buckets))
                ]
                the_bucket["offset"] += 1
                counter = the_bucket["base"] + the_bucket["offset"]
                if the_bucket["offset"] >= the_bucket["top"]:
                    self.active_buckets.remove(the_bucket)
            ark = self._get_ark(counter)
            self._advance_counter()
            return Response({"data": {"ark": ark}})
        except MinterExhaustedException:
            return Response({"errors": "This minter has been exhausted."})

    def is_exhausted(self):
        return self.counter >= self.total and not self.order == MintOrder.GROWING

    def to_json(self):
        minter_state = {
            "active_buckets": self.active_buckets,
            "counter": self.counter,
            "naan": self.naan,
            "template": self.template,
        }
        if self.order == MintOrder.RANDOM:
            minter_state["prng_identifier"] = self.prng_identifier
            minter_state["max_buckets_count"] = self.max_buckets_count
        return json.dumps(minter_state)

    @classmethod
    def load(cls, state: str) -> Self:
        return Minter(json.loads(state))
