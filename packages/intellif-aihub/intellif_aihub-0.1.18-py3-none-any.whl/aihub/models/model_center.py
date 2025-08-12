from __future__ import annotations

from enum import IntEnum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    """用户"""

    id: int = Field(description="用户ID")
    name: str = Field(description="用户名")


class ModelType(BaseModel):
    """模型类型"""

    id: int = Field(description="类型ID")
    name: str = Field(description="类型名称")


class DeployPlatform(BaseModel):
    """部署平台"""

    id: int = Field(description="部署平台ID")
    name: str = Field(description="部署平台名称")


class QuantLevel(BaseModel):
    """量化等级"""

    id: int = Field(description="量化等级ID")
    name: str = Field(description="量化等级名称")


class ModelStatus(IntEnum):
    """模型状态：1-Waiting；2-Creating；3-Success；4-Fail"""
    Waiting = 1
    Creating = 2
    Success = 3
    Fail = 4


class Model(BaseModel):
    """模型详情"""

    id: int = Field(description="模型ID")
    name: str = Field(description="模型名称")
    description: str = Field(description="描述")
    model_type: ModelType = Field(alias="model_type", description="模型类型")
    model_path: str = Field(alias="model_path", description="模型路径")
    deploy_platform: DeployPlatform = Field(alias="deploy_platform", description="部署平台")
    param_cnt: str = Field(alias="param_cnt", description="参数量")
    quant_level: QuantLevel = Field(alias="quant_level", description="量化等级")
    creator: User = Field(description="创建人")
    status: ModelStatus = Field(description="模型状态")
    created_at: int = Field(alias="created_at", description="创建时间戳 (ms)")
    updated_at: int = Field(alias="updated_at", description="更新时间戳 (ms)")

    model_config = ConfigDict(protected_namespaces=(), use_enum_values=True)


class ListModelTypesRequest(BaseModel):
    """查询模型类型列表请求"""

    page_size: int = Field(999, alias="page_size", description="每页数量")
    page_num: int = Field(1, alias="page_num", description="当前页码")


class ListModelTypesResponse(BaseModel):
    """查询模型类型列表返回"""

    total: int = Field(description="总条数")
    page_size: int = Field(alias="page_size", description="每页数量")
    page_num: int = Field(alias="page_num", description="当前页码")
    data: List[ModelType] = Field(default_factory=list, description="类型列表")


class ListDeployPlatformsRequest(BaseModel):
    """查询部署平台列表请求"""

    page_size: int = Field(999, alias="page_size", description="每页数量")
    page_num: int = Field(1, alias="page_num", description="当前页码")


class ListDeployPlatformsResponse(BaseModel):
    """查询部署平台列表返回"""

    total: int = Field(description="总条数")
    page_size: int = Field(alias="page_size", description="每页数量")
    page_num: int = Field(alias="page_num", description="当前页码")
    data: List[DeployPlatform] = Field(default_factory=list, description="平台列表")


class ListQuantLevelsRequest(BaseModel):
    """查询量化等级列表请求"""

    page_size: int = Field(999, alias="page_size", description="每页数量")
    page_num: int = Field(1, alias="page_num", description="当前页码")


class ListQuantLevelsResponse(BaseModel):
    """查询量化等级列表返回"""

    total: int = Field(description="总条数")
    page_size: int = Field(alias="page_size", description="每页数量")
    page_num: int = Field(alias="page_num", description="当前页码")
    data: List[QuantLevel] = Field(default_factory=list, description="量化等级列表")


class ListModelsRequest(BaseModel):
    """查询模型列表请求"""

    page_size: int = Field(20, alias="page_size", description="每页数量")
    page_num: int = Field(1, alias="page_num", description="当前页码")
    name: Optional[str] = Field(None, description="名称过滤")


class ListModelsResponse(BaseModel):
    """查询模型列表返回"""

    total: int = Field(description="总条数")
    page_size: int = Field(alias="page_size", description="每页数量")
    page_num: int = Field(alias="page_num", description="当前页码")
    data: List[Model] = Field(default_factory=list, description="模型列表")


class CreateModelRequest(BaseModel):
    """创建模型请求"""

    name: str = Field(description="模型名称")
    description: Optional[str] = Field(None, description="描述")
    model_type_id: int = Field(alias="model_type_id", description="模型类型ID")
    model_path: Optional[str] = Field(None, alias="model_path", description="模型路径")
    deploy_platform_id: Optional[int] = Field(None, alias="deploy_platform_id", description="部署平台ID")
    param_cnt: Optional[str] = Field(None, alias="param_cnt", description="参数量")
    quant_level_id: Optional[int] = Field(None, alias="quant_level_id", description="量化等级ID")
    model_config = ConfigDict(protected_namespaces=())


class CreateModelResponse(BaseModel):
    """创建模型返回"""

    id: int = Field(description="模型ID")


class EditModelRequest(BaseModel):
    """编辑模型请求"""

    id: int = Field(description="模型ID")
    name: str = Field(description="模型名称")
    description: Optional[str] = Field(None, description="描述")
    model_type_id: int = Field(alias="model_type_id", description="模型类型ID")
    model_path: Optional[str] = Field(None, alias="model_path", description="模型路径")
    deploy_platform_id: Optional[int] = Field(None, alias="deploy_platform_id", description="部署平台ID")
    param_cnt: Optional[str] = Field(None, alias="param_cnt", description="参数量")
    quant_level_id: Optional[int] = Field(None, alias="quant_level_id", description="量化等级ID")
    model_config = ConfigDict(protected_namespaces=())
