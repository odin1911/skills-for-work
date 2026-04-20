---
name: generate-template
description: 在 courseware-next-frontend 中根据 PRD 文档新建课件模板页面。当用户要求实现某个课件模板（如「实现 KJTF_Q_TF_v2」「根据 PRD 创建模板」「新建模板页面」）时使用。
---

# generate-template Skill

本 skill 定义在 `courseware-next-frontend` 中**新建课件模板页面**的完整步骤与约束。

---

## 前置要求（开始前确认）

1. **用户必须指定 PRD md 文件路径**，这是唯一的功能参考来源
2. 目标页面目录由用户指定；若未指定，按约定推导：模板 key `KJTF_Q_TF_v2` → `src/pages/KJTF_Q_TF_v2_2026/`
3. 读取 PRD 文件，重点提取以下章节：
   - **页面结构**：组件层级、坐标/尺寸
   - **功能逻辑**：初始化流程、作答逻辑
   - **交互逻辑**：触发条件 → 事件链
   - **状态模型**：各状态及转换
4. 忽略 PRD 中：Egret API、exml 皮肤、原始数据接口

> PRD 来源于 tamic-egret 原模板项目，项目背景参考 [docs/skills/tamic-egret.md](../../../docs/skills/tamic-egret.md)

---

## 技术选型规则

遵守 [Contract.md](../../../docs/skills/Contract.md) 全部约束，要点摘要：

- **模板页面使用 React + TypeScript**（交互复杂，符合 React 使用条件）
- 页面尺寸固定 **1024 × 768**，需在不同屏幕上居中缩放适配
- 每个页面必须有独立的 `index.html` 入口
- **禁止**引入 Redux / XState 等重型状态管理
- 路径别名：`@` → `src/`

---

## 样式还原规则（必读，避免常见错误）

> **根本原因：** PRD 文档仅描述功能逻辑，视觉细节（颜色、透明度、按钮外观）存储在 exml 皮肤文件和图集中。凭感觉推断样式会导致与原模板大幅偏差。

### 开始编码前必须读取的文件

| 文件 | 路径模式 | 获取信息 |
|---|---|---|
| 主皮肤 exml | `tamic-egret/resource/assets/template/<模板名>/eui_skin/<模板>ui.exml` | 背景面板 alpha 值、容器坐标 |
| 组件皮肤 exml | `tamic-egret/resource/assets/template/<模板名>/eui_skin/ccomponents/*.exml` | 文字颜色、字号、组件尺寸（`width`/`height`） |
| 图集图片 | `tamic-egret/resource/assets/common/texture/1x/<图集名>.png` | 各状态按钮实际视觉（颜色/形状）|
| 图集 JSON | `tamic-egret/resource/assets/common/texture/1x/<图集名>.json` | 精灵名→坐标映射，用于裁切图片 |
| **布局常数文件** | `tamic-egret/src/template/<模板名>/common/DataConst.ts` | **所有布局常数**：`LINE_GAP`、`OPTION_GAP`、`ITEM_OFFX`、`OPTION_OFFX` 等，**直接照抄，禁止自行计算** |
| **布局逻辑文件** | `tamic-egret/src/template/<模板名>/controller/<Xxx>ViewController.ts` | 组件定位方式（绝对/相对）、偏移计算公式、选项间距规则 |

> 图集名从组件皮肤 exml 的 `source` 属性推断，如 `source="Common_5_json.xxx"` → 图集为 `Common_5`

### 流程优化规则（减少第 1 步耗时）

1. **优先并行读取核心上下文**：首批只读这些文件：PRD、目标页面 `App.tsx`、样式文件、主皮肤 exml、对应组件 exml、布局逻辑文件；能并行就并行，避免逐个试探。
2. **`tamic-egret/` 下的文件优先用 terminal 读取**：该目录在部分环境下**不一定能被 workspace 索引命中**，优先使用 `ls` / `find` / `cat` 定位与读取，**不要先反复用 `file_search` 试探**。
3. **布局常数先看就近文件**：若模板目录下没有 `common/DataConst.ts`，先看组件/控制器里的 `static` 常量（如 `SkeletonsContainerView.ts` 中的 `BASE_Y`、`GAP_TWO`、`MIN_SIZE` 等），**直接以源码证据为准**。
4. **搜索两次未命中就止损**：同一类文件（如基类、DataConst、某个 controller）连续 2 次未找到后，不再继续盲搜；改为：
   - 从已找到的 exml / controller / component 文件提取直接证据；
   - 若仍不足以支撑实现，再**先向用户确认**，不要自行猜测。
