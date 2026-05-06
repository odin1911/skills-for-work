# 模板文件快速定位规则

## 适用场景

当任务涉及 Egret/EUI 教学模板的源码、皮肤、图集、资源路径定位时，按本规则回源；不要直接凭模板名猜目录。

## 定位顺序

1. 先在 `tools/template.json` 中根据模板 key 查找 `name` 与 `skin`，确认代码目录名和资源目录名。
2. 代码文件优先在 `src/template/<name>/` 查找，至少覆盖：`Main.ts`、`SceneContainer.ts`、`controller/*.ts`、`component/*.ts`、`common/*.ts`。
3. 布局文件优先在 `resource/assets/template/<skin>/eui_skin/` 查找；主皮肤通常是主场景 exml，组件皮肤通常在 `eui_skin/ccomponents/*.exml` 下。
4. 组件与皮肤的绑定关系在 `resource/default.thm.json` 中反查，确认“哪个类对应哪个 exml”。
5. 模板资源组、图集注册关系在 `resource/default.res.json` 中确认；默认只列标准 `1x` 资源路径。

## 补充回源规则

- 若 exml 或代码中出现 `Common_5_json.xxx`、`Common_1_json.xxx` 或 `<模板>_json.xxx` 之类引用，继续追溯对应图集的 `.json` 和 `.png` 文件，并说明该资源用于什么组件或状态。
- 若存在 `DataConst.ts`、`CommonDefine.ts` 等常量文件，优先记录其中的布局常量；若不存在，再从 `controller` / `component` 文件中提取尺寸、gap、offset 和布局计算公式，禁止自行计算。

## 输出要求

- 最终 PRD 必须写清“模板相关文件的位置 + 每个文件的作用”，便于后续溯源时快速定位。
- 文件定位结果不是分析过程中的隐含上下文，必须显式落到 PRD。
