import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "zh-CN",
  title: "W1ndysGroupBot",
  description: "W1ndysGroupBot 的展示和使用文档",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