5. **基类不是必读项**：像 `QuestionView` 这类继承基类，只有在当前模板文件无法提供关键布局或行为信息时才继续追；若现有 exml + controller 已足够，就直接进入样式修复。

### exml 属性 → CSS 映射规则

| exml 属性 | 含义 | CSS 对应 |
|---|---|---|
| `<Label textColor="0xRRGGBB" />` | 文字颜色（十六进制） | `color: #RRGGBB` |
| `<Label size="N" />` | 字号（1024×768 坐标系中的 px） | `font-size: Npx`（固定画布内直接用 px） |
| `<Label bold="true" />` | 加粗 | `font-weight: bold`（缺少此属性或值为 false 则不加） |
| `<Image alpha="N" />` | 透明度 0~1 | `background: rgba(255,255,255,N)` |
| `<Image source="atlas_json.spriteName" />` | 引用图集中的精灵 | 需查看图集图片确认实际外观 |

**关键原则：**
- `textColor` 就是文字颜色，**不要**因为背景深就假设文字是白色
- `size` 就是字号，模板画布固定 1024×768，**直接对应 `font-size: Npx`，不要换算成 vw/rem**
- 面板 `alpha` 直接对应 CSS 透明度，**不要**自行估算
- 按钮各状态的视觉（边框/填充/阴影）必须**查看图集图片**确认，**不要**假设

### 如何读取图集精灵外观

1. 从组件皮肤 exml 找到各状态所用精灵名，如 `imgNormal` / `imgCorrect` / `imgWrong` / `imgSelect` 的 `source`
2. 从图集 JSON 找到精灵坐标 `{x, y, w, h}`
3. 用 `tools/split-atlas/split_atlas.py` 拆分图集（见下方工具说明），直接查看各精灵图片

### 常见错误及正确做法

| ❌ 错误做法 | ✅ 正确做法 |
|---|---|
| 背景深色 → 推断文字白色 | 读 exml `textColor` → 直接用十六进制值 |
| 凭感觉设字号（如 16px / 18px） | 读 exml `size` → `font-size: Npx` |
| 自行推算布局偏移量（如居中公式） | 读 `DataConst.ts` → 直接照抄 `OPTION_OFFX`、`ITEM_OFFX` 等常数，一个数字都不改 |
| 用固定行高 × 题序号做绝对定位 | 读 `ItemViewController.ts` 布局逻辑：选项 y = `item.y + item.height + LINE_GAP/2 - option.height/2`，应用 flex 列布局使其自动适配多行文字 |
| 凭感觉给按钮背景半透明或加边框 | 用拆图工具查看对应精灵图片，还原实际外观 |
| 背景面板随意设透明度 | 读 exml `alpha` 属性，直接映射 |
| 根容器硬编码主题色（如深蓝、深灰） | 根容器不设背景色或只用 `transparent`；背景图由 `exercise.bgPath` 提供，兜底色用中性浅色（如 `#f0f0f0`）且必须来自 bgPath 实际色调推断 |
| 因 bgPath 未加载就自己补一个「看起来合理」的背景色 | bgPath 未加载时保持透明或极浅中性色，**不推断主题色** |
| 滚动条默认用白色/灰色半透明（`rgba(255,255,255,0.x)`） | 读主皮肤 exml 的 `<tamic_egret:VSliderBar skinName="skins.VSliderBarSkinXxx">` 确认皮肤名 → 读对应 `ccomponents/VSliderBarSkinXxx.exml` 的 `source` 字段 → 用拆图工具查看精灵图片，确认 thumb 和 track 的实际颜色。**示例：** `VSliderBarSkinBlue` 的 thumb 精灵 `common1_scrollBarVThumb` 为 `#32C8ED` 亮青蓝；track `vsbg` 的 `alpha="0.4"` → `rgba(58,107,138,0.4)` 深蓝灰 |
| 题干文本直接用 `white-space: normal`（默认值） | 原 Egret `<Label multiline="true">` 保留换行符。数据中的 `\n` 在 HTML 下必须用 `white-space: pre-line` 才能正常换行；若只用 `dangerouslySetInnerHTML` 而不设该属性，`\n` 会被折叠为空格，换行丢失 |

