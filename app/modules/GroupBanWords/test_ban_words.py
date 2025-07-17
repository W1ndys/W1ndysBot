from app.modules.GroupBanWords.handlers.data_manager_words import DataManager


if __name__ == "__main__":
    group_id = input("请输入群组ID (默认为'1046961227'，输入0为全局词库): ").strip()
    if not group_id:
        group_id = "1046961227"

    is_global = group_id == "0"
    group_type = "全局词库" if is_global else f"群{group_id}"

    with DataManager(group_id) as dm:
        while True:
            print(f"\n当前操作：{group_type}")
            print("0. 退出 🚪")
            print("1. 检验文本 🔍")
            print("2. 添加违禁词 ⛔")
            print("3. 查看违禁词 📋")
            print("4. 删除违禁词 🗑️")
            print("5. 切换到全局词库 🌍" if not is_global else "5. 切换到群词库 🏠")
            choice = input("请选择操作: ")

            if choice == "1":
                if is_global:
                    print("全局词库无法直接检验文本，请切换到具体群进行检验")
                    continue
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
                        word_type = "全局违禁词" if is_global else "群专属违禁词"
                        print(f"已添加{word_type}: {word} (权值: {weight}) ✅")
                    except ValueError:
                        print("格式错误，请使用'词 权值'的格式 ❌")
            elif choice == "3":
                words = dm.get_all_words_and_weight()
                word_type = "全局违禁词" if is_global else "群专属违禁词"
                print(f"{word_type} ({len(words)}个):")
                for word, weight in words:
                    print(f"  {word}: {weight}")
            elif choice == "4":
                words = dm.get_all_words_and_weight()
                if not words:
                    word_type = "全局违禁词" if is_global else "群专属违禁词"
                    print(f"没有{word_type}")
                    continue
                print("现有违禁词:")
                for word, weight in words:
                    print(f"  {word}: {weight}")
                word_to_delete = input("请输入要删除的违禁词: ").strip()
                if word_to_delete:
                    if dm.delete_word(word_to_delete):
                        print(f"删除成功: {word_to_delete} ✅")
                    else:
                        print(f"未找到: {word_to_delete} ❌")
            elif choice == "5":
                if is_global:
                    new_group_id = input("请输入群号: ").strip()
                    if new_group_id and new_group_id != "0":
                        dm = DataManager(new_group_id)
                        group_id = new_group_id
                        is_global = False
                        group_type = f"群{group_id}"
                else:
                    dm = DataManager("0")
                    group_id = "0"
                    is_global = True
                    group_type = "全局词库"
                print(f"已切换到{group_type}")
            elif choice == "0":
                break
            else:
                print("无效的选择，请重试 ⚠️")
