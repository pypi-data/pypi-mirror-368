import json
import requests
from urllib.parse import urlparse, parse_qs


class Proxy:
    """
    一个代理类，用于包装字典、列表、对象和字符串，提供统一的属性式访问（点操作符）。

    - 代理字典: `proxy.key` -> `dict['key']`
    - 代理列表/元组: `proxy.0` -> `list[0]`
    - 代理对象: `proxy.attribute` -> `obj.attribute`
    - 代理字符串/字节串: 自动尝试按顺序解析 JSON、URL、URL query string。
      - JSON: '{"key": "value"}' -> proxy.key
      - URL: 'http://a.com/b?c=d' -> proxy.scheme, proxy.path, proxy.query
      - URL Query: 'key1=val1&key2=val2' -> proxy.key1

    所有返回的元素都会被再次包装为此类的实例，以支持链式访问。
    使用 `proxy._` 属性可以获取原始的、未被包装的内部对象。
    """

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    def _parse_string(self, s: str):
        """按顺序尝试解析字符串。"""
        # 1. 尝试解析 JSON
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            pass

        # 2. 尝试解析 URL (absolute or relative)
        # 包含 '://' 或以 '/' 开头的字符串被认为是 URL
        if "://" in s or s.startswith("/"):
            return urlparse(s)._asdict()

        # 3. 尝试解析 URL Query String
        # 包含 '=' 但不包含 '/' 的字符串被认为是查询参数
        if "=" in s and "/" not in s:
            parsed_query = parse_qs(s)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed_query.items()}

        # 如果所有解析都失败，返回原始字符串
        return s

    def __getattr__(self, name: str):
        """通过点操作符访问元素。"""
        try:
            return self[name]
        except (KeyError, IndexError, TypeError):
            return Proxy(None)

    def __getitem__(self, key):
        """通过下标 `[]` 访问元素，逻辑与 __getattr__ 统一。"""
        target = self._obj

        # 如果代理的对象是 bytes 或 str，先尝试解析
        if isinstance(target, bytes):
            try:
                # 先解码，再解析
                target = self._parse_string(target.decode("utf-8"))
            except UnicodeDecodeError:
                target = None  # 解码失败则无法继续
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


if __name__ == "__main__":

    def assert_eq(test_name, actual, expected):
        """辅助测试函数，比较实际值和期望值。"""
        print(f"--- Running Test: {test_name} ---")
        print(f"Expected: {repr(expected)}")
        print(f"Actual  : {repr(actual._)}")
        if actual == expected:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED: Expected {repr(expected)}, but got {repr(actual._)}")
        print("-" * 20)

    # 1. 准备一个 requests.Request 对象
    # Fragment 现在包含一个带有路径和查询的 URL 式字符串
    url = "https://example.com/api/v1/data?key=value#/profile?user=test&page=1"
    json_body = {
        "user": {"name": "Alex", "id": 123, "tags": ["dev", "test"]},
        "status": "active",
    }
    headers = {"Content-Type": "application/json", "X-Custom-Header": "Test"}

    # 使用 requests 库构造请求
    request = requests.Request(method="POST", url=url, json=json_body, headers=headers)

    # Request 对象需要被“准备”后，body 和 headers 才会最终确定
    prepared_request = request.prepare()

    # 2. 使用 Proxy 包装 prepared_request 对象
    p_req = Proxy(prepared_request)

    # 3. 执行断言测试
    print("--- Testing Proxied requests.PreparedRequest ---")

    # 测试 URL 解析
    assert_eq("URL Scheme", p_req.url.scheme, "https")
    assert_eq("URL Path", p_req.url.path, "/api/v1/data")
    assert_eq("URL Main Query", p_req.url.query.key, "value")
    assert_eq("None Query", p_req.url.query.key2, None)

    # 测试 Fragment 的嵌套解析
    fragment_str = "/profile?user=test&page=1"
    assert_eq("Fragment Full String", p_req.url.fragment, fragment_str)
    assert_eq("Fragment Path", p_req.url.fragment.path, "/profile")
    assert_eq("Fragment Query User", p_req.url.fragment.query.user, "test")
    assert_eq("Fragment Query Page", p_req.url.fragment.query.page, "1")

    # 测试 JSON Body 解析
    assert_eq("Body User Name", p_req.body.user.name, "Alex")
    assert_eq("Body Tag 1 (getattr)", getattr(p_req.body.user.tags, "1"), "test")

    # 测试 Header 访问
    assert_eq("Header Content-Type", p_req.headers["Content-Type"], "application/json")
    assert_eq("Header Custom", p_req.headers["X-Custom-Header"], "Test")
