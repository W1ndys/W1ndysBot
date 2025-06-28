from modules.GroupBanWords.data_manager_words import DataManager


if __name__ == "__main__":
    group_id = input("请输入群组ID (默认为'1046961227'): ").strip()
    if not group_id:
        group_id = "1046961227"
    with DataManager(group_id) as dm:
        while True:
            print("\n0. 退出 🚪")
            print("1. 检验文本 🔍")
            print("2. 添加违禁词 ⛔")
            print("3. 添加全局违禁词 🌐")
            print("4. 查看群专属违禁词 📋")
            print("5. 查看全局违禁词 🌍")
            choice = input("请选择操作: ")

            if choice == "1":
                message = input("请输入要检验的文本: ")
                weight, matched_words = dm.calc_message_weight(message)
                print(f"文本总权值: {weight} ⚖️\n")
                print(f"命中的违禁词列表: {matched_words} 📋\n")
                print("=" * 50)
            elif choice == "2":
                print("请输入违禁词和权值(每行一组，格式: 词 权值，直接回车结束):")
                while True:
                    line = input().strip()
                    if not line:
                        break
                    try:
                        word, weight = line.split()
                        weight = int(weight)
                        dm.add_word(word, weight)
                        print(f"已添加群专属违禁词: {word} (权值: {weight}) ✅")
                    except ValueError:
                        print("格式错误，请使用'词 权值'的格式 ❌")
            elif choice == "3":
                print("请输入全局违禁词和权值(每行一组，格式: 词 权值，直接回车结束):")
                while True:
                    line = input().strip()
                    if not line:
                        break
                    try:
                        word, weight = line.split()
                        weight = int(weight)
                        dm.add_global_word(word, weight)
                        print(f"已添加全局违禁词: {word} (权值: {weight}) ✅")
                    except ValueError:
                        print("格式错误，请使用'词 权值'的格式 ❌")
            elif choice == "4":
                words = dm.get_all_words_and_weight()
                print(f"群专属违禁词 ({len(words)}个):")
                for word, weight in words:
                    print(f"  {word}: {weight}")
            elif choice == "5":
                words = dm.get_all_global_words_and_weight()
                print(f"全局违禁词 ({len(words)}个):")
                for word, weight in words:
                    print(f"  {word}: {weight}")
            elif choice == "0":
                break
            else:
                print("无效的选择，请重试 ⚠️")
