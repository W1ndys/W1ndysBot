import { navbar } from "vuepress-theme-hope";

export default navbar([
  "/",
  {
    text: "快速开始",
    icon: "rocket",
    prefix: "/QuickStart/",
    link: "/QuickStart/",
  },
  {
    text: "命令手册",
    icon: "book",
    link: "/UserManual/",
  },
]);
