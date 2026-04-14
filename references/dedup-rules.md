# 论文去重规则

## 目标

把“同一篇论文在多个来源的多个入口”聚合成一个研究对象，同时尽量避免把不同论文误合并。

## 第一层：URL 归一化

去掉这些差异：
- `utm_*` 等追踪参数
- URL fragment `#...`
- 同一站点仅表示视图差异的参数
- `http`/`https` 等可安全归一化的差异

## 第二层：标识符优先

若可提取到以下标识符，优先用它们聚合：
- DOI
- arXiv id
- OpenReview forum/id
- ACL Anthology id
- Semantic Scholar paper id（仅作为辅助）

规则：
- DOI 一致 → 高置信度同一论文
- arXiv id 一致 → 高置信度同一 preprint
- DOI 与 arXiv 同时出现 → 视为同一研究工作不同入口，聚合但保留版本说明

## 第三层：标题归一化匹配

标题归一化时：
- 转小写
- 去标点和多余空格
- 统一连字符、冒号、括号差异
- 去掉常见前后缀（如 extended abstract、supplementary，若明确是附录则不要合并到主论文）

高置信度合并条件建议：
- 归一化标题完全相同
- 且作者列表高度重合，或年份相同/接近

中置信度合并条件：
- 标题极高相似
- 作者部分重合
- 主题和摘要明显一致

低置信度时不要自动合并，应保留为两个候选条目。

## 第四层：版本处理

区分这些情况：

### 可聚合但保留版本说明
- arXiv 预印本 与 正式 conference/journal 版本
- 同一论文不同镜像页
- 同一论文的项目页 / 作者页 / GitHub repo

### 不应直接合并
- workshop 版 与 大幅扩展后的 journal 版
- 标题接近但任务不同的论文
- 同一团队的 follow-up work

## 聚合后保留字段

每个“论文对象”建议保留：
- canonical_title
- aliases
- authors
- year
- doi
- arxiv_id
- venue
- abstract_sources
- canonical_source
- alternate_sources
- code_links
- project_links
- version_notes

## 选择 canonical source 的顺序

1. DOI / 正式出版页
2. arXiv / OpenReview / 会议官网
3. 作者主页 / 项目页
4. 索引页

若正式出版页没有摘要，而 arXiv 有完整摘要：
- canonical source 仍可设为正式出版页
- 但摘要来源可来自 arXiv

## 实际输出时的简化规则

若用户只是想要“推荐阅读清单”：
- 同一论文只显示一次
- 在条目下列出备用来源

若用户在做严肃文献综述：
- 需要额外标注 preprint / published / journal extension 等版本信息
