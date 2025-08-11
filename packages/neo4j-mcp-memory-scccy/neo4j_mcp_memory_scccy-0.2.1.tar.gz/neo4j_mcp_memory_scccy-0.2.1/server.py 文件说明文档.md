---
1. 1. # server.py 文件说明文档

      ## 概述
      `server.py` 是 Neo4j MCP Memory 服务的核心服务器文件，负责创建和管理一个基于 Model Context Protocol (MCP) 的服务器，该服务器提供知识图谱内存管理功能。

      ## 主要功能

      ### 1. MCP 服务器创建
      - 通过 `create_mcp_server()` 函数创建一个 FastMCP 服务器实例
      - 配置服务器名称为 "mcp-neo4j-memory"
      - 声明依赖项：neo4j 和 pydantic
      - 支持无状态 HTTP 模式

      ### 2. 知识图谱管理工具
      服务器提供以下 9 个核心工具：

      #### 读取操作
      | 工具名称 | 功能描述 | 参数 | 返回值 | 中文提示词 | 英文提示词 |
      |---------|---------|------|--------|------------|------------|
      | **Read Graph** | 读取整个知识图谱 | 无 | KnowledgeGraph | "请读取整个知识图谱" | "Please read the entire knowledge graph" |
      | **Search Memories** | 基于查询词搜索记忆节点 | query: str | KnowledgeGraph | "搜索包含[关键词]的记忆" | "Search for memories containing [keywords]" |
      | **Find Memories by Name** | 根据名称查找特定记忆 | names: list[str] | KnowledgeGraph | "查找名为[名称]的记忆" | "Find memories with names [name_list]" |

      #### 创建操作
      | 工具名称 | 功能描述 | 参数 | 返回值 | 中文提示词 | 英文提示词 |
      |---------|---------|------|--------|------------|------------|
      | **Create Entities** | 在知识图谱中创建多个新实体 | entities: list[Entity] | list[Entity] | "创建以下实体：[实体列表]" | "Create the following entities: [entity_list]" |
      | **Create Relations** | 在实体之间创建多个新关系 | relations: list[Relation] | list[Relation] | "在以下实体间创建关系：[关系列表]" | "Create relationships between the following entities: [relation_list]" |
      | **Add Observations** | 向现有实体添加新的观察结果 | observations: list[ConstraintAddition] | list[dict] | "为实体[名称]添加观察：[观察内容]" | "Add observations to entity [name]: [observation_content]" |

      #### 删除操作
      | 工具名称 | 功能描述 | 参数 | 返回值 | 中文提示词 | 英文提示词 |
      |---------|---------|------|--------|------------|------------|
      | **Delete Entities** | 删除多个实体及其关联关系 | entityNames: list[str] | str | "删除以下实体：[实体名称列表]" | "Delete the following entities: [entity_name_list]" |
      | **Delete Relations** | 从图谱中删除多个关系 | relations: list[Relation] | str | "删除以下关系：[关系列表]" | "Delete the following relationships: [relation_list]" |
      | **Delete Observations** | 删除实体的特定观察结果 | deletions: list[ConstraintDeletion] | str | "删除实体[名称]的观察：[观察内容]" | "Delete observations from entity [name]: [observation_content]" |

      

      

      

      ### 数据验证
      - 使用 Pydantic 进行输入数据验证
      - 确保数据模型的完整性

      ### 工具注解
      - 每个工具都包含详细的 MCP 注解
      - 指定工具的只读性、破坏性、幂等性和开放性

      

      

      ## 提示词对照表

      ### 常用操作提示词
      | 操作类型 | 中文提示词 | 英文提示词 | 使用场景 |
      |---------|-----------|-----------|----------|
      | **读取图谱** | "请显示整个知识图谱的结构" | "Please show the structure of the entire knowledge graph" | 了解图谱整体情况 |
      | **搜索记忆** | "查找所有与[主题]相关的记忆" | "Find all memories related to [topic]" | 主题相关搜索 |
      | **创建实体** | "请创建名为[名称]的[类型]实体" | "Please create a [type] entity named [name]" | 新建节点 |
      | **建立关系** | "在[实体A]和[实体B]之间建立[关系类型]关系" | "Establish [relationship_type] between [entity_A] and [entity_B]" | 连接节点 |
      | **添加属性** | "为[实体名称]添加[属性类型]：[属性值]" | "Add [property_type]: [property_value] to [entity_name]" | 更新节点属性 |
      | **删除操作** | "删除[实体名称]及其所有关联关系" | "Delete [entity_name] and all its associated relationships" | 清理数据 |
      | **批量操作** | "批量创建以下[数量]个[类型]实体" | "Batch create [count] [type] entities as follows" | 批量处理 |

      ### 高级查询提示词
      | 查询类型 | 中文提示词 | 英文提示词 | 应用场景 |
      |---------|-----------|-----------|----------|
      | **路径查询** | "查找从[起点]到[终点]的所有路径" | "Find all paths from [start_point] to [end_point]" | 关系路径分析 |
      | **模式匹配** | "查找所有符合[模式]的实体组合" | "Find all entity combinations matching [pattern]" | 复杂关系查询 |
      | **属性过滤** | "筛选出[属性]为[值]的所有实体" | "Filter all entities where [property] equals [value]" | 条件筛选 |
      | **统计查询** | "统计[类型]实体的数量" | "Count the number of [type] entities" | 数据分析 |

      ## 方法调用示例
      | 操作类型 | 输入示例 | 预期结果 |
      |---------|---------|----------|
      | 创建人员实体 | `{"name": "张三", "type": "Person", "properties": {"age": 30, "occupation": "工程师"}}` | 成功创建人员节点 |
      | 创建公司实体 | `{"name": "ABC公司", "type": "Company", "properties": {"industry": "科技", "founded": 2020}}` | 成功创建公司节点 |
      | 创建项目实体 | `{"name": "智能助手项目", "type": "Project", "properties": {"status": "进行中", "budget": 100000}}` | 成功创建项目节点 |

      ### 关系创建示例
      | 关系类型 | 输入示例 | 预期结果 |
      |---------|---------|----------|
      | 雇佣关系 | `{"source": "张三", "target": "ABC公司", "type": "WORKS_FOR", "properties": {"start_date": "2023-01-01"}}` | 创建雇佣关系边 |
      | 项目参与 | `{"source": "张三", "target": "智能助手项目", "type": "PARTICIPATES_IN", "properties": {"role": "开发工程师"}}` | 创建项目参与关系 |
      | 公司拥有 | `{"source": "ABC公司", "target": "智能助手项目", "type": "OWNS", "properties": {"ownership": 100}}` | 创建所有权关系 |

      ### 观察添加示例
      | 观察类型 | 输入示例 | 预期结果 |
      |---------|---------|----------|
      | 技能观察 | `{"entity_name": "张三", "constraint_type": "has_skill", "constraint_value": "Python编程"}` | 为张三添加技能属性 |
      | 项目状态 | `{"entity_name": "智能助手项目", "constraint_type": "current_phase", "constraint_value": "开发阶段"}` | 更新项目状态 |
      | 公司信息 | `{"entity_name": "ABC公司", "constraint_type": "employee_count", "constraint_value": "50"}` | 更新公司员工数量 |

      ## 安全特性

      ### 访问控制
      - 只读工具标记
      - 破坏性操作标记
      - 幂等性保证

      ### 错误隔离
      - 异常不会影响服务器稳定性
      - 详细的错误日志记录

      ## 错误处理与常见问题

      ### 常见错误类型
      | 错误类型 | 错误描述 | 解决方案 | 预防措施 |
      |---------|---------|----------|----------|
      | **Neo4jError** | 数据库连接或查询错误 | 检查数据库连接、验证查询语法 | 确保数据库服务正常运行 |
      | **ValidationError** | 数据模型验证失败 | 检查输入数据格式、验证必填字段 | 使用正确的数据模型结构 |
      | **ConnectionError** | 网络连接失败 | 检查网络配置、验证URI地址 | 配置正确的数据库连接参数 |
      | **PermissionError** | 权限不足 | 检查用户权限、验证认证信息 | 使用具有适当权限的账户 |

      ### 调试提示词
      | 问题类型 | 调试提示词 | 检查要点 |
      |---------|-----------|----------|
      | 连接问题 | "检查数据库连接状态" | 网络配置、认证信息、服务状态 |
      | 数据验证 | "验证输入数据格式" | 字段类型、必填项、数据范围 |
      | 查询性能 | "分析查询执行计划" | 索引使用、查询复杂度、数据量 |
      | 权限问题 | "检查用户权限设置" | 角色分配、数据库访问权限 |

      ## 扩展性

      ### 工具注册
      - 模块化的工具定义
      - 易于添加新的功能工具

      ### 协议支持
      - 多种传输协议支持
      - 便于集成到不同环境

      ## 实际使用场景提示词示例

      ### 企业知识管理场景
      | 业务场景 | 中文提示词 | 英文提示词 |
      |---------|-----------|-----------|
      | **员工入职** | "创建新员工[姓名]的信息，包括部门、职位、技能等" | "Create information for new employee [name], including department, position, skills, etc." |
      | **项目建立** | "建立[项目名称]项目，并关联相关团队成员和资源" | "Establish [project_name] project and associate relevant team members and resources" |
      | **技能评估** | "为员工[姓名]添加新掌握的技能：[技能名称]" | "Add newly acquired skill [skill_name] to employee [name]" |
      | **组织架构** | "显示[部门名称]的组织架构和人员分布" | "Show the organizational structure and personnel distribution of [department_name]" |

      ### 学术研究场景
      | 研究类型 | 中文提示词 | 英文提示词 |
      |---------|-----------|-----------|
      | **文献关联** | "查找与[研究主题]相关的所有论文和作者" | "Find all papers and authors related to [research_topic]" |
      | **概念网络** | "构建[学科领域]的概念关系网络" | "Build a conceptual relationship network for [academic_field]" |
      | **引用分析** | "分析[论文标题]的引用关系和影响因子" | "Analyze the citation relationships and impact factor of [paper_title]" |
      | **合作网络** | "展示[研究者姓名]的合作网络和共同发表论文" | "Show the collaboration network and co-authored papers of [researcher_name]" |

      ### 产品推荐场景
      | 推荐类型 | 中文提示词 | 英文提示词 |
      |---------|-----------|-----------|
      | **用户画像** | "基于用户[ID]的行为数据构建个性化画像" | "Build personalized profile based on behavior data of user [ID]" |
      | **相似产品** | "查找与[产品名称]相似的其他产品" | "Find other products similar to [product_name]" |
      | **购买路径** | "分析用户从浏览到购买的完整路径" | "Analyze the complete path from browsing to purchase for users" |
      | **兴趣标签** | "为用户[ID]添加新的兴趣标签：[标签内容]" | "Add new interest tag [tag_content] to user [ID]" |

      ## 总结

      `server.py` 文件是整个 Neo4j MCP Memory 服务的核心，它提供了一个完整的、可扩展的知识图谱管理服务器。通过 MCP 协议，客户端可以方便地访问各种知识图谱操作功能，包括创建、读取、更新和删除操作。该服务器设计考虑了异步性能、错误处理、安全性和可扩展性，是一个功能完整的企业级知识图谱管理解决方案。