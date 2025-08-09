import json

class DotDict:
    __slots__ = ("_data",)

    def __init__(self, data=None):
        object.__setattr__(self, "_data", {})
        if isinstance(data, dict):
            for k, v in data.items():
                self._data[k] = self._wrap(v)

    def _wrap(self, v):
        if isinstance(v, dict):
            return DotDict(v)
        if isinstance(v, list):
            return [self._wrap(i) for i in v]
        return v

    # 自动“生长”层级：访问不存在的键时创建子节点
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._data:
            self._data[name] = DotDict()
        return self._data[name]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = self._wrap(value)

    def __delattr__(self, name):
        del self._data[name]

    # 兼容 dict 行为
    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self.__setattr__(key, value)
    def __delitem__(self, key): del self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)

    def to_dict(self):
        def unwrap(v):
            if isinstance(v, DotDict): return v.to_dict()
            if isinstance(v, list): return [unwrap(i) for i in v]
            return v
        return {k: unwrap(v) for k, v in self._data.items()}
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)
    
    def __repr__(self):
        return f"Dot({self.to_dict()})"
    
    