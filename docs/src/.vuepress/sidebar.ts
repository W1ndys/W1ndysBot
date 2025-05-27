import { sidebar } from "vuepress-theme-hope";

export default sidebar({
  "/QuickStart/": "structure",
  "/UserManual/": [
    {
      text: "命令手册",
      link: "/UserManual/",
      children: [
        "/UserManual/BlackList.md",
        "/UserManual/GroupManager.md",
        "/UserManual/GroupSpamDetection.md",
        "/UserManual/InviteTreeRecord.md",
        "/UserManual/FAQSystem.md",
      ],
    },
  ],
});
