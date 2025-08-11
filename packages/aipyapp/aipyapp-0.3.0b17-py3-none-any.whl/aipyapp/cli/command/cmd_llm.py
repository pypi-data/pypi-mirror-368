from ... import T
from .base import CommandMode, Completable
from .base_parser import ParserCommand
from .utils import print_records

class LLMCommand(ParserCommand):
    name = 'llm'
    description = T('LLM operations')
    modes = [CommandMode.MAIN, CommandMode.TASK]

    def add_subcommands(self, subparsers):
        use_parser = subparsers.add_parser('use', help=T('Use a LLM provider'))
        use_parser.add_argument('provider', type=str, help=T('Provider name'))
        subparsers.add_parser('list', help=T('List LLM providers'))

    def get_arg_values(self, arg, subcommand=None, partial_value=''):
        if subcommand == 'use' and arg.name == 'provider':
            ctx = self.manager.context
            return [Completable(client.name, str(client)) for client in ctx.tm.client_manager.clients.values()]
        return super().get_arg_values(arg, subcommand)
            
    def cmd_list(self, args, ctx):
        rows = ctx.tm.list_llms()
        print_records(rows)
        
    def cmd_use(self, args, ctx):
        if ctx.task:
            ret = ctx.task.use(args.provider)
        else:
            ret = ctx.tm.use(llm=args.provider)
        ctx.console.print(T('Success') if ret else T('Failed'), style='cyan' if ret else 'red')
        if ret:
            self.log.info(f'Use {args.provider} LLM provider')
        return ret

    def cmd(self, args, ctx):
        self.cmd_list(args, ctx)