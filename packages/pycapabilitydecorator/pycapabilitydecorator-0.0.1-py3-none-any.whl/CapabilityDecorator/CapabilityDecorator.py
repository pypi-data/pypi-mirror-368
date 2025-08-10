# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "click>=8.1.8",
#     "Flask>=2.3.3",
# ]
# ///

'''
@File    :   CapabilityDecorator.py
@Time    :   2025/07/29 20:50:32
@Author  :   LX
@Version :   1.0.0
@Desc    :   Capability 元数据与 CLI 命令自动注册系统
'''

import click
import json
import base64
import inspect
import os
from functools import wraps
from typing import Any, Dict, List, Optional, Callable
from io import StringIO
import sys
import atexit


class CapabilityDecorator:
    """Capability 元数据与 CLI 命令自动注册系统管理类"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CapabilityDecorator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # --- 全局存储 ---
        # 存储所有 capability 的元数据，key 为 capability name
        self._CAPABILITIES: Dict[str, Dict[str, Any]] = {}
        # 存储所有待注册的 Option (顶级命令)
        self._PENDING_OPTIONS: List[Dict[str, Any]] = []
        # 顶级 CLI Group - 在第一个 @init wrapper 中初始化
        self._CLI_GROUP: Optional[click.Group] = None
        # 存储 capability name 到其初始化函数的映射
        self._CAPABILITY_INIT_FUNCS: Dict[str, Callable] = {}
        # 标记是否已显式定义了 capability
        self._EXPLICIT_CAPABILITY_DEFINED: bool = False
        # 标记是否已经注册了退出处理函数
        self._EXIT_HANDLER_REGISTERED: bool = False
        # 特殊命令列表
        self._SPECIAL_COMMANDS = ['register', 'start', 'stop', 'destroy' , 'server']

        self._OK_RETURNS = {
            'code': 0,
            'msg': 'OK',
        }

        self._initialized = True

    class CapabilityError(Exception):
        """Capability 模块自定义异常。"""
        pass

    def _get_default_capability_name(self):
        """获取默认的 capability 名称（基于文件名）。"""
        # 获取调用栈中的文件名
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            if filename != __file__:
                # 获取文件名（不含扩展名）作为 capability 名称
                return os.path.splitext(os.path.basename(filename))[0]
            frame = frame.f_back
        # 如果无法获取文件名，使用默认名称
        return "default_capability"

    def _ensure_default_capability(self):
        """确保至少有一个默认的 capability。"""
        if not self._CAPABILITIES and not self._EXPLICIT_CAPABILITY_DEFINED:
            # 创建默认的 capability
            name = self._get_default_capability_name()
            meta = {
                'name': name,
                'version': "1.0.0",
                'status': 1,
                'pages': [],
                'methods': [],
                'init_params': {},
                'language_type': "Python"
            }
            self._CAPABILITIES[name] = meta
            # 添加一个空的初始化函数
            self._CAPABILITY_INIT_FUNCS[name] = lambda x: None

    def _output_all_capability_meta(self, ctx: click.Context, param: click.Parameter, value: bool):
        """处理顶级 --capability 选项的回调：输出所有 capability 元数据。"""
        if not value or ctx.resilient_parsing:
            return
        self._ensure_default_capability()
        json_output = json.dumps(list(self._CAPABILITIES.values()), indent=2, ensure_ascii=False)
        click.echo(json_output)
        ctx.exit(0)

    def _run_cli_if_needed(self):
        """在程序退出前检查是否需要运行 CLI"""
        # 只有在有注册的命令但没有运行过 CLI 的情况下才运行
        if self._PENDING_OPTIONS and self._CLI_GROUP is None:
            self._CLI_GROUP = click.Group()
            self.register_pending_options()
            self.add_top_level_capability_option()
            self.add_init_command()
            self.add_special_commands()  # 添加特殊命令
            self._CLI_GROUP(standalone_mode=True, prog_name=os.path.basename(sys.argv[0]))

    def add_special_commands(self):
        """添加特殊命令（register, start, stop, destroy, server）"""
        assert self._CLI_GROUP is not None

        # 添加 register 命令
        if 'register' not in self._CLI_GROUP.commands:
            @click.command(name='register')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def register_command(ctx, parameters_str):
                """注册 capability 元数据"""
                try:
                    params_dict = {}
                    json_dict = {}
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)

                    params_dict['params'] = json_dict
                    params_dict['capability'] = list(self._CAPABILITIES.values())

                    result = params_dict['capability']
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'register': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(register_command)

        # 添加 start 命令
        if 'start' not in self._CLI_GROUP.commands:
            @click.command(name='start')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def start_command(ctx, parameters_str):
                """启动能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'start': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(start_command)

        # 添加 stop 命令
        if 'stop' not in self._CLI_GROUP.commands:
            @click.command(name='stop')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def stop_command(ctx, parameters_str):
                """停止能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'stop': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(stop_command)

        # 添加 destroy 命令
        if 'destroy' not in self._CLI_GROUP.commands:
            @click.command(name='destroy')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def destroy_command(ctx, parameters_str):
                """销毁能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'destroy': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(destroy_command)


        # 添加 server 命令
        if 'server' not in self._CLI_GROUP.commands:
            @click.command(name='server')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def server_command(ctx, parameters_str):
                """启动服务器"""
                from flask import Flask, jsonify, render_template, request
                try:
                    try:
                        from flask import Flask, jsonify, render_template, request
                    except ImportError:
                        click.echo("Flask is not installed. Please install it to use the server feature.")
                        click.echo("You can install it with: pip install flask")
                        ctx.exit(1)

                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        server_params = json.loads(json_str)
                    else:
                        server_params = {}


                    # 获取服务器配置参数
                    host = server_params.get('host', '0.0.0.0')
                    port = server_params.get('port', 5000)
                    templates = server_params.get('templates', "assets/pages")
                    static = server_params.get('static', "assets/static")

                    # 创建Flask应用
                    app = Flask(__name__,
                                static_folder=static,
                                template_folder=templates)

                    # 查找自定义的页面和方法处理器
                    custom_pages_handler = None
                    custom_methods_handler = None

                    # 在所有能力中查找自定义处理器
                    for capability in self._CAPABILITIES.values():
                        methods = capability.get('methods', [])
                        for method in methods:
                            method_name = method.get('name', '')
                            if method_name == 'server_pages':
                                custom_pages_handler = method.get('func')
                            elif method_name == 'server_methods':
                                custom_methods_handler = method.get('func')

                    # 默认页面处理器 - 显示 register JSON
                    @app.route('/')
                    def index():
                        # 收集所有能力的元数据
                        capabilities_meta = list(self._CAPABILITIES.values())
                        return jsonify(capabilities_meta)

                    # 页面路由处理器
                    @app.route('/pages')
                    def pages():
                        # 获取url参数
                        page_url = request.args.get('url')

                        # 如果没有指定页面，默认显示index页面
                        if not page_url or page_url == 'index':
                            # 显示register JSON
                            capabilities_meta = list(self._CAPABILITIES.values())
                            return jsonify(capabilities_meta)

                        # 如果有自定义页面处理器，使用它
                        if custom_pages_handler:
                            params = {
                                'url': page_url,
                                'url_params': request.args.to_dict(),
                                'capabilities': list(self._CAPABILITIES.keys())
                            }
                            params['url_params'].pop('url', None)  # 移除url参数本身
                            return custom_pages_handler(params)

                        # 否则使用默认处理逻辑
                        try:
                            # 尝试渲染指定的模板
                            return render_template(page_url)
                        except:
                            # 如果模板不存在，尝试添加.html后缀
                            try:
                                return render_template(page_url + ".html")
                            except:
                                # 如果还是找不到，返回错误信息
                                return jsonify({
                                    "error": f"Page '{page_url}' not found",
                                    "available_pages": self._get_available_pages()
                                }), 404

                    # 辅助方法：获取所有可用页面
                    def _get_available_pages():
                        pages_list = []
                        for capability in self._CAPABILITIES.values():
                            capability_name = capability['name']
                            pages = capability.get('pages', [])
                            for page in pages:
                                page_path = page.get('path', '')
                                pages_list.append({
                                    'capability': capability_name,
                                    'path': page_path,
                                    'description': page.get('description', '')
                                })
                        return pages_list

                    # 添加方法路由处理器
                    if custom_methods_handler:
                        # 如果有自定义方法处理器，使用它处理所有方法调用
                        @app.route('/methods', methods=['GET', 'POST'])
                        def custom_methods_endpoint():
                            # 收集所有参数
                            params = request.args.to_dict()
                            if request.method == 'POST':
                                try:
                                    json_data = request.get_json()
                                    if json_data:
                                        params.update(json_data)
                                except:
                                    pass

                            # 添加方法调用信息
                            params['endpoint'] = 'methods'
                            params['capability_list'] = list(self._CAPABILITIES.keys())

                            # 调用自定义处理器
                            return custom_methods_handler(params)
                    else:
                        # 否则使用默认方法处理器
                        @app.route('/methods', methods=['GET', 'POST'])
                        def default_methods_endpoint():
                            method_name = request.args.get('m') or request.args.get('method')      # 获取方法名称
                            capability_name = request.args.get('c') or request.args.get('capability')    # 获取能力名称

                            if not method_name:
                                return jsonify({"error": "Method name (n) is required"}), 400

                            # 查找对应的能力和方法
                            target_capability = None
                            target_method = None

                            if capability_name:
                                # 如果指定了能力名称
                                target_capability = self._CAPABILITIES.get(capability_name)
                            else:
                                # 如果没有指定能力名称，遍历所有能力
                                for cap in self._CAPABILITIES.values():
                                    for method in cap.get('methods', []):
                                        if method.get('name') == method_name:
                                            target_capability = cap
                                            target_method = method
                                            break
                                    if target_capability:
                                        break

                            # 如果没有指定能力名称，查找对应的方法
                            if not target_capability and not capability_name:
                                for cap in self._CAPABILITIES.values():
                                    for method in cap.get('methods', []):
                                        if method.get('name') == method_name:
                                            target_capability = cap
                                            target_method = method
                                            break
                                    if target_capability:
                                        break

                            if not target_capability:
                                return jsonify({"error": f"Capability not found"}), 404

                            if not target_method:
                                # 在目标能力中查找方法
                                for method in target_capability.get('methods', []):
                                    if method.get('name') == method_name:
                                        target_method = method
                                        break

                            if not target_method:
                                return jsonify({"error": f"Method '{method_name}' not found"}), 404

                            # 执行方法
                            try:
                                method_func = target_method.get('func')
                                params = request.args.to_dict()
                                # 移除 'c' 和 'n' 参数
                                # params.pop('c', None)
                                # params.pop('capability', None)
                                # params.pop('m', None)
                                # params.pop('method', None)
                                # 处理 入参
                                parameters_str = request.args.get('p') or request.args.get('params')      # 获取方法名称

                                if parameters_str.strip():
                                    # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                                    json_str = base64.b64decode(parameters_str).decode('utf-8')
                                    params = json.loads(json_str)
                                else:
                                    params = {}
                                # 处理POST数据
                                if request.method == 'POST':
                                    try:
                                        json_data = request.get_json()
                                        if json_data:
                                            params.update(json_data)
                                    except:
                                        pass

                                # 检查函数签名以决定如何调用
                                import inspect
                                sig = inspect.signature(method_func)
                                func_params = list(sig.parameters.keys())

                                if params and len(func_params) > 0:
                                    result = method_func(params)
                                elif len(func_params) == 0:
                                    result = method_func()
                                else:
                                    result = method_func({})

                                return jsonify(result) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                return jsonify({"error": f"Error executing method: {str(e)}"}), 500
                    click.echo(f"server调试模式: ")
                    click.echo(f"Starting Flask server for capabilities: {list(self._CAPABILITIES.keys())}")
                    click.echo(f"Host: {host}, Port: {port}")
                    app.run(host=host, port=port, debug=False)

                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'server': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(server_command)


    def register_pending_options(self):
        """注册所有暂存的 Option 作为顶级命令。"""
        # 确保 _CLI_GROUP 已经存在
        if self._CLI_GROUP is None:
            self._CLI_GROUP = click.Group()

        self._ensure_default_capability()

        for option_meta in self._PENDING_OPTIONS:
            cmd_name = option_meta['name']
            # 使用 alias 作为命令名，如果提供了 alias，否则使用 name
            command_name = option_meta.get('alias') or cmd_name
            description = option_meta['description']
            params = option_meta['params']
            func = option_meta['func']
            capability_name = option_meta['capability_name']
            # 获取 option_meta 中的 returns (如果存在)
            returns = option_meta.get('returns', {})

            # 创建顶级命令
            @click.command(name=command_name, help=description)
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def command_wrapper(ctx, parameters_str, func=func, params=params, returns=returns, cmd_name=command_name):
                try:
                    params_dict = {}
                    json_dict = {}
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)

                    # 对于 register 和 destroy 命令特殊处理，始终添加 capability 数据
                    if cmd_name in self._SPECIAL_COMMANDS:
                        params_dict['params'] = json_dict
                        params_dict['capability'] = list(self._CAPABILITIES.values())
                    else:
                        params_dict = json_dict
                    sig = inspect.signature(func)
                    func_params = list(sig.parameters.keys())

                    # 捕获函数的打印输出
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    try:
                        if len(func_params) == 0:
                            result = func()
                        else:
                            result = func(params_dict)
                    finally:
                        # 恢复标准输出
                        sys.stdout = old_stdout

                    # 获取捕获的输出
                    output = captured_output.getvalue()

                    # 特殊处理 register 和 destroy 方法
                    if cmd_name == 'register':
                        if result is None:
                            result = params_dict['capability']
                        click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    elif cmd_name in [ 'start' , 'stop' , 'destroy' ] :
                        if result is None:
                            result = self._OK_RETURNS
                        click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    else:
                        # 先输出函数的打印内容（如果有的话）
                        if output.strip():
                            # 如果有打印输出，就输出打印内容
                            click.echo(output.strip())

                        # 其它 命令的标准处理
                        if result is not None:
                            if isinstance(result, dict):
                                click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                            else:
                                click.echo(result)
                        else:
                            # 如果没有返回值且没有打印输出，输出默认值
                            # if not output.strip():
                            click.echo(json.dumps(self._OK_RETURNS, ensure_ascii=False, indent=4))

                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing '{cmd_name}': {e}", err=True)
                    ctx.exit(1)

            # 将命令添加到顶级 Group
            self._CLI_GROUP.add_command(command_wrapper)

            # --- 更新 capability 的 methods 列表中的 name ---
            # 确保我们使用正确的 capability_name
            actual_capability_name = capability_name
            if actual_capability_name is None and self._CAPABILITIES:
                # 如果没有显式指定 capability_name，则使用默认的 capability
                actual_capability_name = next(iter(self._CAPABILITIES))

            cap_methods = self._CAPABILITIES[actual_capability_name]['methods']
            for method in cap_methods:
                if (method['description'] == description and
                    method.get('params', {}) == params and
                    method.get('returns', {}) == returns):
                    method['name'] = command_name
                    if 'alias' in option_meta:
                        method['alias'] = option_meta['alias']
                    break

    def add_top_level_capability_option(self):
        """为顶级 CLI Group 添加 --capability 选项。"""
        assert self._CLI_GROUP is not None
        # 检查是否已添加，避免重复
        if not any(isinstance(p, click.Option) and '--capability' in p.opts for p in self._CLI_GROUP.params):
            self._CLI_GROUP.params.append(
                click.Option(
                    ['--capability'],
                    is_flag=True,
                    is_eager=True,
                    expose_value=False,
                    help='Output metadata for all capabilities (JSON) and exit.',
                    callback=self._output_all_capability_meta
                )
            )

    def add_init_command(self):
        """添加顶级 init 命令，用于执行所有 capability 的初始化逻辑。"""
        assert self._CLI_GROUP is not None

        if 'init' not in self._CLI_GROUP.commands:
            @click.command(name='init')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters for the init command. (Optional)')
            @click.option('--capability', is_flag=True, is_eager=True, expose_value=False,
                          help='Output metadata for all capabilities (JSON) and exit.',
                          callback=self._output_all_capability_meta)
            @click.pass_context
            def init_command(ctx, parameters_str):
                """执行所有 capability 的初始化逻辑。"""
                init_params = {}
                if parameters_str.strip():
                    try:
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        init_params = json.loads(json_str)
                    except (base64.binascii.Error, UnicodeDecodeError) as e:
                        click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                        ctx.exit(1)
                    except json.JSONDecodeError as e:
                        click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                        ctx.exit(1)

                self._ensure_default_capability()

                if not self._CAPABILITY_INIT_FUNCS:
                    click.echo("No capabilities to initialize.")
                    return self._OK_RETURNS

                for cap_name, init_func in self._CAPABILITY_INIT_FUNCS.items():
                    try:
                        click.echo(f"Initializing capability: {cap_name}")
                        result = init_func(init_params)
                        # 如果初始化函数没有返回值，则输出默认值
                        if result is None:
                            click.echo(json.dumps(self._OK_RETURNS, ensure_ascii=False, indent=4))
                        else:
                            click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    except Exception as e:
                        click.echo(f"Error initializing capability '{cap_name}': {e}", err=True)

            self._CLI_GROUP.add_command(init_command)


    # --- 装饰器定义 ---
    def init(self, name: str = None,
             version: str = "1.0.0",
             status: int = 1,
             pages: List[Dict[str, str]] = None,
             init_params: Optional[Dict[str, Dict[str, str]]] = None,
             language_type: str = "Python") -> Callable[[Callable], Callable]: # 添加 language_type 参数
        """
        装饰器：初始化一个 capability 的元数据
        name (可选): 能力名称，默认为文件名
        version (可选): 版本
        status (可选): 状态默认块状态，默认为 1
        pages (可选): 描述能力文档的页面列表，支持多种格式：
                    1. 字符串列表: ["/page1", "/page2"]
                    2. 字典列表: [{"url": "/page1", "description": "页面1"}, ...]
        `init_params` (可选): 描述初始化函数可能接收的参数元数据
        `language_type` (可选): 描述能力实现使用的编程语言，默认为 "Python"
        """
        self._EXPLICIT_CAPABILITY_DEFINED = True

        pages = pages or []
        init_params = init_params or {} # 如果没提供 init_params，用空字典

        def decorator(func: Callable) -> Callable:
            # 如果没有提供 name，则使用文件名
            capability_name = name if name else self._get_default_capability_name()

            if capability_name in self._CAPABILITIES:
                raise self.CapabilityError(f"Capability '{capability_name}' is already defined.")

            # 处理 pages 参数，统一转换为标准格式
            processed_pages = []
            if pages:
                # 获取调用函数的文件名和行号
                frame = inspect.currentframe()
                try:
                    caller_frame = frame.f_back
                    filename = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                    # 获取文件名（不含路径）和行号
                    basename = os.path.basename(filename)
                finally:
                    del frame

                # 处理 pages 参数，支持两种格式
                for page in pages:
                    if isinstance(page, str):
                        # 格式1: 字符串列表
                        page_info = {
                            'path': page,
                            'description': "",  # 没有描述则为空字符串
                            'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                        }
                        processed_pages.append(page_info)
                    elif isinstance(page, dict):
                        # 格式2: 字典列表
                        url = page.get('url', '')
                        if url:
                            page_info = {
                                'path': url,
                                'description': page.get('description', ""),  # 没有描述则为空字符串
                                'handler': page.get('handler'),  # 如果有处理函数也一并保存
                                'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                            }
                            processed_pages.append(page_info)

            meta = {
                'name': capability_name,
                'version': version,
                'status': status,
                'pages': processed_pages,
                'methods': [],
                'init_params': init_params,
                'language_type': language_type
            }
            self._CAPABILITIES[capability_name] = meta
            self._CAPABILITY_INIT_FUNCS[capability_name] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                if self._CLI_GROUP is None:
                    self._CLI_GROUP = click.Group()

                self.register_pending_options()
                self.add_top_level_capability_option()
                self.add_init_command()
                self.add_special_commands()  # 添加特殊命令
                self._CLI_GROUP(standalone_mode=True, prog_name="capability_test")


            return wrapper

        return decorator


    def option(self, name: Optional[str] = None, description: str = "",
               params: Dict[str, Dict[str, str]] = None,
               returns: Dict[str, Dict[str, str]] = None,
               capability_name: Optional[str] = None,
               alias: Optional[str] = None,
               pages: Optional[List] = None) -> Callable[[Callable], Callable]:
        """
        装饰器：注册一个顶级 CLI 命令。
        name (可选): 命令的名称。如果未提供，则使用被装饰函数的名称 (func.__name__)。
        `capability_name (可选)` 指定该命令属于哪个 capability (通过 @init 定义的 name)。
                    如果不指定，则尝试关联到最近定义的 capability。
        `params (可选)` 是 `parameters` 的简化别名。
        alias (可选): 为该命令指定一个别名作为 CLI 命令名。如果未提供，则使用 name（或函数名）。
        pages (可选): 页面列表，支持两种格式：
                    1. 字符串列表: ["/page1", "/page2"]
                    2. 字典列表: [{"url": "/page1", "description": "页面1"}, ...]
        """
        # 注册退出处理函数，确保在没有 @init 装饰器的情况下也能运行 CLI
        if not self._EXIT_HANDLER_REGISTERED:
            atexit.register(self._run_cli_if_needed)
            self._EXIT_HANDLER_REGISTERED = True

        params = params or {}
        returns = returns or {}
        pages = pages or []

        def decorator(func: Callable) -> Callable:
            cap_name = capability_name
            if cap_name is None and self._CAPABILITIES:
                # 如果没有显式指定 capability_name，但已存在定义的 capability，则使用第一个
                cap_name = next(iter(self._CAPABILITIES))
            elif cap_name is None and not self._CAPABILITIES:
                # 如果没有定义任何 capability，则创建一个默认的
                self._ensure_default_capability()
                cap_name = next(iter(self._CAPABILITIES))

            if cap_name not in self._CAPABILITIES:
                raise self.CapabilityError(f"Cannot assign option to capability '{cap_name}': capability not defined.")

            final_name = name
            if not final_name:
                final_name = func.__name__
            if not final_name:
                raise self.CapabilityError(f"Cannot determine name for option from function '{func.__name__}'. Function name is empty.")

            option_meta = {
                'name': final_name,
                'description': description,
                'params': params,
                'returns': returns,
                'func': func,
                'capability_name': cap_name
            }
            if alias is not None:
                option_meta['alias'] = alias

            self._PENDING_OPTIONS.append(option_meta)

            method_entry = {
                'name': final_name,
                'description': description,
                'params': params,
                'returns': returns,
                'func': func
            }

            if alias is not None:
                method_entry['alias'] = alias

            self._CAPABILITIES[cap_name]['methods'].append(method_entry)

            # 处理 pages 参数并添加到 capability 的 pages 列表中
            if pages:
                capability_pages = self._CAPABILITIES[cap_name]['pages']
                # 获取调用函数的文件名和行号
                frame = inspect.currentframe()
                try:
                    caller_frame = frame.f_back
                    filename = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                    # 获取文件名（不含路径）和行号
                    basename = os.path.basename(filename)
                finally:
                    del frame

                # 处理 pages 参数，支持两种格式
                for page in pages:
                    if isinstance(page, str):
                        # 格式1: 字符串列表
                        page_info = {
                            'path': page,
                            'description': f"Page {page}",
                            'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                        }
                        capability_pages.append(page_info)
                    elif isinstance(page, dict):
                        # 格式2: 字典列表
                        url = page.get('url', '')
                        if url:
                            page_info = {
                                'path': url,
                                'description': page.get('description', f"Page {url}"),
                                'handler': page.get('handler'),  # 如果有处理函数也一并保存
                                'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                            }
                            capability_pages.append(page_info)

            return func

        return decorator

# 创建全局实例
capability = CapabilityDecorator()

# 为了向后兼容，创建装饰器函数
init = capability.init
option = capability.option
CapabilityError = CapabilityDecorator.CapabilityError