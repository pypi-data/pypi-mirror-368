# -*- coding: utf-8 -*-
import json
import random
import os
import time
import base64
from datetime import datetime, timedelta
from typing import Union, Dict, Literal, List, Optional
from sqlalchemy import create_engine, Table, Column, CHAR, Text, DateTime, Integer, Date, inspect, JSON, Index, \
    UniqueConstraint, func, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT, BLOB

class SqlalchemyService:
    def __init__(self,
                 cut: Literal['DB', 'MYSQL'] = 'MYSQL',
                 db_file: str = '',
                 db_path: str = '',
                 table_name: str = '',
                 mysql_config: dict = None,
                 pool_size: int = 200,
                 Base: declarative_base = None,
                 maximum_retention_period: int = 50,
                 maximum_number_of_single_storage: int = 1000,
                 del_expired_data: bool = True
                 ):
        """
        :param cut: 数据库类型，支持本地db文件数据库 或 mysql数据库
        :param db_path: db文件的存储路径，列：D:/tmp/cache，，通常是固定的，这只是个路径
        :param db_file: db文件名称，列：cache.db，通常是固定的，这只是个文件（含后缀）
        :param table_name: 要读取或创建的表名称
        :param mysql_config: MYSQL的配置
        :param pool_size: 连接池大小设置
        :param Base: 基础声明，是否共享
        :param maximum_retention_period: 可保留数据最长有效期（天）
        :param maximum_number_of_single_storage: 单次最多可插入或更新多少条数据（表是灵活的，此限制是代码的限制，并非表的限制）
        :param del_expired_data: 初始化时删除过期数据
        """
        self.cut = cut.upper()
        self.pool_size = pool_size
        self.Base = Base
        assert table_name,  f'[{self.cut}][table_name]要读取或创建的表名称不能为空'
        if cut == 'DB':
            # 路径
            file_path = db_path or os.path.dirname(__file__)
            # 文件夹创建
            if not os.path.exists(file_path): os.makedirs(file_path, exist_ok=True)
            # 绝对路径
            self.db_file = os.path.join(file_path, db_file or "cache.db")
            self.engine = create_engine(f'sqlite:///{self.db_file}', pool_size=self.pool_size, echo=False)
        elif cut == 'MYSQL':
            # MySQL配置改为参数传入
            MYSQL_config = mysql_config or {
                'USER': 'www',  # MySQL用户名
                'PASSWORD': '123456',  # MySQL密码
                'HOST': '192.168.1.91',  # MySQL服务器地址
                'PORT': '3306',  # MySQL端口，默认3306
                'NAME': 'rpa_local'  # 数据库名称，此处使用'rpa_local'作为默认数据库
            }
            # 本段代码用于创建与数据库的连接，使用mysql+pymysql作为数据库引擎
            user = MYSQL_config['USER']
            password = MYSQL_config['PASSWORD']
            host = MYSQL_config['HOST']
            port = MYSQL_config['PORT']
            name = MYSQL_config['NAME']
            self.engine = create_engine(
                f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}',  # 创建MySQL数据库连接引擎
                pool_size=self.pool_size,  # 连接池大小设置为20
                echo=False,  # 不输出SQL日志
                pool_recycle=3600,  # 连接回收时间设为3600秒(1小时)
                pool_pre_ping=True  # 启用连接前ping检测，确保连接有效性
            )
        else:
            raise ValueError(f'数据库类型错误，请检查数据库类型 - [{self.cut}]')

        # 定义Session，绑定数据库引擎
        self.Session = sessionmaker(bind=self.engine)
        # 表名称 用于检测是否已经存在此表，如果已经存在，则不创建表
        self.table_name = ''
        # 模型定义 占位
        self.DynamicProduct = None

        # ----- [Temporary local storage space][临时本地存储空间]
        # 可保留数据最长有效期（天）
        self.maximum_retention_period = maximum_retention_period
        # 单次最多可插入或更新多少数据
        self.maximum_number_of_single_storage = maximum_number_of_single_storage
        # 动态模型定义[通用型]
        self.dynamics_model_definition(table_name=table_name, table_model='1')
        # 创建表[通用型]
        self.create_table()
        if del_expired_data and (30 - int(time.time()) % 30) > 10:
            # 删除所有已过期的数据
            self.local_remove_data(remove_expired=True)

    # 创建动态表[通用数据临时存储表]
    def general_temporary_Table_MYSQL(self, table_name):
        """
        @Title    : 动态模型定义
        @Desc     : 创建动态表[通用数据临时存储表], 这个模型和浏览器的本地存储空间是一样的，但这个还有一个额外的功能，数据到期时间，如果时间戳小于当前时间，则会把数据删除(手动触发删除)
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - table_name: 表的名称
        """
        # 使用 type 创建动态模型类
        return type(table_name, (self.Base,), {
            '__tablename__': table_name,
            # 表格的引擎、字符集等其他选项，可以在 `__table_args__` 中指定
            '__table_args__': (
                Index(f'idx_{table_name}_timestamp_end', 'timestamp_end'),  # 单列索引
                UniqueConstraint('Key', name=f'uq_{table_name}_key'),  # 唯一约束
                {
                    'mysql_engine': 'InnoDB',
                    'mysql_charset': 'utf8mb4',
                    'mysql_collate': 'utf8mb4_general_ci'
                }),
            'id': Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='自增id'),
            'timestamp_end': Column(Integer, nullable=False, comment='10位时间戳,数据过期时间'),
            'Key': Column(CHAR(100), nullable=False, comment='键', index=True),  # 使用CHAR(100)固定长度存储键值，提高查询效率，确保索引性能稳定
            'Value': Column(LONGTEXT, nullable=False, comment='值'),
        })
    # 创建动态表[通用数据临时存储表]
    def general_temporary_Table_DB(self, table_name):
        """
        @Title    : 动态模型定义
        @Desc     : 创建动态表[通用数据临时存储表], 这个模型和浏览器的本地存储空间是一样的，但这个还有一个额外的功能，数据到期时间，如果时间戳小于当前时间，则会把数据删除(手动触发删除)
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - table_name: 表的名称
        """
        # 使用 type 创建动态模型类
        return type(table_name, (self.Base,), {
            '__tablename__': table_name,
            # 表格的引擎、字符集等其他选项，可以在 `__table_args__` 中指定
            '__table_args__': (
                Index(f'idx_{table_name}_timestamp_end', 'timestamp_end'),  # 单列索引
                UniqueConstraint('Key', name=f'uq_{table_name}_key'),  # 唯一约束
                {
                    'mysql_engine': 'InnoDB',
                    'mysql_charset': 'utf8mb4',
                    'mysql_collate': 'utf8mb4_general_ci'
                }),
            'id': Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='自增id'),
            'timestamp_end': Column(Integer, nullable=False, comment='10位时间戳,数据过期时间'),
            'Key': Column(CHAR(100), nullable=False, comment='键', index=True),  # 使用CHAR(100)固定长度存储键值，提高查询效率，确保索引性能稳定
            'Value': Column(Text, nullable=False, comment='值'),
        })

    def dynamics_model_definition(self, table_name: str = '', table_model: Literal['1'] = '') -> Union[int, ValueError]:
        """
        @Title    : 动态模型定义[通用型]
        @Desc     : 动态定义表的模型，用于创建或读取数据表
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - table_name: 表的名称，用来对表定义模型并创建表，如果表已经存在，则不会创建
            - table_model：选择模型 要用什么模型创建表或读取表
                - 1: [通用数据临时存储表]模型
        @Returns  :  # 1成功  0失败  仅返回成功或失败的状态码
        """
        if not table_name or not table_model:
            raise ValueError(f'[{self.cut}]表名称不能为空/模型不能为空')
        self.table_name = table_name
        # 模型已存在
        if table_name in self.Base.registry._class_registry:
            self.DynamicProduct = self.Base.registry._class_registry[table_name]  # 返回已存在的模型
            return 1
        # 模型选择定义
        if table_model == '1':
            if self.cut == 'MYSQL':
                # 模型定义[通用数据临时存储表]模型
                self.DynamicProduct = self.general_temporary_Table_MYSQL(table_name)
            elif self.cut == 'DB':
                # 模型定义[通用数据临时存储表]模型
                self.DynamicProduct = self.general_temporary_Table_DB(table_name)
            else:
                raise ValueError(f'数据库类型错误，请检查数据库类型 - [{self.cut}]')
        else:
            raise ValueError(f'[{self.cut}]没有此模型，定义失败')
        # 模型定义完成
        return 1

    def create_table(self) -> int:
        """
        @Title    : 创建表[通用型]
        @Desc     : 通过以定义的模型创建表，如果已经存在则不会创建
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Returns  : # 1成功  0失败  仅返回成功或失败的状态码
        """
        # 创建一个检查器
        inspector = inspect(self.engine)
        # 判断表格是否存在    nspector.get_table_names() 获取所有的表名称
        if self.table_name not in inspector.get_table_names():
            # 创建该表(通过模型创建)
            self.Base.metadata.create_all(self.engine)
            # 创建表完成
            return 1
        # 表已经存在，不执行创建表
        return 1

    def local_query_data(self, key: str = '') -> Union[list, dict, ValueError]:
        """
        @Title    : 查询全部数据/查询某个键数据 [Temporary local storage space][临时本地存储空间]
        @Desc     : 仅用于临时本地存储空间，查询全部数据/查询指定键. （自带默认-自动·删除过期数据(timestamp_end < 当前时间)）
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - key: 要查询的Key，如果不填写，则默认会查询获取所有数据
        @Returns  : #  仅返回查找后的结果，查找全部数据，返回列表。查找单个键，返回为字典
        """
        self.create_table()
        if not self.DynamicProduct:
            raise ValueError(f'[{self.cut}][查询]请先选择或创建表')
        # 使用上下文管理器自动管理会话
        with self.Session() as session:
            try:
                current_time = int(time.time())
                # 查询未过期的数据
                AccountQueryNumber = session.query(self.DynamicProduct).filter(
                    self.DynamicProduct.timestamp_end > current_time
                )
                if key != '':
                    AccountQueryNumber = AccountQueryNumber.filter(self.DynamicProduct.Key == key)

                # 提取结果为列表字典
                dict_results = [
                    {
                        'id': row.id,
                        'timestamp_end': row.timestamp_end,
                        'Key': row.Key,
                        'Value': row.Value
                    }
                    for row in AccountQueryNumber
                ]

                # # 是否要搜索某个键的数据
                # if key != '':
                #     # 搜索数据
                #     _dict_results: Union[dict, str] = (
                #         lambda dict_results: ([results for results in dict_results if results['Key'] == key] + [''])[
                #             0])(dict_results)
                #     if _dict_results == '':
                #         # 不存在此键
                #         return {}
                #     # 查找单个键成功
                #     return _dict_results
                if key != '':
                    return dict_results and dict_results[0] or {}
                # 成功获取全部数据
                return dict_results or {}
            except Exception as e:
                session.rollback()
                raise ValueError(f"[{self.cut}]从表导出数据时出错: {str(e)}")

    def local_insert_data(self, data_dict_list: Union[List[dict], dict], timestamp_end_up=True) -> Union[int, ValueError]:
        """
        @Title    : 插入数据/更新数据 [Temporary local storage space][临时本地存储空间]
        @Desc     : 插入数据，更新数据，可传递列表内嵌多字典数据，或单字典数据（单次插入或更新的数据不能超过设置的最大限制，具体看[self.maximum_number_of_single_storage]参数）这是规则
                新增限制：
                    1. timestamp_end与当前时间戳不能相差超过设置的具体天数，具体看[self.maximum_retention_period]参数
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - data_dict_list: 要存储/更新的数据 列表内嵌字典：[{...},{...},{...},{...}] 或 单字典：{...}
            - timestamp_end_up: 是否更新时间戳
        @Returns  : # 1成功  0失败  仅返回成功或失败的状态码
        """
        self.create_table()
        if not self.DynamicProduct:
            raise ValueError(f'[{self.cut}][插入数据]请先选择或创建表')
        # 检查数据量限制
        if isinstance(data_dict_list, list) and len(data_dict_list) > self.maximum_number_of_single_storage:
            raise ValueError(f'[{self.cut}]一次最多只能插入/更新{self.maximum_number_of_single_storage}条数据')
            # 使用上下文管理器自动管理会话
        with self.Session() as session:
            try:
                current_time = int(time.time())
                # 将天数转换为秒
                fifty_days = self.maximum_retention_period * 24 * 60 * 60
                # 统一处理输入数据
                data_list = [data_dict_list] if isinstance(data_dict_list, dict) else data_dict_list

                # 检测数据格式
                for data in data_list:
                    # 检查必要字段
                    if 'Key' not in data or 'Value' not in data or 'timestamp_end' not in data or len(
                            str(data.get('timestamp_end'))) != 10:
                        raise ValueError(f'[{self.cut}]数据格式不正确，必须包含Key、Value和timestamp_end字段')

                    if not isinstance(data['Value'], str):
                        data['Value'] = json.dumps(data['Value'])
                    # 检查字段类型
                    if not all([
                        isinstance(data['timestamp_end'], int),
                        isinstance(data['Key'], str),
                        isinstance(data['Value'], str)
                    ]):
                        raise ValueError(f'[{self.cut}]Key、Value和timestamp_end的类型错误')
                    # 检查时间戳有效性
                    if data['timestamp_end'] <= current_time:
                        raise ValueError(f'[{self.cut}]timestamp_end必须大于当前时间戳')
                    # 检查时间戳是否在50天内
                    if abs(data['timestamp_end'] - current_time) > fifty_days:
                        raise ValueError(
                            f'[{self.cut}]timestamp_end只能设置在{self.maximum_retention_period}天内，不能超过这个最大存储时间')
                    # 检测Key的长度有没有超标
                    if len(data['Key']) > 100:
                        raise ValueError(f'[{self.cut}]Key的长度不能超过100个字符')
                # 遍历每个数据
                for data in data_list:
                    # 查找是否已存在相同Key的记录
                    existing = session.query(self.DynamicProduct).filter(self.DynamicProduct.Key == data['Key']).first()
                    # 如果存在 则执行更新 所有键值信息
                    if existing:
                        # 更新现有记录
                        for key, value in data.items():
                            if hasattr(existing, key) and (timestamp_end_up == True or key != 'timestamp_end'):
                                setattr(existing, key, value)
                    else:
                        # 插入新记录
                        product = self.DynamicProduct(**data)
                        session.add(product)
                session.commit()
                # 数据插入成功
                return 1
            except Exception as e:
                session.rollback()
                raise ValueError(f'[{self.cut}]数据插入失败: {e}')

    def local_remove_data(self, key: Union[str, List[str]] = None, remove_all: bool = False,
                          remove_expired: bool = False) -> Union[int, ValueError]:
        """
        @Title    : 删除数据 [Temporary local storage space][临时本地存储空间]
        @Desc     : 删除指定键、所有键或过期键的数据
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - key: 要删除的键(单个字符串或字符串列表)，可选
            - remove_all: 是否删除所有键，默认为False，可选
            - remove_expired: 是否删除过期数据(timestamp_end < 当前时间)，默认为False，可选
        @Returns  :  1成功  0失败  仅返回成功或失败的状态码
        """
        self.create_table()
        if not self.DynamicProduct:
            raise ValueError(f'[{self.cut}][删除数据]请先选择或创建表')

        # 参数校验
        if sum([key is not None, remove_all, remove_expired]) > 1:
            raise ValueError(f'[{self.cut}]每次只能使用一种删除模式')

        with self.Session() as session:
            try:
                # 情况1: 删除指定键
                if key is not None:
                    keys_list = [key] if isinstance(key, str) else key
                    # 优化版
                    session.query(self.DynamicProduct).filter(
                        self.DynamicProduct.Key.in_(keys_list)
                    ).delete(synchronize_session=False)
                    # for _key in keys_list:
                    #     # 查找并删除指定键
                    #     session.query(self.DynamicProduct) \
                    #         .filter(self.DynamicProduct.Key == _key) \
                    #         .delete(synchronize_session=False)

                # 情况2: 删除所有数据
                elif remove_all:
                    session.query(self.DynamicProduct) \
                        .delete(synchronize_session=False)

                # 情况3: 删除过期数据
                elif remove_expired:
                    current_time = int(time.time())
                    session.query(self.DynamicProduct) \
                        .filter(self.DynamicProduct.timestamp_end < current_time) \
                        .delete(synchronize_session=False)
                else:
                    # 删除操作完成
                    return 1
                session.commit()
                # 删除操作完成
                return 1

            except Exception as e:
                session.rollback()
                raise ValueError(f'[{self.cut}]删除数据时发生错误: {str(e)}')

    def time(self, minutes: Union[int, float]=0, tianchao:str='', fixed:list=None) -> int:
        """
        @Desc     : 时间戳
        @Author   : 祁国庆
        @Time     : 2025/04/23 18:21:23
        @Params   :
            - minutes: 相对当前时间保存多少分钟（分钟）
            - tianchao: 相对当天时间保存至什么时间（天）
                当前时间为：2025-04-02
                例如:  0.0.0=2025-04-02 00:00:00    0.1.0=2025-04-02 01:00:00  0.1.1=2025-04-02 01:59:59
                例如:  1.0.0=2025-04-03 00:00:00    1.1.0=2025-04-03 01:00:00  1.1.1=2025-04-03 01:59:59
                拆分:  3.2.1 == 3：2025-04-05(天数+3)  2：02:00:00(2代表小时，最高为23，最小为0)  1：00:59:59(代表分钟和秒,0为00:00,1为59:59)
            - fixed: 基于本周 周1-周日的时间戳（week） | 基于本月 1-31日时间戳（month）
                当前时间为：2025-04-02
                获取4月2号当前周的周5时间戳 例如：['周', 5]
                获取4月2号当前周的周日时间戳 例如：['周', 7]
                获取4月2号当月的29号时间戳 例如：['月', 29]
                注意：如果当月最大天数小于29天，则会以当月最大天数代替，例如2月只有28天，如果填入['月', 31]，则会获取当月的第28天时间戳
                注意：可设置时间最长为每周的周日晚上23点59分59秒 和 每月的最后一天的晚上23点59分59秒，超出则直接按最大设置
        @Returns  : 标准的10位时间戳
        """
        # 获取当前时间
        now = datetime.now()
        if tianchao:
            assert not tianchao.count('.') != 2, f'[{self.cut}]格式错误'
            assert not int(tianchao.split('.')[0]) > self.maximum_retention_period, f'[{self.cut}]存储时间不能超过{self.maximum_retention_period}天'
            assert not int(tianchao.split('.')[1]) > 23, f'[{self.cut}]小时设置错误 只能是[0-23]'
            assert not int(tianchao.split('.')[2]) > 1, f'[{self.cut}]分秒设置错误 只能是[0/1]'
            # 将时、分、秒、微秒设置为 0
            today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # 转换为时间戳（Unix 时间戳，单位：秒）
            timestamp = int(today_midnight.timestamp()) + (60 * 60 * 24) * int(tianchao.split('.')[0])
            # 4. 将新时间戳转回 datetime 对象
            new_date = datetime.fromtimestamp(timestamp)
            # 5. 格式化为 "YYYY-MM-DD" 字符串
            formatted_date = new_date.strftime("%Y-%m-%d")
            return int(time.mktime(datetime.strptime(formatted_date + ' ' + tianchao.split('.')[1] + ':' + (
                    (tianchao.split('.')[2] == '1') and '59:59' or '00:00'), "%Y-%m-%d %H:%M:%S").timetuple()))
        elif minutes != 0:
            if minutes < 0.1: minutes = 0.1
            # 当前时间 + 指定分钟数 → 直接计算时间戳
            return int((now + timedelta(minutes=minutes)).timestamp())
        elif fixed:
            if fixed[0] == '周':
                fixed[1] = int(fixed[1])
                if fixed[1] > 7: fixed[1] = 7
                if fixed[1] < 1: fixed[1] = 1
                # today.weekday()  周1 - 周日 分别为 0-6
                days_to_saturday = fixed[1] - 1 - now.weekday()
                if days_to_saturday < 0:  # 如果日期小于当前日期，则直接返回周日
                    days_to_saturday = 6 - now.weekday()
                saturday_midnight = (now + timedelta(days=days_to_saturday)).replace(
                    hour=23, minute=59, second=59, microsecond=0
                )
                return int(saturday_midnight.timestamp())
            elif fixed[0] == '月':
                fixed[1] = int(fixed[1])
                # 获取当前是几号（1-31）
                current_day = now.day
                # 计算当前月份总天数
                # 方法：获取下个月1号，然后减去1天得到本月最后一天
                if now.month == 12:
                    next_month = datetime(now.year + 1, 1, 1)
                else:
                    next_month = datetime(now.year, now.month + 1, 1)

                last_day_of_month = next_month - timedelta(days=1)
                # 本月最大天数
                total_days = last_day_of_month.day
                if fixed[1] > total_days: fixed[1] = total_days
                if fixed[1] < 1: fixed[1] = 1
                if fixed[1] < current_day: fixed[1] = current_day
                days_to_saturday = fixed[1] - current_day
                saturday_midnight = (now + timedelta(days=days_to_saturday)).replace(
                    hour=23, minute=59, second=59, microsecond=0
                )
                return int(saturday_midnight.timestamp())
        else:
            return int(time.time() + 1000)

