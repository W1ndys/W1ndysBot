from modules.GroupBanWords.data_manager_words import DataManager


if __name__ == "__main__":
    group_id = "1046961227"
    with DataManager(group_id) as dm:
        while True:
            message = input("请输入要检验的文本: ")
            weight, matched_words = dm.calc_message_weight(message)
            print(f"文本总权值: {weight}\n")
            print(f"命中的违禁词列表: {matched_words}\n")
            print("=" * 50)
