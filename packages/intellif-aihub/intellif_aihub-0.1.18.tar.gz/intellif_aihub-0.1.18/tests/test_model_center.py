from __future__ import annotations

import unittest
import uuid

from src.aihub.client import Client
from src.aihub.models.model_center import *

BASE_URL = "http://192.168.13.160:30021"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ5MDY2ODUwODAsImlhdCI6MTc1MzA4NTA4MCwidWlkIjoxMH0.89bQ66BJDGoCzwxuxugRRt9acPFKEVmgqXMZX7ApnhM"


class TestModelCenter(unittest.TestCase):
    def test_model(self) -> None:
        client = Client(base_url=BASE_URL, token=TOKEN)

        name = f"sdk_test_model_{uuid.uuid4().hex[:6]}"
        model_id = client.model_center.create_model(
            CreateModelRequest(
                name=name,
                description="SDK 单测创建",
                model_type_id=6,
                model_path="192.168.13.160:/data1/liujingyi/modelzoo_data/model/pose/onnx_yolov7_pose",
                deploy_platform_id=3,
                param_cnt="1",
                quant_level_id=1,
            )
        )
        self.assertGreater(model_id, 0)

        models = client.model_center.list_models(ListModelsRequest(name=name))
        self.assertTrue(any(m.id == model_id for m in models.data))

        detail = client.model_center.get_model(model_id)
        self.assertEqual(detail.name, name)

        new_name = name + "_upd"
        client.model_center.edit_model(
            EditModelRequest(
                id=model_id,
                name=new_name,
                description="SDK 单测创建",
                model_type_id=6,
                model_path="192.168.13.160:/data1/liujingyi/modelzoo_data/model/pose/onnx_yolov7_pose",
                deploy_platform_id=3,
                param_cnt="1",
                quant_level_id=1,
            )
        )
        detail2 = client.model_center.get_model(model_id)
        self.assertEqual(detail2.name, new_name)

        client.model_center.delete_model(model_id)

        types_resp = client.model_center.list_model_types()
        self.assertIsInstance(types_resp.data, list)

        plat_resp = client.model_center.list_deploy_platforms()
        self.assertIsInstance(plat_resp.data, list)

        quant_resp = client.model_center.list_quant_levels()
        self.assertIsInstance(quant_resp.data, list)
