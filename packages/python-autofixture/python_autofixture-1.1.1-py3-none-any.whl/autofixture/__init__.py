import datetime
import decimal
import typing
import uuid
from decimal import Decimal
from enum import Enum
import random as rand
from types import NoneType

from autofixture.exceptions import AutoFixtureException

T = typing.TypeVar("T")


class AutoFixture:

    def create_many_dict(self, dto,
                         ammount,
                         seed=None,
                         num=None,
                         nest=0,
                         list_limit=100):
        many = self.create_many(dto=dto,
                                ammount=ammount,
                                seed=seed,
                                num=num,
                                nest=nest,
                                list_limit=list_limit)
        return list(map(lambda x: x.__dict__, many))

    def create_dict(self, dto,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        return self.create(dto=dto,
                           seed=seed,
                           num=num,
                           nest=nest,
                           list_limit=list_limit).__dict__

    def create_many(self, dto,
                    ammount,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        list_of_dtos = []
        for i in range(0, ammount):
            list_of_dtos.append(self.create(dto=dto,
                                            seed=seed,
                                            num=num,
                                            nest=nest,
                                            list_limit=list_limit))
        return list_of_dtos

    def create(self, dto: typing.Type[T],
               seed=None,
               num=None,
               nest=0,
               list_limit=10) -> T:
        self.__validate_predictable_data(num, seed)

        try:
            new_value = dto()
        except TypeError:
            raise AutoFixtureException("class must empty ctor, if a dataclass, must have fields initialised to "
                                       "sensible defaults or None")

        is_predictable_data = seed is not None and num is not None

        members = all_annotations(cls=dto).items()
        for (key, _type) in members:

            if (getattr(new_value, key) is None) or (
                    typing.get_origin(_type) is list and getattr(new_value, key) == []):

                if typing.get_origin(_type) is typing.Union:
                    args = typing.get_args(_type)
                    non_none_args = [a for a in args if a is not NoneType]
                    if len(non_none_args) == 1:
                        _type = non_none_args[0]

                if _type is str:
                    self.__generate_string_field(is_predictable_data, key, new_value, seed)

                if _type is bool:
                    self.__generate_bool_field(is_predictable_data, key, new_value, num)

                if _type == datetime.datetime:
                    self.__generate_datetime_field(is_predictable_data, key, new_value, num)

                if _type is int:
                    self.__generate_int_field(is_predictable_data, key, new_value, num)

                if _type is float:
                    self.__generate_float_field(is_predictable_data, key, new_value, num)

                if _type is Decimal:
                    self.__generate_decimal_field(is_predictable_data, key, new_value, num)

                if _type == list[str]:
                    self.__generate_str_list_field(is_predictable_data, key, new_value, num, seed, list_limit)

                if _type == list[int]:
                    self.__generate_int_list_field(is_predictable_data, key, new_value, num, list_limit)

                if _type == list[bool]:
                    self.__generate_bool_list_field(is_predictable_data, key, new_value, num, list_limit)

                if _type == list[datetime.datetime]:
                    self.__generate_datetime_list_field(is_predictable_data, key, new_value, num, list_limit)

                if _type == list[float]:
                    self.__generate_float_list_field(is_predictable_data, key, new_value, num, list_limit)

                if _type == list[decimal.Decimal]:
                    self.__generate_decimal_list_field(is_predictable_data, key, new_value, num, list_limit)

                if type(_type) is type(Enum):
                    self.__generate_random_enum_field(_type, is_predictable_data, key, new_value, num)


                if has_type_hints(_type):
                    self.__generate_class_field(_type, key, nest, new_value, num, seed)

                if typing.get_origin(_type) is list:
                    arg = typing.get_args(_type)[0]
                    if type(arg) is type(Enum):
                        self.__generate_list_of_enums_field(arg, is_predictable_data, key, new_value, num, list_limit)
                    if bool(typing.get_type_hints(arg)):
                        self.__generate_class_list(arg, is_predictable_data, key, nest, new_value, num, seed,
                                                   list_limit)

        return new_value

    def __generate_class_field(self, _type, key, nest, new_value, num, seed):
        setattr(new_value, key, self.create(dto=_type,
                                            seed=seed,
                                            num=num,
                                            nest=nest + 1))

    def __generate_class_list(self, _type, is_predictable_data, key, nest, new_value, num, seed, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(self.create(dto=_type,
                                                          seed=seed,
                                                          num=num,
                                                          nest=nest + 1))
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(self.create(dto=_type,
                                                          seed=seed,
                                                          num=num,
                                                          nest=nest + 1))
        setattr(new_value, key, value_for_given_member)

    def __generate_list_of_enums_field(self, _type, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                enum_iterable = list(_type)
                length = len(enum_iterable)
                index = num % length
                value_for_given_member.append(enum_iterable[index])
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(rand.choice(list(_type)))
        setattr(new_value, key, value_for_given_member)

    def __generate_random_enum_field(self, _type, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            enum_iterable = list(_type)
            length = len(enum_iterable)
            index = num % length
            value_for_given_member = enum_iterable[index]
        else:
            value_for_given_member = rand.choice(list(_type))
        setattr(new_value, key, value_for_given_member)

    def __generate_datetime_list_field(self, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(datetime.datetime(2, 2, 2, 2, 2, 2))
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(datetime.datetime.utcnow())
        setattr(new_value, key, value_for_given_member)

    def __generate_bool_list_field(self, is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(bool(num))
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(rand.choice([True, False]))
        setattr(new_value, key, value_for_given_member)

    def __generate_datetime_field(self, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = datetime.datetime(num, num, num, num, num, num)
        else:
            value_for_given_member = datetime.datetime.utcnow()
        setattr(new_value, key, value_for_given_member)

    def __generate_bool_field(self, is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = bool(num)
        else:
            value_for_given_member = rand.choice([True, False])
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_float_list_field(is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                trailing_decimals = ""
                for i in range(0, num):
                    trailing_decimals = f"{trailing_decimals}{num}"
                value_for_given_member_item = float(f"{num}.{trailing_decimals}")
                value_for_given_member.append(value_for_given_member_item)
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(rand.uniform(0, 100))
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_decimal_list_field(is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                trailing_decimals = ""
                for i in range(0, num):
                    trailing_decimals = f"{trailing_decimals}{num}"
                value_for_given_member_item = float(f"{num}.{trailing_decimals}")
                value_for_given_member.append(Decimal(str(value_for_given_member_item)))
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(Decimal(str(rand.uniform(0, 100))))
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_int_list_field(is_predictable_data, key, new_value, num, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member.append(num + i)
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member.append(rand.randint(0, 100))
        setattr(new_value, key, value_for_given_member)

    def __generate_str_list_field(self, is_predictable_data, key, new_value, num, seed, list_limit):
        if is_predictable_data:
            value_for_given_member = []
            for i in range(0, num):
                value_for_given_member_item = key
                value_for_given_member_item = f"{value_for_given_member_item}{seed}{i}"
                value_for_given_member.append(value_for_given_member_item)
        else:
            value_for_given_member = []
            for i in range(0, rand.randint(0, list_limit)):
                value_for_given_member_item = key
                value_for_given_member_item = f"{value_for_given_member_item}{self.__generate_random_seed()}"
                value_for_given_member.append(value_for_given_member_item)
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_random_seed() -> str:
        return str(uuid.uuid4()).split("-")[0]

    @staticmethod
    def __validate_predictable_data(num, seed):
        if seed is not None and num is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")
        if seed is not None and num is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")

    @staticmethod
    def __generate_float_field(is_predictable_data, key, new_value, num):
        if is_predictable_data:
            trailing_decimals = ""
            for i in range(0, num):
                trailing_decimals = f"{trailing_decimals}{num}"
            value_for_given_member = float(f"{num}.{trailing_decimals}")
        else:
            value_for_given_member = rand.uniform(0, 100)
        setattr(new_value, key, value_for_given_member)

    @staticmethod
    def __generate_decimal_field(is_predictable_data, key, new_value, num):
        if is_predictable_data:
            trailing_decimals = ""
            for i in range(0, num):
                trailing_decimals = f"{trailing_decimals}{num}"
            value_for_given_member = float(f"{num}.{trailing_decimals}")
        else:
            value_for_given_member = rand.uniform(0, 100)
        setattr(new_value, key, Decimal(str(value_for_given_member)))

    @staticmethod
    def __generate_int_field(is_predictable_data, key, new_value, num):
        if is_predictable_data:
            value_for_given_member = num
        else:
            value_for_given_member = rand.randint(0, 100)
        setattr(new_value, key, value_for_given_member)

    def __generate_string_field(self, is_predictable_data, key, new_value, seed):
        value_for_given_member = key
        if is_predictable_data:
            value_for_given_member = f'{value_for_given_member}{seed}'
        else:
            value_for_given_member = f'{value_for_given_member}{self.__generate_random_seed()}'
        setattr(new_value, key, value_for_given_member)


def all_annotations(cls):
    d = {}
    for c in cls.mro():
        try:
            d.update(**c.__annotations__)
        except AttributeError:
            # object, at least, has no __annotations__ attribute.
            pass
    return d

def has_type_hints(t):
    origin = typing.get_origin(t)
    if origin is not None:
        # It's a generic like list[LayoutItem], get the inner type(s)
        args = typing.get_args(t)
        # For simplicity, just check the first arg recursively
        if args:
            return has_type_hints(args[0])
        else:
            return False
    else:
        # Normal class/type, try to get hints safely
        try:
            return bool(typing.get_type_hints(t))
        except Exception:
            return False