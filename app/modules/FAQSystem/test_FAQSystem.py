from modules.FAQSystem.db_manager import FAQDatabaseManager


def main():
    """FAQ系统测试程序"""
    print("欢迎使用FAQ系统测试程序 👋")

    # 要求用户输入群组ID
    group_id = input("请输入群组ID (默认为'1046961227'): ").strip()
    if not group_id:
        group_id = "1046961227"

    # 创建数据库管理器
    with FAQDatabaseManager(group_id) as db_manager:
        while True:
            print("\n" + "=" * 50)
            print("FAQ系统测试菜单 📋")
            print("=" * 50)
            print("1. 添加问答对 ➕")
            print("2. 查看单个问答对 🔍")
            print("3. 查看所有问答对 📚")
            print("4. 更新问答对 ✏️")
            print("5. 删除问答对 🗑️")
            print("0. 退出测试程序 🚪")
            print("=" * 50)

            choice = input("请选择操作 (0-5): ").strip()

            if choice == "0":
                print("感谢使用FAQ系统测试程序，再见！ 👋")
                break

            elif choice == "1":
                # 批量添加问答对
                print("请输入问答对(每行一组，格式: 问题 答案，直接回车结束):")
                success_count = 0
                fail_count = 0

                while True:
                    line = input().strip()
                    if not line:
                        break

                    try:
                        question, answer = line.split(" ", 1)
                        question = question.strip()
                        answer = answer.strip()

                        if not question or not answer:
                            print("错误: 问题和答案不能为空！ ❌")
                            fail_count += 1
                            continue

                        qa_id = db_manager.add_FAQ_pair(question, answer)
                        if qa_id:
                            print(f"成功添加问答对，ID: {qa_id} ✅")
                            success_count += 1
                        else:
                            print("添加问答对失败 ❌")
                            fail_count += 1
                    except ValueError:
                        print("格式错误，请使用'问题 答案'的格式 ❌")
                        fail_count += 1

                print(f"\n添加完成: 成功 {success_count} 个，失败 {fail_count} 个 📊")

            elif choice == "2":
                # 查看单个问答对
                qa_id = input("请输入要查询的问答对ID: ").strip()

                try:
                    qa_id = int(qa_id)
                    result = db_manager.get_FAQ_pair(qa_id)

                    if result:
                        print(f"ID: {result[0]} 🔢")
                        print(f"问题: {result[1]} ❓")
                        print(f"答案: {result[2]} 💡")
                    else:
                        print(f"未找到ID为 {qa_id} 的问答对 ❌")
                except ValueError:
                    print("错误: ID必须是数字 ❌")

            elif choice == "3":
                # 查看所有问答对
                results = db_manager.get_all_FAQ_pairs()

                if results:
                    print(f"共找到 {len(results)} 个问答对: 📚")
                    for result in results:
                        print("-" * 40)
                        print(f"ID: {result[0]} 🔢")
                        print(f"问题: {result[1]} ❓")
                        print(f"答案: {result[2]} 💡")
                    print("-" * 40)
                else:
                    print("数据库中没有问答对 📭")

            elif choice == "4":
                # 更新问答对
                qa_id = input("请输入要更新的问答对ID: ").strip()

                try:
                    qa_id = int(qa_id)
                    old_qa = db_manager.get_FAQ_pair(qa_id)

                    if not old_qa:
                        print(f"未找到ID为 {qa_id} 的问答对 ❌")
                        continue

                    print(f"当前问题: {old_qa[1]} ❓")
                    print(f"当前答案: {old_qa[2]} 💡")

                    question = input("请输入新问题 (留空则保持原问题): ").strip()
                    answer = input("请输入新答案 (留空则保持原答案): ").strip()

                    question = question if question else old_qa[1]
                    answer = answer if answer else old_qa[2]

                    success = db_manager.update_FAQ_pair(qa_id, question, answer)
                    if success:
                        print("问答对更新成功 ✅")
                    else:
                        print("问答对更新失败 ❌")
                except ValueError:
                    print("错误: ID必须是数字 ❌")

            elif choice == "5":
                # 删除问答对
                qa_id = input("请输入要删除的问答对ID: ").strip()

                try:
                    qa_id = int(qa_id)
                    old_qa = db_manager.get_FAQ_pair(qa_id)

                    if not old_qa:
                        print(f"未找到ID为 {qa_id} 的问答对 ❌")
                        continue

                    print(f"将要删除的问答对:")
                    print(f"问题: {old_qa[1]} ❓")
                    print(f"答案: {old_qa[2]} 💡")

                    confirm = input("确认删除? (y/n): ").strip().lower()
                    if confirm == "y":
                        success = db_manager.delete_FAQ_pair(qa_id)
                        if success:
                            print("问答对删除成功 ✅")
                        else:
                            print("问答对删除失败 ❌")
                    else:
                        print("已取消删除 ⏹️")
                except ValueError:
                    print("错误: ID必须是数字 ❌")

            else:
                print("无效的选择，请重新输入 ⚠️")


if __name__ == "__main__":
    main()