### 检查清单（Step 1.5 中补充）

在 `prd-analysis.md` 的"Shared 组件映射"章节增加一栏「样式参数速查」，格式：

```markdown
## 样式参数速查（从 exml + 图集读取，禁止估算）
| UI 元素 | exml 来源 | 读取值 | CSS 对应 |
|---|---|---|---|
| 题干文字颜色 | `<Label textColor="0x...">` | 读 ccomponents exml | `color: #...` |
| 题干文字字号 | `<Label size="N">` | 读 ccomponents exml | `font-size: Npx` |
| 选项文字字号 | `<Label size="N">` | 读选项皮肤 exml | `font-size: Npx` |
| 背景面板透明度 | `<Image id="bg" alpha="...">` | 读主皮肤 exml | `rgba(255,255,255,N)` |
| 选项 normal 态外观 | `<Image id="imgNormal" source="...">` | 拆图工具查看精灵 | （填入实际颜色/边框） |
| 选项 correct 态外观 | `<Image id="imgCorrect" source="...">` | 拆图工具查看精灵 | （填入实际颜色/边框） |
| 选项 wrong 态外观 | `<Image id="imgWrong" source="...">` | 拆图工具查看精灵 | （填入实际颜色/边框） |
| 选项 select 态外观 | `<Image id="imgSelect" source="...">` | 拆图工具查看精灵 | （填入实际颜色/边框） |
```

### 拆图工具

```bash
# 安装依赖（仅首次）
pip3 install Pillow

# 拆解指定图集（输出到 tools/split-atlas/output/<图集名>/）
python3 tools/split-atlas/split_atlas.py tamic-egret/resource/assets/common/texture/1x/<图集名>.json
```

输出目录包含所有精灵 PNG 和 `index.html` 预览页。

---

## 参考已有实现

开始前先浏览以下已有模板页面作为参考：

- `src/pages/KJ_ATP_CP_v2_2026/` — 选择题模板（React，含音频、组件拆分）
- `src/pages/KJ_Q_ZP_v2_2026/` — 另一模板参考

---

## 可复用共享组件

优先使用 `src/shared/components/` 中已有组件，避免重复实现：

| 组件 | 路径 | 用途 |
|---|---|---|
| `AudioButton` | `shared/components/audio-button/` | 带音频播放的按钮 |
| `ResetButton` | `shared/components/reset-button/` | 重置按钮（reset_btn.png 背景，无尺寸约束，用 `styled(ResetButton)` 扩展尺寸和定位） |
| `FrameAnimation` | `shared/components/frame-animation/` | 帧动画播放 |
| `SpinePlayer` | `shared/components/spine-player/` | Spine 骨骼动画 |
| `StyledBaseTemplateWrap` | `shared/components/base-template-wrap/` | 带背景图的模板容器 |

---

## 创建步骤

### Step 1 — 读取 PRD

```
read_file(用户指定的 PRD 路径)
```

提取并整理：布局尺寸、组件列表、状态机、交互事件表。

---

### Step 1.5 — PRD 结构化分析（superpower 阶段）

> **目的：** 在编码前完成一次完整的设计推演，生成 `prd-analysis.md` 作为后续所有步骤的"地图"。此步骤直接决定最终代码质量。

在目标页面目录 `src/pages/<page-name>/` 下创建 `prd-analysis.md`，内容必须覆盖以下六个章节：

#### 1. 状态枚举表

列出 PRD 所有**状态节点**，确保无遗漏。格式：

```markdown
| 状态名（枚举值） | 含义 | 进入条件 | 允许的操作 |
|---|---|---|---|
| IDLE | 初始/待作答 | 页面加载完成 | 点击选项 |
| ANSWERED_WRONG_RETRY | 答错可重试 | 答错且未达最大错误数 | 点击其他选项 |
| REVEALED | 正确答案已揭晓 | 答对 或 达最大错误数 | 点选任意项（仅回看） |
```

**要求：** 覆盖 PRD 中所有分支路径；若 PRD 描述模糊，在「风险点」章节标注。

#### 2. 组件树设计

规划 `App.tsx` 下的组件拆分，明确每个组件的职责边界。格式：

```markdown
App
├── StageWrap (1024×768 缩放容器，来自 shared/components/base-template-wrap)
│   ├── QuestionHeader
│   │   ├── QuestionText        — 纯渲染，props: text
│   │   └── AudioButton         — 来自 shared/components/audio-button
│   ├── OptionGrid              — 负责布局计算，props: options, state
│   │   └── OptionItem × N      — 单选项，管理自身动画态
│   └── ResetButton
```

**要求：** 每个组件标注「状态由谁持有」「来自 shared 还是新建」。

#### 3. TypeScript 类型草稿

在编码前定义核心接口，避免后期返工。格式：

```typescript
// 答题状态枚举
type AnswerState = 'IDLE' | 'ANSWERED_WRONG_RETRY' | 'REVEALED'

