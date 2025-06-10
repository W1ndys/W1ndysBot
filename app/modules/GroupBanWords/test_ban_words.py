from modules.GroupBanWords.data_manager_words import DataManager


if __name__ == "__main__":
    group_id = "1046961227"
    with DataManager(group_id) as dm:
        while True:
            message = input("请输入要检验的文本: ")
            weight = dm.calc_message_weight(message)
            print(f"文本总权值: {weight}")
