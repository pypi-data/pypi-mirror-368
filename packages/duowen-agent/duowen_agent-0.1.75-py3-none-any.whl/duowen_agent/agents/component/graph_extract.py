import json
from time import sleep
from typing import List, Optional
from typing import Literal, Type, Union, Annotated

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.error import LLMError, ObserverException, LengthLimitExceededError
from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.prompt.prompt_build import GeneralPromptBuilder
from duowen_agent.utils.core_utils import (
    stream_to_string,
    json_observation,
    remove_think,
)
from duowen_agent.utils.string_template import StringTemplate
from pydantic import BaseModel, Field
from pydantic import create_model

DEFAULT_GRAPH_CONFIG = {
    "entity_types": {
        "person": "代表一个个体，通常指人的姓名。",
        "organization": "代表一个组织、机构、公司或团体，如政府部门、企业、学校等。",
        "location": "代表一个地理位置，如国家、城市、街道地址或具体的建筑物。",
        "datetime": "代表一个具体的日期、时间或时间段。",
        "event": "代表一个发生的具体事件，如会议、发布会、事故、节日庆典等。",
        "product": "代表一个商业化的产品、服务或软件。",
        "quantity": "代表带有单位的数值或度量，如货币金额、重量、距离等。",
        "concept": "代表一个抽象的概念、技术术语、理论、学科领域或业务名称。",
        "document": "代表一篇具体的文档、报告、文章、合同或出版物。",
        "thing": "代表一个通用的、具体的、不属于其他任何类别的物理对象或事物。",
    },
    "edge_definitions": {
        "belongs_to": {
            "description": "表示从属或成员关系，如 'A是B的成员' 或 'A隶属于B'。",
            "source_types": ["person", "product", "organization"],
            "target_types": ["organization", "location"],
        },
        "located_in": {
            "description": "表示实体在地理位置上的关系，即 'A位于B'。",
            "source_types": [
                "person",
                "organization",
                "event",
                "thing",
                "product",
            ],
            "target_types": ["location"],
        },
        "happened_at": {
            "description": "表示事件发生的时间，即 'A发生在B'。",
            "source_types": ["event"],
            "target_types": ["datetime"],
        },
        "involved_in": {
            "description": "表示实体参与或涉及到某个事件中，即 'A参与了B'。",
            "source_types": ["person", "organization", "product"],
            "target_types": ["event"],
        },
        "has_property": {
            "description": "表示一个实体具有某种属性、特征或能力。",
            "source_types": [
                "person",
                "organization",
                "product",
                "thing",
                "event",
            ],
            "target_types": ["concept", "quantity"],
        },
        "refers_to": {
            "description": "表示一个实体（通常是文档或概念）引用、指向或关于另一个实体。",
            "source_types": ["document", "concept", "event"],
            "target_types": [
                "person",
                "organization",
                "product",
                "event",
                "document",
                "concept",
            ],
        },
        "produces": {
            "description": "表示一个实体创造、生产或发布了另一个实体。",
            "source_types": ["person", "organization"],
            "target_types": ["product", "document", "thing"],
        },
        "uses": {
            "description": "表示一个实体使用另一个实体（如工具、技术或产品）。",
            "source_types": ["person", "organization", "event"],
            "target_types": ["product", "concept", "thing"],
        },
        "connects_to": {
            "description": "表示两个实体之间存在一种未被其他关系明确定义的通用关联或互动。",
            "source_types": [
                "person",
                "organization",
                "location",
                "datetime",
                "event",
                "product",
                "quantity",
                "concept",
                "document",
                "thing",
            ],
            "target_types": [
                "person",
                "organization",
                "location",
                "datetime",
                "event",
                "product",
                "quantity",
                "concept",
                "document",
                "thing",
            ],
        },
    },
}


class GraphConfig(BaseModel):
    entity_types: dict[str, str] = Field(description="实体类型")
    edge_definitions: dict[str, dict[str, str | list[str]]] = Field(
        description="边定义列表"
    )


class Entity(BaseModel):
    entity_type: str = Field(description="实体类型")
    entity_name: str = Field(description="实体名称")
    entity_description: str = Field(description="实体描述")


class Edge(BaseModel):
    edge_type: str = Field(description="边类型")
    source_entity: str = Field(description="源实体名称")
    source_entity_type: str = Field(description="源实体类型")
    target_entity: str = Field(description="目标实体名称")
    target_entity_type: str = Field(description="目标实体类型")
    relationship_description: str = Field(description="关系描述")


