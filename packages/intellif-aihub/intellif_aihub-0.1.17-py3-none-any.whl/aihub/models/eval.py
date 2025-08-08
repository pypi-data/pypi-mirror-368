# !/usr/bin/env python
# -*-coding:utf-8 -*-
from typing import Dict

from pydantic import BaseModel, Field


class CreateEvalReq(BaseModel):
    """创建评测任务"""
    dataset_id: int = Field(description="数据集ID")
    dataset_version_id: int = Field(description="数据集版本ID")
    prediction_artifact_path: str = Field(description="推理产物的路径")
    evaled_artifact_path: str = Field(description="评测结果产物的路径")
    run_id: str = Field(description="运行ID")
    user_id: int = Field(0, description="用户ID")
    report: Dict = Field(default_factory=dict, description="评测报告")


class EvalRun(BaseModel):
    """评测任务的运行实体"""
    id: int = Field(description="评测的运行ID")


class CreateEvalResp(BaseModel):
    """创建评测任务的返回结果"""
    eval_run: EvalRun = Field(alias="eval_run", description="评测运行信息")
