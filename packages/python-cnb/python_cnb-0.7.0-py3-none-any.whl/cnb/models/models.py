from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, ValidationError

class CNBBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name = True,
        arbitrary_types_allowed=True,
        protected_namespaces=(),  # 防止与父类属性冲突
        defer_build=True  # 延迟模型构建
    )
    def to_dict(self) -> dict:
        """将模型实例转换为字典，兼容Pydantic v2+"""
        return self.model_dump()
    @classmethod
    def safe_parse(cls, data: Dict[str, Any]) -> Optional['CNBBaseModel']:
        try:
            # 首次校验以捕获所有错误
            return cls.model_validate(data)
        except ValidationError as exc:
            # 提取错误字段路径
            error_locs = cls._get_error_locations(exc)
            # 清洗数据：将错误字段设为 None
            cleaned_data = cls._clean_data(data, error_locs)
            try:
                # 使用清洗后的数据重新校验
                return cls.model_validate(cleaned_data)
            except ValidationError as e:
                print(e)
                return None

    @staticmethod
    def _get_error_locations(exc: ValidationError) -> set:
        """从 ValidationError 中提取所有错误字段的路径"""
        return {tuple(error["loc"]) for error in exc.errors()}

    @classmethod
    def _clean_data(cls, data: Any, error_locs: set) -> Any:
        """基于别名路径清理数据"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                field_path = (key,)  
                if field_path in error_locs:
                    cleaned[key] = None
                else:
                    cleaned[key] = value
            return cleaned
        else:
            return None