class GraphModel(BaseModel):
    entities: Optional[List[Entity]] = Field(description="实体列表")
    edges: Optional[List[Edge]] = Field(description="边列表")


def create_dynamic_graph_model(graph_config: GraphConfig) -> Type[BaseModel]:
    entity_type_keys = list(graph_config.entity_types.keys())
    entity_types_literal = Literal[tuple(entity_type_keys)]

    entity_type_descriptions = "\n".join(
        [f"- `{key}`: {desc}" for key, desc in graph_config.entity_types.items()]
    )
    entity_type_field_description = (
        f"实体的类型。必须是以下之一：\n{entity_type_descriptions}"
    )

    _DynamicEntity = create_model(
        "Entity",
        entity_type=(
            entity_types_literal,
            Field(description=entity_type_field_description),
        ),
        entity_name=(str, Field(description="实体的唯一名称")),
        entity_description=(str, Field(description="对这个具体实体的详细描述")),
    )

    # 3. 循环创建所有 Edge 子模型 (这部分逻辑保持不变)
    edge_submodels = []
    for index, data in enumerate(graph_config.edge_definitions.items()):
        edge_name, definition = data
        source_types_literal = Literal[tuple(definition["source_types"])]
        target_types_literal = Literal[tuple(definition["target_types"])]

        edge_fields = {
            "edge_type": (
                Literal[edge_name],
                Field(description=definition["description"]),
            ),
            "source_entity": (
                str,
                Field(
                    description="源实体的名称，必须与实体列表中的某个实体名称完全匹配"
                ),
            ),
            "source_entity_type": (
                source_types_literal,
                Field(description=f"源实体类型必须是: {definition['source_types']}"),
            ),
            "target_entity": (
                str,
                Field(
                    description="目标实体的名称，必须与实体列表中的某个实体名称完全匹配"
                ),
            ),
            "target_entity_type": (
                target_types_literal,
                Field(description=f"目标实体类型必须是: {definition['target_types']}"),
            ),
            "relationship_description": (
                str,
                Field(description="对这条关系的详细描述"),
            ),
        }

        _EdgeSubmodel = create_model(f"Edge_{index}", **edge_fields)
        edge_submodels.append(_EdgeSubmodel)

    # 4. 构建带 Discriminator 的联合类型 (逻辑保持不变)
    _DynamicEdgeUnion = Union[tuple(edge_submodels)]
    _DynamicEdge = Annotated[_DynamicEdgeUnion, Field(discriminator="edge_type")]

    # 5. 创建最终的 Graph 模型 (逻辑保持不变)
    _DynamicGraph = create_model(
        "Graph",
        entities=(
            List[_DynamicEntity],
            Field(description="从文本中识别出的所有实体列表"),
        ),
        edges=(
            List[_DynamicEdge],
            Field(description="连接实体的关系列表，每条关系都必须符合其定义的类型约束"),
        ),
    )

    return _DynamicGraph


