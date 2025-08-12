# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""模型中心服务模块

封装与 **Model‑Center** 后端交互的常用能力，主要涉及模型的增、删、改、查，以及模型元数据（类型 / 部署平台 / 量化等级）的查询功能：

- **分页查询模型列表**
- **获取单个模型详情**
- **新建模型**
- **编辑模型**
- **删除模型**
- **查询模型类型下拉**
- **查询部署平台下拉**
- **查询量化等级下拉**
"""

from __future__ import annotations

import httpx

from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.model_center import (
    ListModelsRequest,
    ListModelsResponse,
    ListModelTypesRequest,
    ListModelTypesResponse,
    ListDeployPlatformsRequest,
    ListDeployPlatformsResponse,
    ListQuantLevelsRequest,
    ListQuantLevelsResponse,
    CreateModelRequest,
    CreateModelResponse,
    EditModelRequest,
    Model,
)

_BASE = "/model-center/api/v1"


class ModelCenterService:
    """模型中心业务封装"""

    def __init__(self, http: httpx.Client):
        self._model = _Model(http)

    def list_models(self, payload: ListModelsRequest) -> ListModelsResponse:
        """分页查询模型列表

        Args:
            payload: 查询参数（分页、名称过滤等）

        Returns:
            ListModelsResponse: 包含分页信息与模型数据
        """
        return self._model.list(payload)

    def get_model(self, model_id: int) -> Model:
        """获取模型详情

        Args:
            model_id: 模型 ID

        Returns:
            Model: 模型完整信息
        """
        return self._model.get(model_id)

    def create_model(self, payload: CreateModelRequest) -> int:
        """创建模型

        Args:
            payload: 创建模型所需字段

        Returns:
            int: 后端生成的模型 ID
        """
        return self._model.create(payload)

    def edit_model(self, payload: EditModelRequest) -> None:
        """编辑模型信息

        Args:
            payload: 编辑模型所需字段（需包含 id）
        """
        self._model.edit(payload)

    def delete_model(self, model_id: int) -> None:
        """删除模型

        Args:
            model_id: 目标模型 ID
        """
        self._model.delete(model_id)

    def list_model_types(self) -> ListModelTypesResponse:
        """查询模型类型列表

        Returns:
            ListModelTypesResponse: 模型类型集合
        """
        return self._model.list_types(ListModelTypesRequest())

    def list_deploy_platforms(self) -> ListDeployPlatformsResponse:
        """查询可用部署平台列表

        Returns:
            ListDeployPlatformsResponse: 部署平台集合
        """
        return self._model.list_platforms(ListDeployPlatformsRequest())

    def list_quant_levels(self) -> ListQuantLevelsResponse:
        """查询量化等级列表

        Returns:
            ListQuantLevelsResponse: 量化等级集合
        """
        return self._model.list_quant_levels(ListQuantLevelsRequest())

    @property
    def model(self) -> _Model:
        return self._model


class _Model:

    def __init__(self, http: httpx.Client):
        self._http = http

    def list(self, payload: ListModelsRequest) -> ListModelsResponse:
        resp = self._http.get(f"{_BASE}/models", params=payload.model_dump(by_alias=True, exclude_none=True))
        wrapper = APIWrapper[ListModelsResponse].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data

    def get(self, model_id: int) -> Model:
        resp = self._http.get(f"{_BASE}/models/{model_id}")
        wrapper = APIWrapper[Model].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data

    def create(self, payload: CreateModelRequest) -> int:
        resp = self._http.post(f"{_BASE}/models", json=payload.model_dump(by_alias=True, exclude_none=True))
        wrapper = APIWrapper[CreateModelResponse].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data.id

    def edit(self, payload: EditModelRequest) -> None:
        resp = self._http.put(f"{_BASE}/models/{payload.id}",
                              json=payload.model_dump(by_alias=True, exclude_none=True))
        wrapper = APIWrapper[dict].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")

    def delete(self, model_id: int) -> None:
        resp = self._http.delete(f"{_BASE}/models/{model_id}")
        wrapper = APIWrapper[dict].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")

    def list_types(self, payload: ListModelTypesRequest) -> ListModelTypesResponse:
        resp = self._http.get(f"{_BASE}/model-types", params=payload.model_dump(by_alias=True))
        wrapper = APIWrapper[ListModelTypesResponse].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data

    def list_platforms(self, payload: ListDeployPlatformsRequest) -> ListDeployPlatformsResponse:
        resp = self._http.get(f"{_BASE}/deploy-platforms", params=payload.model_dump(by_alias=True))
        wrapper = APIWrapper[ListDeployPlatformsResponse].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data

    def list_quant_levels(self, payload: ListQuantLevelsRequest) -> ListQuantLevelsResponse:
        resp = self._http.get(f"{_BASE}/quant-levels", params=payload.model_dump(by_alias=True))
        wrapper = APIWrapper[ListQuantLevelsResponse].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data
