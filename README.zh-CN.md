# Jean Skills

[English](README.md) | 简体中文

面向实际开发任务的 Agent Skills 集合。每个 skill 独立安装、按需读取参考资料；不同生态使用同级目录，分别维护开发工作流和验收案例。

## 技能目录

| Skill | 用途 | 状态 |
| --- | --- | --- |
| [web3-evm-dev](skills/web3-evm-dev/SKILL.md) | EVM 合约、React DApp、DeFi、智能账户、钱包认证及配套后端 | 已实现 |

未来的 Solana 技能使用 `skills/web3-solana-dev/`，实现时再添加目录和索引。

## 仓库结构

```text
jean-skills/
├── README.md
├── README.zh-CN.md
├── skills/
│   └── web3-evm-dev/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
│           ├── contracts.md
│           ├── testing.md
│           ├── dapp.md
│           ├── backend.md
│           ├── deployment.md
│           ├── authentication.md
│           ├── defi.md
│           └── smart-accounts.md
└── evals/
    └── web3-evm-dev/
        └── scenarios.md
```

`skills/` 保存可分发的技能，`evals/` 保存维护者使用的验收任务。技能运行不依赖仓库根目录、其他技能或 `evals/`。有实际需要时，再在对应技能内添加 `scripts/` 和 `assets/`。

## EVM 技能的工程约定

| 层次 | 新项目默认 |
| --- | --- |
| DApp | React + TypeScript，RainbowKit 钱包入口，wagmi 合约交互，viem 底层能力 |
| 体验与数据 | react-toastify 状态通知；统一主题与多语言；TanStack Query 链上数据缓存和刷新 |
| 配套后端（按需） | Node.js + TypeScript + Prisma + viem；常驻主机进程使用 PM2 |
| 合约与签名 | Foundry + OpenZeppelin；关键业务测试；Cast Wallet 加密 keystore，不在 `.env` 存开发者私钥 |

技能将这些约定转为按需执行的工作流和可观察的验收要求。已有项目优先保持兼容，明确要求迁移时再调整。PM2 提供进程管理与故障重启；RPC、数据库和主机故障需通过健康检查及恢复机制处理。

进阶能力按任务加载：[DeFi](skills/web3-evm-dev/references/defi.md) 覆盖兑换、预言机、ERC-4626 金库及借贷；[智能账户](skills/web3-evm-dev/references/smart-accounts.md) 覆盖 ERC-4337、EIP-7702、ERC-1271 和 EIP-5792；[钱包认证](skills/web3-evm-dev/references/authentication.md) 覆盖 SIWE 与会话。基础流程同时包含 approve/permit、编译器已知问题、静态分析、跨层 CI、L2 确认策略及上线权限交接。不会因启用技能而默认给普通 DApp 增加这些模块。

## 安装到 Codex

将需要的技能目录放进 Codex 的技能发现路径。以下命令在本仓库根目录运行，将 EVM 技能链接到个人技能目录；克隆目录需要保持可用。运行前确认目标 `~/.agents/skills/web3-evm-dev` 尚不存在（包括同名符号链接）：

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/web3-evm-dev" "$HOME/.agents/skills/web3-evm-dev"
```

如果目标已经存在，先检查它的来源，再决定更新；不要重复创建或覆盖已有安装。也可以把整个 `skills/web3-evm-dev/` 目录复制到目标项目的 `.agents/skills/` 下，仅供该项目使用。

Codex 支持技能目录的符号链接，以及个人和项目级技能发现。技能未出现时重启 Codex。具体发现机制见 [Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。

安装 skill 本身不要求安装区块链工具。实际开发时按项目需要使用 Foundry、Node.js 和项目包管理器；保留已有 Hardhat、ethers 等技术栈。

## 使用示例

在目标项目中提出具体任务，也可以显式指定技能：

```text
使用 $web3-evm-dev，在这个空项目里实现带增发权限的 ERC20，
补充测试，并在本地部署；暂时不连接公共网络。
```

```text
使用 $web3-evm-dev，给现有页面接入 ERC20 转账，
处理 6 位 decimals、拒签和链上失败，沿用当前前端框架。
```

```text
使用 $web3-evm-dev，新建支持中文和英文的 React DApp，
用 RainbowKit 连接钱包，统一主题和交易通知，确认后刷新余额。
```

```text
使用 $web3-evm-dev，修复这个 Hardhat 项目的权限问题，
先复现，再补回归测试，不迁移工具链。
```

```text
使用 $web3-evm-dev，接入已有 ERC-4626 金库的存取款页面，
处理资产/份额单位、舍入、allowance 和交易后刷新，补充边界测试。
```

```text
使用 $web3-evm-dev，为现有钱包接入 ERC-4337 操作与 gas 代付，
先核对目标链、账户 SDK 和 EntryPoint 版本，正确展示失败与费用。
```

## 语言约定

- 英文是仓库文档的主要语言。修改共有内容时，同步维护 [英文 README](README.md) 与本中文版。
- skill 的指令、参考文档、界面元数据及维护者验收场景全部使用英文。每个 skill 只维护一份内容，不再维护独立的中文 skill 副本。
- 源文件语言不强制回复或产品使用英文。沟通遵循用户指定语言，产品遵循项目多语言要求；新 DApp 未指定时仍默认支持简体中文和英文。

## 新增与维护技能

- Web3 技能使用 `web3-生态-能力` 命名，例如 `web3-evm-dev`、`web3-solana-dev`；其他领域按具体任务命名。目录名与 frontmatter 的 `name` 一致。
- 每个技能的 `SKILL.md` 描述触发条件、工作流和完成标准，细节放进自身的参考文件并从入口链接。
- 同级技能分别维护生态差异，不依赖彼此的私有文件。仓库级校验工具可在出现实际重复需求时提取。
- 新增技能时，同时更新中英文 README 索引和 `evals/<skill-name>/scenarios.md`。先验证真实任务，再决定是否增加脚本或模板。
- 维护 SDK、CLI 示例时核对项目版本及官方文档，不把“最新版本”当作永远有效的常量。

EVM 技能的验收输入、环境要求和通过标准见 [验收案例](evals/web3-evm-dev/scenarios.md)。结构校验通过不代表行为验收已通过；执行记录应区分已运行、部分验证和未运行。
