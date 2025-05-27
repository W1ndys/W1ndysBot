import { defineUserConfig } from "vuepress";

import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "zh-CN",
  title: "W1ndysBot",
  description: "W1ndysBot 的展示和使用文档",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