// 单选项运行时状态
interface OptionRuntime {
  id: string
  isCorrect: boolean
  uiState: 'default' | 'selected' | 'wrong' | 'correct' | 'disabled'
}

// App 主状态
interface AppState {
  answerState: AnswerState
  options: OptionRuntime[]
  errorCount: number
}
```

**要求：** 类型须能完整驱动状态枚举表中的所有转换。

#### 4. Shared 组件映射

明确 PRD 每个 UI 元素对应哪个 shared 组件，或声明需新建：

| PRD 描述 | 实现方案 | 来源 |
|---|---|---|
| 题干音频按钮 | `<AudioButton>` | `shared/components/audio-button` |
| 骨骼动画选项 | `<SpinePlayer>` | `shared/components/spine-player` |
| 1024×768 容器 | `<StyledBaseTemplateWrap>` | `shared/components/base-template-wrap` |
| 帧动画（如有） | `<FrameAnimation>` | `shared/components/frame-animation` |

**要求：** 所有"新建"组件都需理由；若已有 shared 组件满足需求，必须复用。

#### 5. 交互事件表

从 PRD「交互逻辑」章节提炼，格式：

| 触发条件 | 前置状态 | 动作序列 | 后置状态 |
|---|---|---|---|
| 点击选项（正确） | IDLE | 播放 correct_mp3 → showRightAnswer → 全部选项可点 | REVEALED |
| 点击选项（错误，可重试） | IDLE | 切 bg2 → 禁用该项 → 播放 wrong_mp3 → 播放 try_again_mp3 | ANSWERED_WRONG_RETRY |
| 错误达上限 | ANSWERED_WRONG_RETRY | 延迟500ms → showRightAnswer → 全部选项可点 | REVEALED |

**要求：** 每一行对应一个 handler 函数；最终 handler 数量应与表行数一致。

#### 6. 风险点与设计决策

记录 PRD 中的模糊描述、边缘情况和设计取舍：

```markdown
- ⚠️ PRD 第X节"延迟 500ms"：实现时用 setTimeout，需在组件卸载时 clearTimeout
- ⚠️ 选项洗牌依赖 scene.seed：当前阶段 mock 数据可用固定 seed，TODO 注释
- 决策：骨骼选项动画由 SpinePlayer 内部管理，App 层只传 state，不调用动画 API
```

---

> **分析完成后检查：** 六个章节均已填写 → 继续 Step 2；若有章节信息不足，重读 PRD 相关段落补全后再继续。

---

### Step 2 — 创建页面目录结构

```
src/pages/<page-name>/
├── index.html      # 页面入口（必须）
├── main.tsx        # React 挂载入口
├── App.tsx         # 根组件，承载状态机和主逻辑
└── style.css       # 页面全局样式（可选）
```

### Step 3 — 实现 index.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><!-- 模板名 --></title>
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      body {
        margin: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        /* ❌ 不得在此设置 background-color，背景由 exercise.bgPath 提供 */
      }
      #app { width: 100%; height: 100%; }
    </style>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="./main.tsx"></script>
  </body>
</html>
```

