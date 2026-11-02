# Jean Skills

[English](README.md) | 简体中文

面向实际开发任务的通用 Agent Skills 集合，可用于 Codex、Claude Code、Cursor、GitHub Copilot、Gemini CLI 和 OpenCode。每个 skill 独立安装、按需读取参考资料；不同生态使用同级目录，分别维护开发工作流和验收案例。

## 技能目录

| Skill | 用途 | 状态 |
| --- | --- | --- |
| [web3-evm-dev](skills/web3-evm-dev/SKILL.md) | EVM 合约、React DApp、DeFi、智能账户、钱包认证及配套后端 | 已实现 |
| [web3-solana-dev](skills/web3-solana-dev/SKILL.md) | Solana 程序、React DApp、SPL 代币、DeFi 集成、钱包认证及配套后端 | 已实现 |

按目标生态选择技能。两个技能均可独立安装，也可以同时安装。

## 安装

### 直接让 Agent 安装

将下面这段话复制给具备终端和文件操作能力的编程 Agent，无需先手动克隆：

```text
请从 https://github.com/0xJean/Jean-Skills 安装 web3-evm-dev skill，
安装到我当前使用的编程 Agent 的用户级技能目录。
先阅读仓库中的安装说明，使用受支持的安装器，或将完整的
skills/web3-evm-dev 目录（包括 references）复制到该 Agent 官方指定的目录。
替换前检查已有安装。完成后验证文件完整性，并在条件允许时检查技能发现；
告诉我实际安装位置，以及是否还需要刷新或重启。
```

安装 Solana 技能时，发送下面这段话：

```text
请从 https://github.com/0xJean/Jean-Skills 安装 web3-solana-dev skill，
安装到我当前使用的编程 Agent 的用户级技能目录。
先阅读仓库中的安装说明，使用受支持的安装器，或将完整的
skills/web3-solana-dev 目录（包括 references）复制到该 Agent 官方指定的目录。
替换前检查已有安装。完成后验证文件完整性，并在条件允许时检查技能发现；
告诉我实际安装位置，以及是否还需要刷新或重启。
```

如果要让团队随项目共享，将 **“用户级技能目录”** 改为 **“当前仓库的项目级技能目录”**。只有聊天或浏览权限的 Agent 无法安装本地文件，请切换到编程模式，或使用下面的方式。

### 使用 Skills CLI 安装

