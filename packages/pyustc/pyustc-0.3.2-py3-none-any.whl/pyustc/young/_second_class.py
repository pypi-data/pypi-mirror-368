try:
    from typing import Self
except:
    from typing_extensions import Self

from ._service import get_service
from ._user import User 
from ._filter import TimePeriod, Module, Department, Label, SCFilter

class Status:
    status_list = {
        26: "报名中",
        28: "报名已结束",
        30: "学时公示中",
        31: "追加学时公示",
        32: "公示已结束",
        33: "学时申请中",
        34: "学时审核通过",
        35: "学时驳回",
        40: "结项"
    }
    def __init__(self, code: int):
        self.code = code

    @property
    def text(self):
        return self.status_list.get(self.code)

    def __repr__(self):
        return f"<Status {self.code} {repr(self.text)}>"

class SignInfo:
    def __init__(self, college: str, classes: str, phone: str, email: str = "", remarks: str = ""):
        self.college = college
        self.classes = classes
        self.phone = phone
        self.email = email
        self.remarks = remarks

    @classmethod
    def get_self(cls):
        user = User.get()
        return cls(user.college, user.classes, user.phone)

    def json(self):
        return {
            "college": self.college,
            "classes": self.classes,
            "phone": self.phone,
            "email": self.email,
            "remarks": self.remarks
        }

class SecondClass:
    _second_class_cache = dict[str, Self]()
    def __new__(cls, id: str, *args, **kwargs):
        if id in cls._second_class_cache:
            return cls._second_class_cache[id]
        else:
            obj = super().__new__(cls)
            cls._second_class_cache[id] = obj
            return obj

    def __init__(self, id: str, data: dict[str] = None):
        self.id = id
        self.data = {}
        self.update(data)
        self._children = list[type(self)]()

    @classmethod
    def from_dict(cls, data: dict[str]):
        return cls(data["id"], data = data)

    @classmethod
    def _fetch(cls, name: str, filter: SCFilter, url: str, size: int):
        if not filter:
            filter = SCFilter()
        if name and not filter.name:
            filter.name = name
        params = filter.generate_params()
        for i in get_service().page_search(url, params, -1, size):
            sc = cls.from_dict(i)
            if filter.check(sc, only_strict = True):
                yield sc

    @classmethod
    def find(
            cls,
            name: str = None,
            filter: SCFilter = None,
            apply_ended: bool = False,
            expand_series: bool = False,
            max: int = -1,
            size: int = 20
        ):
        """
        Find the second class that meets the conditions.

        Arguments:
            name: The name of the second class. If `filter.name` is set, this argument will be ignored.
            filter: The filter for the second class, which will be used for both the series and the children.
            apply_ended: Whether to show the second class that has ended or not.
            expand_series: Whether to expand the series to get all second classes in the series.
        """
        if not max: return
        url = f"item/scItem/{'endList' if apply_ended else 'enrolmentList'}"
        for sc in cls._fetch(name, filter, url, size):
            if expand_series and sc.is_series:
                for i in sc.children:
                    if filter.check(i, only_strict = True) and (apply_ended ^ (i.status.code <= 26)):
                        yield i
                        max -= 1
                    if not max:
                        break
            else:
                yield sc
                max -= 1
            if not max:
                break

    @classmethod
    def get_participated(
            cls,
            name: str = None,
            filter: SCFilter = None,
            max: int = -1,
            size: int = 20
        ):
        """
        Get the specific second class list that the user has participated in.
        """
        if not max: return
        for sc in cls._fetch(name, filter, "item/scParticipateItem/list", size):
            del sc.data["applyNum"]
            yield sc
            max -= 1
            if not max:
                break

    @property
    def name(self) -> str:
        return self.data["itemName"]

    @property
    def status(self):
        return Status(self.data["itemStatus"])

    @property
    def create_time(self):
        return TimePeriod._strptime(self.data["createTime"])

    @property
    def apply_time(self):
        return TimePeriod(self.data["applySt"], self.data["applyEt"])

    @property
    def hold_time(self):
        return TimePeriod(self.data["st"], self.data["et"])

    @property
    def tel(self) -> str:
        return self.data["tel"]

    @property
    def valid_hour(self) -> float:
        return self.data["validHour"]

    @property
    def apply_num(self) -> int:
        if "applyNum" not in self.data:
            self.update()
        return self.data["applyNum"]

    @property
    def apply_limit(self) -> int:
        return self.data["peopleNum"]

    @property
    def applied(self) -> bool:
        return self.data["booleanRegistration"] == 1

    @property
    def applyable(self):
        """
        This method will check the status and the number of applicants.
        """
        return self.status.code == 26 and not self.applied and self.apply_num < (self.apply_limit or 0)

    @property
    def need_sign_info(self) -> bool:
        return self.data["needSignInfo"] == "1"

    @property
    def module(self):
        if "moduleName" not in self.data:
            self.update()
        return Module(self.data["module"], self.data["moduleName"])

    @property
    def department(self):
        if "businessDeptName" not in self.data:
            self.update()
        return Department(self.data["businessDeptId"], self.data["businessDeptName"], level = -1)

    @property
    def labels(self):
        if "lableNames" not in self.data:
            self.update()
        return [Label(i, j) for i, j in zip(self.data["itemLable"].split(","), self.data["lableNames"])]

    @property
    def conceive(self) -> str:
        return self.data["conceive"]

    @property
    def is_series(self) -> bool:
        return self.data["itemCategory"] == "1"

    @property
    def children(self):
        if self._children or not self.is_series:
            return self._children
        url = "item/scItem/selectSignChirdItem"
        params = {
            "id": self.id
        }
        try:
            self._children = [self.from_dict(i) for i in get_service().get_result(url, params)]
            return self._children
        except RuntimeError as e:
            e.args = ("Failed to get children",)
            raise e

    def update(self, data: dict[str] = None):
        if not data:
            url = "item/scItem/queryById"
            params = {
                "id": self.id
            }
            try:
                data = get_service().get_result(url, params)
            except RuntimeError as e:
                e.args = ("Failed to update",)
                raise e
        self.data.update(data)

    def get_applicants(self, max: int = -1, size: int = 50):
        url = "item/scItemRegistration/list"
        params = {
            "itemId": self.id
        }
        for i in get_service().page_search(url, params, max, size):
            yield str(i["username"])

    def apply(self, force: bool = False, auto_cancel: bool = False, sign_info: SignInfo = None) -> bool:
        """
        Apply for this second class.

        Arguments:
            force: Whether to force apply even if the second class is not applyable.
            auto_cancel: Whether to cancel the application with time conflict and apply again.
            sign_info: The sign info for the second class. If `need_sign_info` is False, this argument will be ignored.
        """
        if not (force or self.applyable):
            return False
        url = f"mobile/item/enter/{self.id}"
        data = get_service().request(
            url, "post",
            json=(sign_info or SignInfo.get_self()).json() if self.need_sign_info else {}
        )
        if data["success"]: return True
        if auto_cancel and "时间冲突" in data["message"]:
            for i in SecondClass.get_participated(
                filter = SCFilter(time_period = self.hold_time)
            ):
                i.cancel_apply()
            return self.apply(force)
        raise RuntimeError(data["message"])

    def cancel_apply(self) -> bool:
        """
        Cancel the application.
        """
        url = f"mobile/item/cancellRegistration/{self.id}"
        data = get_service().request(url, "post")
        if data["success"]: return True
        raise RuntimeError(data["message"])

    def __repr__(self):
        if self.is_series:
            return f"<SecondClass {repr(self.name)} Series>"
        return f"<SecondClass {repr(self.name)}>"