### Step 4 — 实现 main.tsx

必须引入全局基础 CSS，并使用项目封装的 `mountReactApp`：

```tsx
import App from './App';
import { mountReactApp } from '@/shared/react/mountApp';
import '@/shared/assets/font/fonts.css';

const app = document.querySelector<HTMLDivElement>('#app');
if (!app) throw new Error('#app not found');

const params = new URLSearchParams(window.location.search);
const unitId = params.get('unitId') || '';
const exerciseId = params.get('exerciseId') || '';

mountReactApp(app, <App unitId={unitId} exerciseId={exerciseId} />);
```

> `fonts.css` 是项目的全局基础样式文件（字体定义 + `button { outline: none }` 等 reset），所有 React 模板页面的 `main.tsx` 均须引入，缺少此引入会导致字体和按钮兼容性问题。

### Step 5 — 实现 App.tsx

> **前置依赖：** 必须先完成 Step 1.5，打开 `prd-analysis.md` 作为参照，对照检查：
> - 状态枚举表 → `useState` / `useReducer` 的状态形状
> - 组件树设计 → 文件拆分方式
> - TypeScript 类型草稿 → 直接复制/调整后使用
> - 交互事件表 → 每行对应一个 handler 函数

- 按 `prd-analysis.md` **状态枚举表**定义本地状态（`useState` / `useReducer`）
- 按 `prd-analysis.md` **组件树**拆分子组件文件
- 按 `prd-analysis.md` **TypeScript 类型草稿**声明接口，放在文件顶部
- 按 PRD **页面结构**还原组件层级，使用 `position: absolute` 还原坐标
- 根容器固定 1024×768，通过 `transform: scale` + `position: fixed` 实现屏幕居中缩放适配：

```tsx
// 根容器样式示例
const stage = {
  width: 1024,
  height: 768,
  position: 'fixed' as const,
  top: '50%',
  left: '50%',
  transform: `translate(-50%, -50%) scale(${scale})`,
  transformOrigin: 'center center',
  overflow: 'hidden',
}
```

- 按 PRD **功能逻辑**实现初始化、交互处理函数
- PRD 中有音频需求时，优先使用 `shared/components/audio-button/`

### Step 6 — 数据层

- **不使用** tamic-egret 原有数据接口
- 数据请求统一使用 `src/shared/core/` 中的 API/Query 方案
- 当前阶段若数据层未就绪，可用 mock 数据占位，并注释 `// TODO: 接入 shared/core API`

### Step 7 — 强制测试（必要环节，禁止跳过）

> **阻塞规则：** 新建模板、修复模板交互或重构模板逻辑时，**必须补测试并实际运行通过**，否则任务不得宣称完成。

最低要求：

1. **状态/纯逻辑测试**
   - 将关键状态判断提炼为纯函数（如交互锁、答题状态转换、重置逻辑）
   - 用 `vitest` 新增回归测试，至少覆盖：
     - 正常作答路径
     - 错误反馈路径
     - 重置或解锁路径

2. **E2E 浏览器测试**
   - 使用 `Playwright` 为模板补至少 1 条端到端用例
   - 必须覆盖 PRD 中最核心的用户链路，尤其是**容易出现时序问题的错误反馈/动画/音频后解锁场景**
   - 优先对接口做**网络层夹具拦截**，保证测试稳定、可重复，不依赖临时 token 或线上环境波动

3. **实际执行验证**
   - 必须真实运行：单测 + E2E + 类型检查
   - 没有 fresh pass 证据，不得说“已完成”

推荐命名：
- 单测：`src/pages/<page-name>/**/*.test.ts`
- E2E：`test/e2e/<page-name>.spec.ts`

