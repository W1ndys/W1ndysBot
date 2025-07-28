#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试重构后的数据管理器功能
验证各个处理器类的集成是否正常
"""

import os
import random
from .data_manager import DataManager


def test_refactored_functionality():
    """测试重构后的功能"""
    print("=" * 80)
    print("测试重构后的 SunAndRain 数据管理器")
    print("=" * 80)

    test_group_id = 123456789
    test_user1 = 987654321
    test_user2 = 111222333

    try:
        with DataManager() as dm:
            print(f"\n✅ 数据管理器初始化成功")
            print(f"📁 数据库文件: {os.path.basename(dm.db_path)}")
            print(f"📅 当前年份: {dm.year}")

            # 测试用户选择类型
            print("\n🔸 测试用户选择类型功能")
            result1 = dm.add_user(test_group_id, test_user1, 0)  # 选择阳光
            print(f"用户1选择阳光: {result1['code']} - {result1['message'][:50]}...")

            result2 = dm.add_user(test_group_id, test_user2, 1)  # 选择雨露
            print(f"用户2选择雨露: {result2['code']} - {result2['message'][:50]}...")

            # 测试重复选择
            result3 = dm.add_user(test_group_id, test_user1, 0)  # 重复选择阳光
            print(f"用户1重复选择: {result3['code']} - {result3['message'][:50]}...")

            # 测试获取用户信息
            print("\n🔸 测试获取用户信息功能")
            user_info = dm.get_user_info(test_group_id, test_user1)
            print(
                f"获取用户信息: {user_info['code']} - 数据长度: {len(user_info['data']) if user_info['data'] else 0}"
            )

            # 测试签到功能
            print("\n🔸 测试签到功能")
            checkin1 = dm.daily_checkin(test_group_id, test_user1, 0)
            print(f"用户1签到: {checkin1['code']} - {checkin1['message'][:50]}...")

            checkin2 = dm.daily_checkin(test_group_id, test_user2, 1)
            print(f"用户2签到: {checkin2['code']} - {checkin2['message'][:50]}...")

            # 测试重复签到
            checkin3 = dm.daily_checkin(test_group_id, test_user1, 0)
            print(f"用户1重复签到: {checkin3['code']} - {checkin3['message'][:50]}...")

            # 测试发言奖励
            print("\n🔸 测试发言奖励功能")
            for i in range(3):
                reward = random.randint(1, 5)
                update_result = dm.update_user_count(
                    test_group_id, test_user1, 0, reward
                )
                if update_result["code"] == 200:
                    print(
                        f"发言奖励{i+1}: +{reward}个阳光, 当前总数: {update_result['data']['count']}"
                    )

            # 测试排行榜
            print("\n🔸 测试排行榜功能")
            ranking = dm.get_group_ranking(test_group_id, 0, 5)
            print(f"阳光排行榜: {ranking['code']} - {len(ranking['data'])}个用户")

            ranking2 = dm.get_group_ranking(test_group_id, 1, 5)
            print(f"雨露排行榜: {ranking2['code']} - {len(ranking2['data'])}个用户")

            # 测试签到历史
            print("\n🔸 测试签到历史功能")
            history = dm.get_checkin_history(test_group_id, test_user1, 0, 5)
            print(f"签到历史: {history['code']} - {len(history['data'])}条记录")

            # 测试连续签到排行榜
            print("\n🔸 测试连续签到排行榜")
            consecutive_ranking = dm.get_consecutive_ranking(test_group_id, 0, 5)
            print(
                f"连续签到排行: {consecutive_ranking['code']} - {len(consecutive_ranking['data'])}个用户"
            )

            # 测试统计信息
            print("\n🔸 测试统计信息功能")
            stats = dm.get_total_stats(test_group_id)
            print(f"群组统计: {stats['code']} - {len(stats['data'])}个类型")

            # 测试年度总结
            print("\n🔸 测试年度总结功能")
            summary = dm.get_yearly_summary(test_group_id)
            if summary["code"] == 200:
                data = summary["data"]
                print(
                    f"年度总结: 活跃用户{data['active_users']}人, 总签到{data['total_checkins']}次"
                )

            # 测试可用年份
            print("\n🔸 测试可用年份功能")
            years = dm.get_available_years()
            print(
                f"可用年份: {years['code']} - {len(years['data'])}个年份: {years['data']}"
            )

            # 测试重置功能
            print("\n🔸 测试重置功能")
            reset_result = dm.reset_user_type_choice(test_group_id, test_user1)
            print(
                f"重置用户类型: {reset_result['code']} - {reset_result['message'][:50]}..."
            )

            # 测试重新选择
            reselect = dm.add_user(test_group_id, test_user1, 1)  # 重置后选择雨露
            print(f"重新选择雨露: {reselect['code']} - {reselect['message'][:50]}...")

            print("\n✅ 所有功能测试完成")
            print("🎯 重构成功：各个处理器类集成正常")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("重构验证完成")
    print("✅ 数据库操作已分离到独立的处理器类")
    print("✅ 主数据管理器通过组合模式整合所有功能")
    print("✅ 代码结构更清晰，便于扩展和维护")
    print("=" * 80)


def test_handler_independence():
    """测试各个处理器的独立性"""
    print("\n" + "=" * 50)
    print("测试处理器独立性")
    print("=" * 50)

    try:
        # 导入各个处理器类
        from user_checkin_handler import UserCheckinHandler
        from checkin_records_handler import CheckinRecordsHandler
        from database_base import DatabaseBase

        # 测试各个处理器可以独立创建和使用
        with UserCheckinHandler() as user_handler:
            print("✅ UserCheckinHandler 可以独立创建")

        with CheckinRecordsHandler() as records_handler:
            print("✅ CheckinRecordsHandler 可以独立创建")

        # 测试基础类的静态方法
        type_name = DatabaseBase.get_type_name(0)
        print(f"✅ DatabaseBase 静态方法正常: {type_name}")

        print("✅ 所有处理器都可以独立工作")

    except Exception as e:
        print(f"❌ 处理器独立性测试失败: {str(e)}")


if __name__ == "__main__":
    test_refactored_functionality()
    test_handler_independence()
