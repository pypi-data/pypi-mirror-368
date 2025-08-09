from robot_base import log_decorator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@log_decorator
def connect_database(
	database_type='sqlite3',
	database_path='',
	host='localhost',
	port=3306,
	user='root',
	password='',
	database='',
	**kwargs,
):
	if database_type == 'sqlite3':
		engine = create_engine(f'sqlite:///{database_path}')
		return engine
	elif database_type == 'mysql':
		engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8')
		return engine
	else:
		raise Exception('暂不支持的数据库类型')


@log_decorator
def execute_sql(database_instance, sql, params=None, **kwargs):
	sql = text(sql)
	# 创建一个Session类
	Session = sessionmaker(bind=database_instance)
	# 创建会话实例
	session = Session()

	# 执行插入语句
	try:
		# 传递插入的数据作为关键字参数
		session.execute(sql, params)
		session.commit()  # 提交事务
	except Exception as e:
		session.rollback()  # 如果发生异常，回滚事务
		raise e
	finally:
		session.close()  # 确保会话被关闭


@log_decorator
def execute_query(database_instance, sql, params=None, **kwargs):
	sql = text(sql)
	with database_instance.connect() as connection:
		result = connection.execute(sql, params)
		return result.fetchall()
