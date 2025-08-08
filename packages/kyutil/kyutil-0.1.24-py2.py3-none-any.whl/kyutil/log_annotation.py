import inspect
import json
import os
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from flask import Response, request

from kyutil.base import request_data
from kyutil.enums import BusinessType
from kyutil.exceptions import LoginException, ServiceException, ServiceWarning
from kyutil.model.vo.log_vo import OperLogModel
from kyutil.response_util import ResponseUtil


class Log:
    """
    日志装饰器
    """

    def __init__(
            self,
            title: str,
            business_type: BusinessType,
            log_type='operation',
            current_ui: dict = None,
            db_session=None,
            logger=None
    ):
        """
        日志装饰器

        :param title: 当前日志装饰器装饰的模块标题
        :param business_type: 业务类型（OTHER其它 INSERT新增 UPDATE修改 DELETE删除 GRANT授权 EXPORT导出 IMPORT导入 FORCE强退 GENCODE生成代码 CLEAN清空数据）
        :param log_type: 日志类型（login表示登录日志，operation表示为操作日志）
        :return:
        """
        self.title = title
        self.business_type = business_type.value
        self.log_type = log_type
        self.current_ui = current_ui
        self.db_session = db_session
        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            # 获取被装饰函数的文件路径
            file_path = inspect.getfile(func)
            # 获取项目根路径
            project_root = os.getcwd()
            # 处理文件路径，去除项目根路径部分
            relative_path = os.path.relpath(file_path, start=project_root)[0:-2].replace('\\', '.').replace('/', '.')
            # 获取当前被装饰函数所在路径
            func_path = f'{relative_path}{func.__name__}()'
            # 获取上下文信息
            operator_type = 0
            user_agent = request.headers.get('User-Agent')
            if 'Windows' in user_agent or 'Macintosh' in user_agent or 'Linux' in user_agent:
                operator_type = 1
            if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
                operator_type = 2
            # 获取请求的url
            oper_url = request.url
            # 获取请求的ip及ip归属区域
            oper_ip = request.headers.get('X-Forwarded-For')
            oper_location = '内网IP'
            # 根据不同的请求类型使用不同的方法获取请求参数
            content_type = request.headers.get('Content-Type')
            if content_type and (
                    'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type
            ):
                payload = request.form.to_dict()
                oper_param = '\n'.join([f'{key}: {value}' for key, value in payload.items()])
            else:
                oper_param = request_data(request)
                oper_param = json.dumps(oper_param, ensure_ascii=False)
            # 日志表请求参数字段长度最大为2000，因此在此处判断长度
            if len(oper_param) > 2000:
                oper_param = '请求参数过长'

            # 获取操作时间
            oper_time = datetime.now()
            # 此处在登录之前向原始函数传递一些登录信息，用于监测在线用户的相关信息
            login_log = {}
            try:
                # 调用原始函数
                result = func(*args, **kwargs)
            except (LoginException, ServiceWarning) as e:
                self.logger.warning(e.message)
                result = ResponseUtil.failure(data=e.data, msg=e.message)
            except ServiceException as e:
                self.logger.error(e.message)
                result = ResponseUtil.error(data=e.data, msg=e.message)
            except Exception as e:
                self.logger.exception(e)
                result = ResponseUtil.error(msg=str(e))
            # 获取请求耗时
            cost_time = float(time.time() - start_time) * 100
            # 判断请求是否来自api文档
            request_from_swagger = (
                request.headers.get('referer').endswith('docs') if request.headers.get('referer') else False
            )
            request_from_redoc = (
                request.headers.get('referer').endswith('redoc') if request.headers.get('referer') else False
            )
            # 根据响应结果的类型使用不同的方法获取响应结果参数
            if isinstance(result, Response):
                result_dict = result.get_json()
            else:
                if request_from_swagger or request_from_redoc:
                    result_dict = {}
                else:
                    if result.status_code == 200:
                        result_dict = {'code': result.status_code, 'message': '获取成功'}
                    else:
                        result_dict = {'code': result.status_code, 'message': '获取失败'}
            json_result = json.dumps(result_dict, ensure_ascii=False)
            # 根据响应结果获取响应状态及异常信息
            status = 1
            error_msg = ''
            if result_dict.get('code') == 200:
                status = 0
            else:
                error_msg = result_dict.get('msg')
            # 根据日志类型向对应的日志表插入数据

            oper_name = self.current_ui['username'] if self.current_ui else None
            dept_name = self.current_ui['dept_name'] if self.current_ui else None
            operation_log = OperLogModel(
                title=self.title,
                businessType=self.business_type,
                method=func_path,
                requestMethod=request.method,
                operatorType=operator_type,
                operName=oper_name,
                deptName=dept_name,
                operUrl=oper_url,
                operIp=oper_ip,
                operLocation=oper_location,
                operParam=oper_param,
                jsonResult=json_result,
                status=status,
                errorMsg=error_msg,
                operTime=oper_time,
                costTime=int(cost_time),
            )
            # OperationLogService.add_operation_log_services(query_db, operation_log)
            self.logger.info(self.title + " | " + self.business_type + " | " + func_path + " | " + operator_type)
            return result

        return wrapper


def get_function_parameters_name_by_type(func: Callable, param_type: Any):
    """
    获取函数指定类型的参数名称

    :param func: 函数
    :param param_type: 参数类型
    :return: 函数指定类型的参数名称
    """
    # 获取函数的参数信息
    parameters = inspect.signature(func).parameters
    # 找到指定类型的参数名称
    parameters_name_list = []
    for name, param in parameters.items():
        if param.annotation == param_type:
            parameters_name_list.append(name)
    return parameters_name_list


def get_function_parameters_value_by_name(func: Callable, name: str, *args, **kwargs):
    """
    获取函数指定参数的值

    :param func: 函数
    :param name: 参数名
    :return: 参数值
    """
    # 获取参数值
    bound_parameters = inspect.signature(func).bind(*args, **kwargs)
    bound_parameters.apply_defaults()
    parameters_value = bound_parameters.arguments.get(name)

    return parameters_value
