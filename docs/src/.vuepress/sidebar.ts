import { sidebar } from "vuepress-theme-hope";

export default sidebar({
  "/QuickStart/": "structure",
  "/UserManual/": [
    {
      text: "命令手册",
      link: "/UserManual/",
      children: [
        "/UserManual/BlackList.md",
        "/UserManual/FAQSystem.md",
        "/UserManual/GroupBanWords.md",
        "/UserManual/GroupHumanVerification.md",
        "/UserManual/GroupManager.md",
        "/UserManual/GroupNickNameLock.md",
        "/UserManual/GroupRandomMsg.md",
        "/UserManual/GroupSpamDetection.md",
        "/UserManual/InviteTreeRecord.md",
        "/UserManual/KeywordsReply.md",
        "/UserManual/WordCloud.md",
      ],
    },
  ],
});