[Vercel Skills CLI](https://github.com/vercel-labs/skills) 是可选的跨 Agent 安装器，会下载本仓库并安装指定技能；它并非每个 Agent 的内置命令。需要 Git 和 Node.js/npm。本次验证使用的 `skills@1.7.0` 要求 Node.js **22.20.0 或更高版本**。

先查看可安装的技能，不执行安装：

```bash
npx skills add 0xJean/Jean-Skills --list
```

安装到某个 Agent 的用户级目录。下面以 Claude Code 为例，将 `claude-code` 替换成下表对应的 Agent ID：

```bash
npx skills add 0xJean/Jean-Skills --skill web3-evm-dev --agent claude-code --global --copy
```

安装 Solana 技能：

```bash
npx skills add 0xJean/Jean-Skills --skill web3-solana-dev --agent claude-code --global --copy
```

安装到项目时，在目标项目目录执行并去掉 `--global`。可以同时指定多个 Agent：

```bash
npx skills add 0xJean/Jean-Skills --skill web3-evm-dev --agent codex cursor --copy
```

`--copy` 复制完整文件，不依赖符号链接支持。确定作用域、目标 Agent 并检查已有安装后，可加 `--yes` 用于无人值守执行。CLI 自行维护安装目录映射，可能使用共享或兼容目录，与下表的原生目录不同；共享目录可能被多个 Agent 发现。

### 支持的 Agent 与手动安装

技能采用开放的 [Agent Skills 格式](https://agentskills.io/specification)：`SKILL.md` 加本地参考文件。以下目录来自各产品官方文档，需要使用支持 Agent Skills 的当前版本。表格列出手动安装的原生目录，不穷举兼容路径。

| Agent 与官方文档 | CLI 的 `--agent` ID | 项目级技能目录 | 用户级技能目录 |
| --- | --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `codex` | `.agents/skills/` | `~/.agents/skills/` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| [Cursor](https://cursor.com/docs/skills) | `cursor` | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot：[CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) / [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) | `github-copilot` | `.github/skills/` | `~/.copilot/skills/` |
| [Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) | `gemini-cli` | `.gemini/skills/` | `~/.gemini/skills/` |
| [OpenCode](https://opencode.ai/docs/skills/) | `opencode` | `.opencode/skills/` | `~/.config/opencode/skills/` |

手动安装时，克隆或下载[本仓库](https://github.com/0xJean/Jean-Skills)，将 **整个 `skills/web3-evm-dev/` 或 `skills/web3-solana-dev/` 文件夹**复制到选定目录。最终结构必须是 `<技能目录>/<技能名称>/SKILL.md`，并保留同级的 `references/`。只下载 `SKILL.md` 会使参考文档链接失效。更新前检查已有目标，避免在同一个 Agent 会读取的多个目录中重复安装。

`agents/openai.yaml` 是可选的 Codex/OpenAI 界面元数据，通用指令不依赖它。复制时可以保留，但不承诺其他 Agent 会使用其中的外观或调用设置。本仓库分发独立 skills，并非 Claude 或 Cursor 插件市场；这些产品的原生市场导入流程需要额外的插件打包。

上述路径面向本地 Agent。云端 Agent 不会自动读取你电脑上的用户目录，需要使用该环境支持的项目级或远程安装方式。安装这些指令文件不要求 Foundry、Solana/Anchor 工具或区块链凭据；只有实际开发任务需要时才安装对应工具。

### 验证并使用

确认目标目录包含 `SKILL.md` 和所选技能的全部参考文档：EVM 为 8 份，Solana 为 6 份。下面以 `web3-evm-dev` 为例；检查或调用 Solana 技能时，将其替换为 `web3-solana-dev`：

- **Codex：** 使用技能选择器或 CLI/IDE 中的 `/skills`，通过 `$web3-evm-dev` 指定技能；新安装未出现时重启。
- **Claude Code / Cursor：** 使用 `/web3-evm-dev`；Cursor 也支持通过 `@` 选择技能。
- **Copilot CLI：** 执行 `/skills reload`，再用 `/skills info web3-evm-dev` 查看；**VS Code** 使用 `/skills` 或 `/web3-evm-dev`，不要直接套用 CLI 的管理命令。
- **Gemini CLI：** 执行 `/skills reload` 和 `/skills list`，再用自然语言要求使用技能；项目级技能需要工作区受信任，激活时按产品提示完成确认。
- **OpenCode：** 必要时开启新会话，要求加载 `web3-evm-dev`；不可用时检查技能权限设置。

Agent 安装文档核验日期：**2026-09-26**。已使用 `skills@1.7.0` 在临时项目中为全部 6 个 Agent ID 试装 EVM 技能，安装后的 10 个 EVM 技能文件与源文件逐字节一致。这证明安装器输出完整，不代表已在每个 Agent 中完成端到端运行。该版本号是验证记录，并非永久版本要求；如需复现安装器版本，可使用 `npx skills@1.7.0`。

**2026-10-29** 使用同一版本 CLI，从本地工作副本向临时项目为全部 6 个 Agent ID 试装了 `web3-solana-dev`。全部 8 个 Solana 技能文件的 SHA-256 与源文件一致。该检查验证本地打包和安装器输出，不代表已验证 GitHub 发布版本或每个 Agent 内的实际执行。

## 仓库结构

```text
jean-skills/
├── .github/workflows/         # PR 校验与外部链接审计
├── README.md
├── README.zh-CN.md
├── requirements-ci.txt
├── scripts/validate_skills.py
├── tests/test_validate_skills.py
├── skills/
│   ├── web3-evm-dev/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   └── references/        # Contracts, DApp, backend, deployment, and advanced flows
│   └── web3-solana-dev/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
│           ├── programs.md
│           ├── testing.md
│           ├── dapp.md
│           ├── backend.md
│           ├── tokens-defi.md
│           └── deployment.md
└── evals/
    ├── web3-evm-dev/scenarios.md
    └── web3-solana-dev/scenarios.md
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

## Solana 技能的工程约定

| 层次 | 新项目默认 |
| --- | --- |
| 程序 | Rust + Anchor；System/SPL 程序已满足需求时直接复用；校验账户关系、PDA、签名者和 CPI 目标 |
| DApp | React + TypeScript、Wallet Standard、兼容的 Solana Kit 客户端与 React 绑定；保留已有 Anchor/web3.js 客户端约束 |
| 体验与数据 | react-toastify；统一主题与 `zh-CN`/`en-US` 多语言；TanStack Query 缓存及确认执行后的刷新 |
| 配套后端（按需） | Node.js + TypeScript + Prisma + 兼容的 Solana SDK；常驻主机使用 PM2 |
| 测试 | 程序行为、恶意账户输入、数值边界及不变量；按需使用 LiteSVM/Mollusk，并补充本地验证器集成 |
| 部署与签名 | 真实凭据使用硬件/外部签名或获准的加密托管；核对集群、程序/IDL 身份、执行结果和权限 |

Solana SDK 指引已于 **2026-10-29** 对照官方文档核验。新客户端可使用 [Solana Kit 和 React 绑定](https://solana.com/docs/frontend)；选定的 [Anchor TypeScript 客户端](https://www.anchor-lang.com/docs/clients/typescript) 可能依赖旧版 web3.js 类型。技能要求核对版本并保留兼容边界，不强制迁移。Solana JSON keypair 是明文文件，即使设置了助记词恢复口令也不会被加密，不能把它当作加密 keystore。

按任务加载 [SPL Token/Token-2022 与 DeFi](skills/web3-solana-dev/references/tokens-defi.md)、[钱包认证与索引后端](skills/web3-solana-dev/references/backend.md)、[部署与权限管理](skills/web3-solana-dev/references/deployment.md)。交易 blockhash 过期、提交结果不明确、代币扩展、已部署账户布局兼容性都有对应检查。仅在任务需要时增加认证、多签或自定义程序。

## 使用示例

在目标项目中提出具体任务。下面使用技能名称作为通用提示；需要显式加载时，使用上文对应 Agent 的选择器或调用语法：

```text
使用 web3-evm-dev skill，在这个空项目里实现带增发权限的 ERC20，
补充测试，并在本地部署；暂时不连接公共网络。
```

```text
使用 web3-evm-dev skill，给现有页面接入 ERC20 转账，
处理 6 位 decimals、拒签和链上失败，沿用当前前端框架。
```

```text
使用 web3-evm-dev skill，新建支持中文和英文的 React DApp，
用 RainbowKit 连接钱包，统一主题和交易通知，确认后刷新余额。
```

```text
使用 web3-evm-dev skill，修复这个 Hardhat 项目的权限问题，
先复现，再补回归测试，不迁移工具链。
```

```text
使用 web3-evm-dev skill，接入已有 ERC-4626 金库的存取款页面，
处理资产/份额单位、舍入、allowance 和交易后刷新，补充边界测试。
```

```text
使用 web3-evm-dev skill，为现有钱包接入 ERC-4337 操作与 gas 代付，
先核对目标链、账户 SDK 和 EntryPoint 版本，正确展示失败与费用。
```

```text
使用 web3-solana-dev skill，实现支持存入、授权释放和取消的 Anchor 托管程序，
补充恶意账户输入测试，并在本地验证。
```

```text
使用 web3-solana-dev skill，开发中英文 React 代币转账页面，
用 Wallet Standard 连接钱包，核对 Token-2022 支持，处理拒签、过期与刷新。
```

```text
使用 web3-solana-dev skill，修复现有 Anchor/web3.js 集成，不迁移 SDK。
目前 RPC 提交后超时，用户有时会重复付款。
```

```text
使用 web3-solana-dev skill，为这个已部署程序准备升级，
核对账户布局兼容性、IDL/客户端一致性及权限；暂不广播。
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

## 持续集成

[Skills CI](.github/workflows/skills-ci.yml) 在 Pull Request、推送到 `main` 及手动触发时运行。**Validate skills** 检查先运行校验器的回归测试，再校验技能集合：

- **格式：** 必须包含 `SKILL.md`，YAML 有效且无重复键，字段及长度符合 Agent Skills 格式，名称与目录一致，指令非空，并校验可选的 OpenAI 界面元数据。
- **英文内容：** 渲染后的指令、参考正文、界面元数据和验收场景。非拉丁文字正文及高置信度识别出的非英文段落会报错，并定位到文件和行号。语言识别属于启发式检查，不是语法审校；代码示例、URL 和较短的技术标签不参与正文语言分类。根目录的两份 README 继续支持双语。
- **本地引用：** 检查 Markdown 链接和图片，包括引用式链接、文件是否存在，以及 GitHub 风格的标题锚点。技能内的本地链接在解析符号链接后也必须留在自身目录中，保证可以独立安装。忽略代码示例里的链接。

本地使用 Python 3.12 和独立环境运行同样的检查（以下命令适用于 macOS/Linux）：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-ci.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_skills.py
```

依赖安装完成后，校验器离线运行。它检查 [Agent Skills 格式规则](https://agentskills.io/specification) 和仓库约定，不依赖本机安装的编程 Agent。这些依赖只供维护者和 CI 使用，安装 skill 时不需要安装它们。

[External link audit](.github/workflows/external-links.yml) 每周一及手动触发时检查 HTTP(S) 文档链接，使用固定版本的 Lychee 和 [.lychee.toml](.lychee.toml)。检查会跟随重定向、限制每个站点的请求频率、重试失败请求，并写入 GitHub Actions 任务摘要。包括 403/429 在内的 HTTP 错误及超时仍记为失败；需要根据报告区分页面删除、限流和机器人防护。不检查外部 HTML 页面的锚点。外部网站可用性与 PR 校验分开，避免第三方故障阻塞本身有效的修改。安装 Lychee v0.24.2 后，可本地复现：

```bash
lychee --config .lychee.toml --no-progress 'README*.md' 'skills/**/*.md' 'evals/**/*.md'
```

定时和手动工作流需要合并到默认分支后才可使用。本次修改不调整分支保护；首次运行后，维护者可将 **Validate skills** 设为必需检查。

验收输入、环境要求和通过标准见 [EVM 验收案例](evals/web3-evm-dev/scenarios.md) 与 [Solana 验收案例](evals/web3-solana-dev/scenarios.md)。结构校验通过不代表行为验收已通过；执行记录应区分已运行、部分验证和未运行。