### Step 8 — 验证

检查：
- [ ] `prd-analysis.md` 已创建且六个章节均已填写
- [ ] `index.html` 存在且正确引用 `main.tsx`
- [ ] 页面目录位于 `src/pages/` 下（入口由构建脚本自动扫描，无需手动注册）
- [ ] 代码中状态枚举值与 `prd-analysis.md` 状态枚举表完全一致，无遗漏
- [ ] handler 函数数量 = `prd-analysis.md` 交互事件表行数
- [ ] 所有在 Shared 组件映射中标记为「新建」的组件已创建，标记为「复用」的已正确引入
- [ ] `prd-analysis.md` 风险点中所有 `⚠️` 条目均已在代码中处理或添加 TODO 注释
- [ ] 已新增至少 1 个单测回归用例，并通过
- [ ] 已新增至少 1 个 Playwright E2E 用例，并通过
- [ ] 已运行类型检查并通过

---

## 全局基础文件

`src/shared/assets/font/fonts.css` 是项目唯一的全局基础 CSS，包含：
- 字体定义（`heiti`、`Primer Print`、`arial`）
- 全局 reset（`button { outline: none; }` 等）

**所有 React 模板 `main.tsx` 都必须在第一行引入**：
```tsx
import '@/shared/assets/font/fonts.css';
```

若未来需要新增其他全局 reset 规则，也统一写入此文件，不得分散到各页面 CSS 中。

---

## CSS 兼容性规则

- ❌ **不得使用 CSS `gap` 属性**：模板运行于旧版内嵌浏览器，`gap` 在 flex 布局中兼容性不足。
  替代方案：用 `& > *:not(:last-child) { margin-right: Npx; }` 控制元素间距。

- ✅ **`button` 点击出现外边框已在全局处理**：项目全局 CSS（`src/shared/assets/font/fonts.css`）已统一设置 `button { outline: none; }`，组件内无需再处理此问题。若某个按钮需要显示 outline（如无障碍焦点样式），在该组件中显式覆盖即可。

---

## 禁止事项

- ❌ 不得跳过 Step 1.5（PRD 结构化分析），直接编写代码
- ❌ 不得在 `prd-analysis.md` 六个章节未完成前进入 Step 2
- ❌ 不得将新模板合并到已有页面的 HTML 入口
- ❌ 不得引入 Redux / XState / MobX
- ❌ 不得参考或复用 tamic-egret 的 Egret API 代码
- ❌ 不得在未经用户确认的情况下修改 `tamic-egret/` 目录下任何文件
- ❌ 不得在没有 PRD 文件的情况下开始实现
- ❌ **不得自由推断任何颜色值**：所有颜色（文字色、背景色、边框色）必须来自 exml 属性或图集图片，没有来源就留空或用 `transparent`
- ❌ **不得为根容器硬编码主题背景色**：背景由 `exercise.bgPath` 提供，根容器（`SceneContainer` 等）只允许设置 `transparent` 或不设 background
- ❌ **不得在 `index.html` 的 `body` 或任何全局 CSS 中设置背景色**：原 Egret 模板的背景由外层播放器通过 `bgPath` 消息注入，`body` 自身无背景，新实现保持一致
- ❌ **不得因「某种风格看起来合适」就自行追加样式**：未在 exml / 图集中出现的视觉效果一律不加
- ❌ **不得凭感觉估算字号**：所有 `font-size` 必须来自 exml `<Label size="N" />`，模板画布固定 1024×768，`size` 值直接对应 `font-size: Npx`，无需 vw/rem 换算
- ❌ **不得自行推算布局偏移常数**：`LINE_GAP`、`OPTION_GAP`、`ITEM_OFFX`、`OPTION_OFFX` 等必须来自 `DataConst.ts`，照抄原始值，不得用「居中公式」重新计算
- ❌ **不得用固定行高乘以题序号做绝对定位**：题目行高由文字多行自动撑开，选项紧贴题目文本而非固定偏移，必须用 flex 列布局，按 `ItemViewController.ts` 布局公式实现