class BaseCache(SqlalchemyService):
    '''通用缓存类，抽象 get/set/del 等操作'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_data(self, *, key: str) -> Union[dict, list, None]:
        '''获取数据'''
        result = self.local_query_data(key=key)
        return json.loads(result['Value']) if result else None

    def set_data(self, *, key: str, data: Union[dict, list, str], timestamp_end=None, timestamp_end_up=False):
        '''写入数据'''
        self.local_insert_data(data_dict_list={
            "timestamp_end": timestamp_end or self.time(tianchao='1.1.1'),
            "Key": key,
            "Value": data
        }, timestamp_end_up=timestamp_end_up)

    def del_data(self, *, key: str):
        '''删除数据'''
        self.local_remove_data(key=key)

class EMAIL_DedicatedDataCaching(BaseCache):
    '''email数据cookie专用'''
    def __init__(self):
        # 基础声明(不共享模型，独立模型)
        Base = declarative_base()
        super().__init__(cut='MYSQL',
                         table_name='email_cookie',
                         pool_size=20,
                         Base=Base)

"""
1:这是一个`模拟浏览器本地存储空间`的数据库，仅作为临时存储使用，不可存储太多无用的数据，用完记得清除数据
2:当然，也可作为临时缓存，存储一些任务快照信息，任务中断可以续上，也可以存储一些固定的数据，可避免重复
  性的采集相同固定的数据，例如：账单..这种属于固定的数据，不会有变动，则可以用缓存保存，下次则可以直
  接提取缓存保存的数据
3:通过继承方法来使用他，也可以自定义创建动态表，方便快捷，支持扩展，支持共享

[插入数据] timestamp_end：设置过期时间，10位时间戳，可使用time(5)自动生成，5代表5分钟后的时间戳   如果键重复，则会更新键的值和过期时间
data_dict = {"timestamp_end": DBGiveInvitation.time(3), "Key": '键', "Value": '值'}
DBGiveInvitation.local_insert_data(data_dict, timestamp_end_up=True)  # timestamp_end_up：True每次保存都更新时间戳 False时间戳已经存在则不更新时间戳

[查询数据] 只能通过建查找
DBGiveInvitation.local_query_data(key='键')

[删除数据] 三个删除规则不能同时使用
DBGiveInvitation.local_remove_data(key='键')   # 通过键删除一条数据 用列表可以删除多个
DBGiveInvitation.local_remove_data(remove_expired=True)   # 删除所有已过期的数据
DBGiveInvitation.local_remove_data(remove_all=True)   # 删除所有数据
"""

__all__ = [
    'EMAIL_DedicatedDataCaching'
]

# if __name__ == '__main__':
#     DBGiveInvitation = LAZADA_ProductsExclusivelyParticipating()
#     # 插入数据
#     data_dict = {"timestamp_end": DBGiveInvitation.time(fixed=['周', 6]), "Key": 'cshannel-id', "Value": [
#         {
#             "channelIndexUrl": "111111",
#             "channelName": "Miravia",
#             "channelSite": "ES",
#             "channelType": "ARISE",
#             "order": 301,
#             "shopLogoUrl": "https://img.alicdn.com/imgextra/i2/O1CN01vIpO4B1YHcQvYCnen_!!6000000003034-55-tps-94-94.svg",
#             "shopModel": "POP",
#             "shopName": "Miravia Store",
#             "shopStatusId": 4,
#             "shopStatusName": "待激活"
#         }
#     ]}
#     # print(DBGiveInvitation.local_insert_data(data_dict, timestamp_end_up=True))
#     print(DBGiveInvitation.local_query_data(key='501421024585_PH_add39OAACI_436595|326653_b62b0b8d6261e824a944e5b528875e6a'))
#
#     #
#     # 查询数据
#     # print(DBGiveInvitation.local_query_data(key='cshannel-id'))
#     # print(DBGiveInvitation.local_query_data(key='channel-id').get('Value'))
#     # # 删除全部数据
#     # DBGiveInvitation.local_remove_data(remove_all=True)


