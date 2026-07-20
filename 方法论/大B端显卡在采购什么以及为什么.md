---
type: 行业认知
author:
date:
tags:
  - AI算力
aliases: []
rating:
---

# 现在大B端显卡究竟在采购什么、为什么

> **先说当下最关键的时间节点**
>
> - **海外**：Blackwell 已经是标配，H100/H200 成了降级选项
> - **国内**：H200 是刚刚突破的新战场，2万亿订单积压待批

---

## 一、海外大B端：为什么必须是 B200/GB200

### 核心驱动不是"快"，而是三个结构性原因

#### 原因1：成本算法在 Blackwell 代际发生了反转

B200 在 FP8 训练吞吐量上约是 H100 的 **4倍**，而售价只有约 **2倍**。这意味着**每 FLOP 的成本效率比 H100 高出约 64%**。对于大规模持续运行 AI 工作负载的企业，B200 更高的前期成本，反而带来更快的盈亏平衡。[Tech Insider](https://tech-insider.org/nvidia-blackwell-gpu-pricing/)

具体数字：

- 购买一台 **GB200 NVL72** 机架约需 **300万美元**，可获得 **13.5TB** 总 GPU 内存和约 **1,300 PFLOPS** FP4 算力。
- 一个原本在 H100 集群上需要 **30天** 的 2000亿参数模型训练任务，在 NVL72 上只需 **8天**。
- 按 80% 利用率、3年周期计算，含电力冷却共 **420万美元**——对比等效云算力约 **2400万美元**。
- **7个月回本。** [Tech Insider](https://tech-insider.org/nvidia-blackwell-gpu-pricing/)

> 这是采购决策的核心逻辑：不是"买最新的"，而是**换一代代比一代便宜**。

#### 原因2：模型参数规模已经突破 H100 的物理内存上限

- B200 的 **192GB HBM3e** 是 H100 容量的三倍。
- 8卡 HGX B200 系统提供 **1.5TB** GPU 内存，足以支撑当前大多数大型语言模型。
- 模型需要 2-GPU 张量并行才能在 H100 上跑起来的，B200 单卡就能解决——**更少的 GPU、更低的跨卡通信开销**。 [Introl](https://introl.com/blog/nvidia-b200-vs-gb200-deployment-guide)

> 换句话说，H100 不是"慢"的问题，而是模型根本装不下的问题。

#### 原因3：供不应求本身成为了采购偏好的强化机制

黄仁勋在 2025 年底的多次高层简报和财报电话会议中，将 B200 和 GB200 的需求描述为 **"insane"（疯狂）**，全球对高端 AI 算力的需求已远超最激进的产能提升。

- 截至 2025 年 12 月，仅来自全球最大云服务商的积压订单就已达 **360万台**。
- 任何想今天建前沿 AI 集群的企业或主权国家，都可能需要等待超过 **18个月**。 [FinancialContent](https://markets.financialcontent.com/wral/article/tokenring-2025-12-29-nvidias-blackwell-dynasty-b200-and-gb200-sold-out-through-mid-2026-as-backlog-hits-36-million-units)

Meta 甚至被迫推迟了其最先进的 **"Llama 4 Behemoth"** 模型的发布，就是因为要等足够多的 Blackwell 集群上线。 [FinancialContent](https://markets.financialcontent.com/wral/article/tokenring-2025-12-29-nvidias-blackwell-dynasty-b200-and-gb200-sold-out-through-mid-2026-as-backlog-hits-36-million-units)

> 这意味着：**能买到 B200 本身已经成为竞争壁垒**。手头有 Blackwell 分配额的初创公司估值在飙升，还卡在 H100 集群上的公司在推理速度和成本上越来越难竞争。

---

### 海外大B端的实际分层采购逻辑（2026年）

2026 年 3 月的算力市场快照清晰地呈现了三层结构：

| 型号 | 按小时中位价 |
| --- | --- |
| B200（hyperscaler） | 约 9.10 美元 |
| H200 | 约 4–5 美元 |
| H100 | 约 2–3.5 美元 |

聪明的团队在承诺锁定之前会先建模利用率模式，目标是至少 **60–70%** 的利用率来验证预定经济学。 [Compute](https://compute.exchange/blogs/reserved-gpus-march-20206)

**实际决策框架：**

| 场景 | 推荐选择 |
| --- | --- |
| 建新基础设施 | **B200**——2026–2028 年部署的正确基础 |
| 部署实时 AI 应用（延迟敏感） | **B200**——每 token 延迟更低 |
| 本周就需要 GPU | **H200**——交货周期更短，广泛可用 |
| 跑 70B 以下中小模型 | **H200**——以约 4万美元/卡提供强劲价值 |
| 现有 H100 集群扩容 | **H100**——硬件一致性简化运维，还在合理范围 |

来源：[Gpu](https://www.gpu.fm/blog/nvidia-b200-complete-buyers-guide-2026)

---

## 二、国内大B端：最新战场是 H200，而不是 H20

### 时间线（关键是这几周发生的事）

- **2025年12月10日**：特朗普政府批准 H200 向"经批准客户"出口中国。中国发改委召开紧急会议，要求阿里、字节、腾讯评估采购需求。
- **2026年1月23日**：Bloomberg 报道，中国监管机构原则上批准三家公司进入采购准备阶段。
- **2026年1月28日**：路透社确认结果（见下）。

**路透社确认结果：**

> 字节跳动、阿里巴巴和腾讯获批**合计采购超过 40万张 H200 芯片**，其他公司正在排队等待后续批次审批。但条件仍在磋商中，一位知情人士表示，附加条件过于严格，客户还未将批准转化为实际订单。 [Yahoo Finance](https://finance.yahoo.com/news/exclusive-china-gives-green-light-034730976.html)

这 40万张只是第一批，但总需求远不止于此：

> 这 40万张的批准，**不到中国科技企业已下订单的 200多万张 H200 的五分之一**。 [WinBuzzer](https://winbuzzer.com/2026/01/28/china-approves-first-nvidia-h200-chip-imports-tech-giants-xcxwbn/)

字节跳动的出价最激进：

> 字节跳动 2025 年全年在英伟达芯片上花了 **850亿元人民币**，2026 年的预算进一步提高——准备花约 **140亿美元** 采购英伟达 AI GPU。 [Tom's Hardware](https://www.tomshardware.com/pc-components/gpus/tiktok-owner-bytedance-to-reportedly-purchase-usd14-billion-worth-of-nvidia-ai-gpus-in-2026-company-betting-on-beijings-approval-following-trump-admins-ease-on-ai-export-controls)

### 国内大B端为什么一定要 H200，不接受 H20

- H200 的性能约是英伟达 H20 芯片的 **6倍**。这解释了为什么在监管不确定的情况下，中国企业仍大量下单。 [WinBuzzer](https://winbuzzer.com/2026/01/28/china-approves-first-nvidia-h200-chip-imports-tech-giants-xcxwbn/)
- H200 比英伟达为应对白宫禁令而生产的 H20 芯片强大得多，也比中国国产芯片制造商的最新产品强得多。这就是为什么本土科技巨头如阿里和字节跳动，**在获批后都准备各自订购超过 20万张 H200**。 [Tom's Hardware](https://www.tomshardware.com/tech-industry/china-expected-to-approve-h200-imports-in-early-2026-report-claims-tech-giants-alibaba-and-bytedance-reportedly-ready-to-order-over-200-000-nvidia-chips-each-if-green-lit-by-beijing)

更关键的一点：国内大厂能够接受 H20 做推理，但无法接受 H20 做模型训练迭代。这在此前阿里云官方已有表态——H20 **"无法满足大模型迭代需求"**。而 H200 是他们能买到的、第一张真正支撑下一代训练的卡。

### 国内采购的政治附加条件（这是新增变量）

- 北京将鼓励企业在获批进口外国芯片时，同时购买一定数量的国产芯片作为条件，但具体比例尚未确定。 [Bloomberg](https://www.bloomberg.com/news/articles/2026-01-23/china-tells-alibaba-top-tech-firms-to-prep-nvidia-h200-orders)
- 监管机构正在考虑的限制包括：
  - **将 Nvidia 硬件的采购数量上限与企业现有及计划中的国产加速器采购挂钩**；
  - 另一方案则禁止 H200 用于金融和能源等战略敏感行业。 [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/china-weighs-import-limits-on-nvidias-h200-after-us-export-rules-relaxed)

> 这构成了国内大B端采购的独特困境：**你想买多少英伟达，就得同时证明你买了多少国产**。这直接影响了整个采购决策的逻辑——从纯技术选择，变成了政治配额管理下的组合采购。

---

## 三、两条线的本质对比

| 维度 | 海外大B端 | 国内大B端 |
| --- | --- | --- |
| **当前目标型号** | B200 / GB200（训练）；H200（推理备选） | H200（刚刚获批）；B200 完全没资格 |
| **不买旧卡的原因** | TCO 算账 B200 反而更便宜；H100 内存装不下新模型 | H20 对模型迭代训练"无法满足需求"（阿里云原话） |
| **最大瓶颈** | 供货——B200 积压 360万台，等 18个月 | 政策——200万张订单只批了 40万张 |
| **是否接受旧卡** | 接受 H100/H200 作为过渡，B200 等不到时的次优 | 接受 H20 做推理跑量；训练迭代坚决不接受 H20 |
| **采购决策的隐含逻辑** | 算力竞争 = 生存问题，落后一代就被甩开 | 算力缺口 = 国家战略问题，买什么由政策决定，不只是技术 |

最后一个数字能说明一切：国产芯片目前能与英伟达 H20 竞争，但**与 H200 仍存在显著代差**。这一性能差距，解释了为什么中国科技公司在监管不确定的情况下，仍然下了超过 200万张 H200 的订单。 [WinBuzzer](https://winbuzzer.com/2026/01/28/china-approves-first-nvidia-h200-chip-imports-tech-giants-xcxwbn/)

> 这才是采购决策的底层逻辑：**不是"想要最新的"，而是"不要被落下"。**
> 对海外是怕竞争对手先拿到 B200；对国内是怕永远只能用 H20，拿 6 倍性能差距去跟全球竞争对手赛跑。

## 相关

- 概念:[[AI算力]] · [[AI]]
- [[国信证券-二十年六大景气行情启示-本轮AI何时见顶]] — 互补:判顶变量与微观证据:云厂商 Capex 二阶导的判顶框架,对应显卡采购行为的一线拆解
- [[算力加资本投资能玩出几层花]] — 互补:算力产业链一体两面:采购行为决定需求真实性,资本玩法决定筹码结构
