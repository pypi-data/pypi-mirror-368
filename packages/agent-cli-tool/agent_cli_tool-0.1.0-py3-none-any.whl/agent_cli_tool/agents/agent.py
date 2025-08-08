import sys
from io import StringIO
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ai import BaseAI


class Agent:
    def __init__(
        self,
        cli_args,
        model: str,
        env_config: Dict[str, str],
        output_io: StringIO,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        before_ai_ask_hook: Optional[Callable] = None,
        after_ai_ask_hook: Optional[Callable] = None,
    ) -> None:
        """
        初始化Agent类。

        :param cli_args: 命令行参数
        :param model: 使用的AI模型名称
        :param env_config: 环境配置字典，包含API_KEY、BASE_URL等
        :param output_io: 用于输出的StringIO对象
        :param tools: 可选，传递给AI的工具
        :param system_prompt: 可选，系统提示信息
        :param messages: 可选，初始消息列表
        :param before_ai_ask_hook: 可选，在向AI提问前执行的钩子函数
        :param after_ai_ask_hook: 可选，在AI回答后执行的钩子函数
        """
        self.cli_args = cli_args
        self.output_io = output_io
        self.before_ai_ask_hook = before_ai_ask_hook
        self.after_ask_ai_hook = after_ai_ask_hook

        # 根据命令行参数和环境配置确定运行模式
        self.mode = self._determine_mode(cli_args, env_config, system_prompt)

        # 初始化AI对象
        self.ai = self._initialize_ai(model, env_config, tools, messages)

        # 获取用户和AI的emoji表示
        self.user_emoji = env_config.get("USER_EMOJI", "💬:")
        self.ai_emoji = env_config.get("AI_EMOJI", "🤖:")
        self.think_start_emoji = env_config.get(
            "THINK_START_EMOJI", "🤔 <Start Thinking>"
        )
        self.think_end_emoji = env_config.get("THINK_END_EMOJI", "💡 <End Thinking>")

        # 如果命令行参数中启用了rich，初始化rich控制台
        if self.cli_args.rich:
            self._initialize_rich_console()

        # 如果命令行参数中指定了输出文件，打开文件
        if self.cli_args.output:
            self.output_file = open(cli_args.output, "w", encoding="utf-8")

    def _determine_mode(
        self,
        cli_args,
        env_config: Dict[str, str],
        system_prompt: Optional[str],
    ) -> Tuple[str, str]:
        """
        根据命令行参数和环境配置确定运行模式。

        :param cli_args: 命令行参数
        :param env_config: 环境配置字典
        :param system_prompt: 可选，系统提示信息
        :return: 运行模式字符串，如"shell"、"code"或"default"
        """
        if cli_args.shell and cli_args.code:
            raise RuntimeError(
                "Only one of `shell mode` or `code mode` can be active at a time."
            )

        if cli_args.shell:
            from os import getenv as os_getenv
            from platform import system as os_name

            # 如果命令行参数中启用了shell模式，设置系统提示为SHELL_PROMPT
            prompt = env_config.get("SHELL_PROMPT").format_map(
                {"os": os_name(), "shell": os_getenv("SHELL")}
            )
            mode = "shell"
            cli_args.ignore_user = cli_args.ignore_ai = True
        elif cli_args.code:
            # 如果命令行参数中启用了code模式，设置系统提示为CODE_PROMPT
            prompt = env_config.get("CODE_PROMPT")
            mode = "code"
            cli_args.ignore_user = cli_args.ignore_ai = True
        else:
            # 否则使用默认提示
            prompt = env_config.get("DEFAULT_PROMPT")
            mode = "default"

        self.system_prompt = prompt if system_prompt is None else system_prompt
        return mode

    def _initialize_ai(
        self,
        model: str,
        env_config: Dict[str, str],
        tools: Optional[List[Dict[str, Any]]],
        messages: Optional[List[Dict[str, str]]],
    ):
        """
        初始化AI对象。

        :param model: 使用的AI模型名称
        :param env_config: 环境配置字典
        :param tools: 传递给AI的工具
        :param messages: 初始消息列表
        :return: 初始化的BaseAI对象
        """
        api_key = env_config.get("API_KEY")
        base_url = env_config.get("BASE_URL")
        timeout = int(env_config.get("TIMEOUT"))
        stream = env_config.get("STREAM", "true").lower() == "true"
        return BaseAI(
            api_key,
            base_url,
            model,
            timeout,
            stream,
            tools,
            self.system_prompt,
            messages,
        )

    def _initialize_rich_console(self):
        """
        初始化rich控制台，用于美化输出。
        """
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.rule import Rule

        self.rich_markdown = Markdown
        self.rich_console = Console()
        self.rich_line = Rule(
            "Rich Markdown",
            style="bold green",
            align="center",
            characters="=",
        )

    def before_ask_ai(self, user_input: str) -> str:
        """
        在向AI提问前执行的操作。

        :param user_input: 用户输入
        :return: 处理后的用户输入
        """
        if not self.cli_args.ignore_ai:
            self.output_io.write(f"\033[32m({self.ai.model})\033[0m {self.ai_emoji}\n")

        # 如果定义了before_ai_ask_hook，执行钩子函数
        if self.before_ai_ask_hook:
            return self.before_ai_ask_hook(user_input, self.mode)

        return user_input

    def after_ask_ai(self, ai_reply: str) -> str:
        """
        在AI回答后执行的操作。

        :param ai_reply: AI的回答
        :return: 处理后的AI回答
        """
        # 如果启用了rich，使用rich控制台输出AI回答
        if self.cli_args.rich:
            reply = ai_reply.strip()
            if self.mode != "default":
                if not reply.startswith("```") and not reply.endswith("```"):
                    reply = f"```\n{reply}\n```"

            self.rich_console.print("", self.rich_line, "", self.rich_markdown(reply))

        # 如果指定了输出文件，将AI回答写入文件
        if self.cli_args.output:
            self.output_file.write(f"{ai_reply}\n")

        # 如果定义了after_ask_ai_hook，执行钩子函数
        if self.after_ask_ai_hook:
            return self.after_ask_ai_hook(ai_reply, self.mode)

        return ai_reply

    def ask_ai(self, user_input: str) -> str:
        """
        向AI提问并获取回答。

        :param user_input: 用户输入
        :return: AI的回答
        """
        # 将处理后的用户输入添加到消息列表中
        self.ai.messages.append(self.ai.user_message(self.before_ask_ai(user_input)))
        # 发送消息并获取响应
        response = self.ai.send_messages()
        if isinstance(response, str):
            # 输出错误信息
            self.output_io.write(f"{response}\n")
            return response

        ai_reply = ""
        has_thinking = False
        # 处理流式响应，逐块获取AI回答
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                if has_thinking:
                    has_thinking = False
                    self.output_io.write(
                        f"\033[0m\n\033[1;36m{self.think_end_emoji}\033[0m\n"
                    )

                content = delta.content
                self.output_io.write(content)
                ai_reply += content
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if self.cli_args.ignore_think:
                    continue

                if not has_thinking:
                    has_thinking = True
                    self.output_io.write(
                        f"\033[1;36m{self.think_start_emoji}\033[0m\n\033[3m"
                    )
                self.output_io.write(delta.reasoning_content)

            self.output_io.flush()

        # 将AI回答添加到消息列表中
        self.ai.messages.append(self.ai.ai_message(ai_reply))

        self.output_io.write("\n")

        ai_reply = self.after_ask_ai(ai_reply)

        if self.cli_args.conversation:
            self.output_io.write("\n")

        return ai_reply

    def get_user_input(self, need_user_input: bool = True) -> str:
        """
        获取用户输入。

        :param need_user_input: 是否需要用户输入
        :return: 用户输入
        """
        try:
            if need_user_input:
                if not self.cli_args.ignore_user:
                    status = "Use ^D to send" if sys.stdin.isatty() else "Pipe-Prompt"
                    self.output_io.write(
                        f"\033[94m({status})\033[0m {self.user_emoji}\n"
                    )
                    self.output_io.flush()

                user_input = sys.stdin.read().strip()
                if not sys.stdin.isatty():
                    self.output_io.write(f"{user_input}")
                self.output_io.write("\n")
                self.output_io.flush()

                return user_input

            return sys.stdin.read().strip() if not sys.stdin.isatty() else ""
        except KeyboardInterrupt:
            return ""

    def run(self) -> None:
        """
        运行Agent，处理用户输入和AI交互。
        """
        if self.cli_args.prompt:
            args_prompt = self.cli_args.prompt
            pipe_prompt = self.get_user_input(need_user_input=False)
            show_pipe = bool(pipe_prompt)
            prompt_show = "(Arg Prompt)"
            if self.cli_args.ahead:
                prompt = args_prompt + pipe_prompt
                prompt_show = "(Arg+Pipe Prompt)" if show_pipe else prompt_show
            else:
                prompt = pipe_prompt + args_prompt
                prompt_show = "(Pipe+Arg Prompt)" if show_pipe else prompt_show

            prompt = prompt.strip()
            if not self.cli_args.ignore_user:
                self.output_io.write(
                    f"\033[94m{prompt_show}\033[0m {self.user_emoji}\n"
                )
                self.output_io.write(f"{prompt}\n\n")

            self.ask_ai(prompt)

        if self.cli_args.conversation or not self.cli_args.prompt:
            while user_input := self.get_user_input():
                self.output_io.write("\n")
                self.ask_ai(user_input)
                if not self.cli_args.conversation:
                    break

    def __del__(self):
        """
        在Agent退出时执行的操作，如关闭输出文件。
        """
        if self.cli_args.output and not self.output_file.closed:
            self.output_file.close()
