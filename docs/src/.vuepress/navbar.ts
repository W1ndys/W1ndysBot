import { navbar } from "vuepress-theme-hope";

export default navbar([
  "/",
  {
    text: "快速开始",
    icon: "rocket",
    prefix: "/quickstart/",
    link: "/quickstart/",
  },
  {
    text: "价格",
    icon: "money-bill",
    prefix: "/price/",
    link: "/price/",
  },
]);
