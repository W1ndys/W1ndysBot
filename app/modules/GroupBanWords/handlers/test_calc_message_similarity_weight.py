from modules.GroupBanWords.handlers.data_manager_words import DataManager

data_manager = DataManager("0")

while True:
    message = input("请输入消息: ")
    result = data_manager.calc_message_similarity_weight(message)
    print(result)
