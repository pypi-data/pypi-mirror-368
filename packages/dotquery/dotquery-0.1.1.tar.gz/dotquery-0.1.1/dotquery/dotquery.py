import json
from urllib.parse import urlparse, parse_qs


class Proxy:
    """
    一个代理类，用于包装字典、列表、对象和字符串，提供统一的属性式访问（点操作符）。
    """

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    def _parse_string(self, s: str):
        """按顺序尝试解析字符串。"""
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            pass

        if "://" in s or s.startswith("/"):
            return urlparse(s)._asdict()

        if "=" in s and "/" not in s:
            parsed_query = parse_qs(s)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed_query.items()}

        return s

    def __getattr__(self, name: str):
        try:
            return self[name]
        except (KeyError, IndexError, TypeError):
            return Proxy(None)

    def __getitem__(self, key):
        target = self._obj
        if isinstance(target, bytes):
            try:
                target = self._parse_string(target.decode("utf-8"))
            except UnicodeDecodeError:
                target = None
        elif isinstance(target, str):
            target = self._parse_string(target)

        value = None
        if hasattr(target, "get") and callable(target.get):
            value = target.get(key)
        elif isinstance(target, (list, tuple)):
            try:
                index = int(key)
                if 0 <= index < len(target):
                    value = target[index]
            except (ValueError, TypeError):
                pass
        elif target is not None:
            value = getattr(target, str(key), None)

        return Proxy(value)

    def __setattr__(self, name, value):
        raise AttributeError(
            f"'{type(self).__name__}' object does not support item assignment."
        )

    @property
    def _(self):
        return self._obj

    def __repr__(self):
        return f"Proxy({repr(self._obj)})"

    def __str__(self):
        return str(self._obj)

    def __eq__(self, other):
        if isinstance(other, Proxy):
            return self._obj == other._
        return self._obj == other

    def __bool__(self):
        return bool(self._obj)


def assert_eq(test_name, actual, expected):
    """一个简单的辅助测试函数。"""
    print(f"--- Running Test: {test_name} ---")
    print(f"Expected: {repr(expected)}")
    # Handle case where 'actual' might be a Proxy object
    actual_value = actual._ if isinstance(actual, Proxy) else actual
    print(f"Actual  : {repr(actual_value)}")
    if actual == expected:  # Proxy.__eq__ handles comparison
        print("✅ PASSED")
    else:
        print(f"❌ FAILED: Expected {repr(expected)}, but got {repr(actual_value)}")
    print("-" * 20)


if __name__ == "__main__":
    import requests

    # 这个块中的代码只在直接运行此文件时执行 (e.g., python dotquery/dotquery.py)
    # 它不应该包含任何被其他文件导入的定义。
    print("--- Running main execution block in dotquery.py ---")

    # 准备一个 requests.Request 对象
    url = "https://example.com/api/v1/data?key=value#/profile?user=test"
    req = requests.Request(
        method="POST",
        url=url,
        json={"user": {"name": "Alex", "tags": ["dev"]}},
        headers={"Content-Type": "application/json"},
    )
    prepared_request = req.prepare()
    p_req = Proxy(prepared_request)

    # 执行断言测试
    assert_eq("URL Scheme", p_req.url.scheme, "https")
    assert_eq("Fragment Path", p_req.url.fragment.path, "/profile")
    assert_eq("Fragment Query", p_req.url.fragment.query.user, "test")
    assert_eq("Body User Name", p_req.body.user.name, "Alex")
    assert_eq("Header Content-Type", p_req.headers["Content-Type"], "application/json")