class GraphExtract(BaseComponent):

    def __init__(
        self,
        llm_instance: OpenAIChat,
        max_gleanings: int = 2,
        graph_config: GraphConfig = None,
        retry_cnt: int = 3,
        retry_sleep: int = 3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs
        self.max_gleanings = max_gleanings
        self.graph_config = graph_config or GraphConfig(**DEFAULT_GRAPH_CONFIG)
        self.retry_cnt = retry_cnt
        self.retry_sleep = retry_sleep
        self.continue_prompt = "MANY entities were missed in the last extraction.  Add them below using the same format:\n"
        self.if_loop_prompt = "It appears some entities may have still been missed. Answer Y if there are still entities that need to be added, or N if there are none. Please answer with a single letter Y or N.\n"
        self.graph: Optional[GraphModel] = None

    def build_prompt(self) -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""给定一份可能与当前任务相关的文本，以及指定的实体类型列表，要求完成以下操作：  
1. **提取所有符合类型的实体**  
2. **识别这些实体之间的关联关系**""",
            step=StringTemplate(
                """#### **1. 实体识别与信息提取**  
对文本进行分析，找出所有目标实体。针对每个实体，需提供以下信息：  
- **实体名称（entity_name）**：实体名称  
- **实体类型（entity_type）**：必须是指定类型之一 `[{entity_types}]`  
- **实体描述（entity_description）**：详细描述该实体的特征、属性或行为  

#### **2. 关系识别与强度评估**  
从已识别的实体中，找出所有**明确存在关联**的实体对（源实体 → 目标实体），并记录：  
- **源实体（source_entity）**：关系发起方（与步骤1中的实体名称一致）  
- **源实体类型（source_entity_type）**：关系发起方（与步骤1中的实体类型一致） 
- **关系类型（edge_type）**： 必须是指定关系类型之一 `[{edge_type}]`  
- **目标实体（target_entity）**：关系接收方（与步骤1中的实体名称一致）  
- **目标实体类型（target_entity_type）**：关系接收方（与步骤1中的实体类型一致）  
- **关系描述（relationship_description）**：说明两者如何关联  """,
            ),
            output_format=create_dynamic_graph_model(self.graph_config),
        )

    def _extract(self, prompt: MessagesSet, **kwargs) -> GraphModel:
        for i in range(self.retry_cnt):
            try:
                _res = stream_to_string(
                    self.llm_instance.chat_for_stream(messages=prompt, **kwargs)
                )
                _res = remove_think(_res)
                return json_observation(_res, GraphModel)
            except (ObserverException, LLMError, LengthLimitExceededError) as e:
                if i == self.retry_cnt - 1:
                    raise e
                else:
                    sleep(self.retry_sleep)

    def _tidy_graph(self, _graph: GraphModel) -> GraphModel:
        valid_entity_types = set(self.graph_config.entity_types.keys())
        if _graph.entities:
            # 过滤掉类型不在配置中的实体
            _graph.entities = [
                entity
                for entity in _graph.entities
                if entity.entity_type in valid_entity_types
            ]

        # 2. 构建有效实体名称集合（用于后续校验边）
        valid_entity_names = (
            {entity.entity_name for entity in _graph.entities}
            if _graph.entities
            else set()
        )

        # 3. 清理无效边
        if _graph.edges:
            valid_edges = []
            for edge in _graph.edges:
                # 检查边类型是否在配置中
                edge_def = self.graph_config.edge_definitions.get(edge.edge_type)
                if not edge_def:
                    continue

                # 检查源实体是否存在且类型匹配
                valid_source = (
                    edge.source_entity in valid_entity_names
                    and edge.source_entity_type in edge_def["source_types"]
                )

                # 检查目标实体是否存在且类型匹配
                valid_target = (
                    edge.target_entity in valid_entity_names
                    and edge.target_entity_type in edge_def["target_types"]
                )

                # 保留有效边
                if valid_source and valid_target:
                    valid_edges.append(edge)

            _graph.edges = valid_edges

            return _graph

    def _merge_graph(self, new_graph: GraphModel) -> GraphModel:

        # 清理新提取的子图
        new_graph = self._tidy_graph(new_graph)

        # 后续合并逻辑...
        if self.graph is None:
            self.graph = new_graph
            return self.graph

        else:

            existing_entities = {e.entity_name for e in self.graph.entities}
            self.graph.entities += [
                e for e in new_graph.entities if e.entity_name not in existing_entities
            ]

            # 合并边（去重）
            existing_edges = {
                (e.source_entity, e.edge_type, e.target_entity)
                for e in self.graph.edges
            }
            self.graph.edges += [
                e
                for e in new_graph.edges
                if (e.source_entity, e.edge_type, e.target_entity) not in existing_edges
            ]
            return self.graph

    def run(self, input: str) -> GraphModel:

        _result = []
        _build = self.build_prompt()

        _prompt = _build.get_instruction(
            user_input=input,
            temp_vars={
                "entity_types": ", ".join(list(self.graph_config.entity_types.keys())),
                "edge_type": ", ".join(self.graph_config.edge_definitions.keys()),
            },
        )

        _res = self._extract(_prompt)
        _res = self._merge_graph(_res)

        _prompt.add_assistant(
            f"```json\n{json.dumps(_res.model_dump(), indent=2, ensure_ascii=False)}\n```"
        )

        for i in range(self.max_gleanings):
            _prompt.add_user(self.continue_prompt)
            _res = self._extract(_prompt, temperature=0.3)
            _res = self._merge_graph(_res)
            if i >= self.max_gleanings - 1:
                break
            _prompt.add_assistant(
                f"```json\n{json.dumps(_res.model_dump(), indent=2, ensure_ascii=False)}\n```"
            )
            _prompt.add_user(self.if_loop_prompt)

            continuation = self.llm_instance.chat(_prompt, temperature=0.8)

            if continuation.strip() != "Y":
                break
            _prompt.add_assistant("Y")

        return self.graph
