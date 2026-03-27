from entities.Class import Class, EnumClass
from entities.Method import *
from entities.Variable import *


def json_deserializable(json_obj):
    # 利用 NODE_TYPE 找到对应的类
    try:
        cls = globals()[json_obj['NODE_TYPE']]  # 确保类已在全局命名空间定义

        # 创建一个空的类实例
        obj = cls()

        # 遍历 JSON 对象中的键值对，为对象设置属性
        for key, value in json_obj.items():
            if key == 'NODE_TYPE':
                continue
            if isinstance(value, dict) and 'NODE_TYPE' in value:
                # 递归处理嵌套对象
                setattr(obj, key, json_deserializable(value))
            elif isinstance(value, list):
                # 处理可能包含嵌套对象的列表
                v = [json_deserializable(item) if isinstance(item, dict) and 'NODE_TYPE' in item else item for item in
                     value]
                setattr(obj, key, v)
            else:
                # 直接为对象设置属性
                setattr(obj, key, value)
    except Exception as e:
        print(e)

    return obj
