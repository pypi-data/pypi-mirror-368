from ml_golem.main_loop_logic.main_loop_messages import MainLoopMessages
from ml_golem.main_loop_logic.argparsing import get_args_and_actions



def main_loop(
        app_title = 'Default App Title',
        system_config_path = 'conf/system_configs/system_conf.yaml',
        _add_additional_args = lambda x, y: (x, y)        
        ):
    print(MainLoopMessages.BEGINNING_PROGRAM.value)
    args, actions = get_args_and_actions(app_title,system_config_path,_add_additional_args)
    for action in actions:
        if action(args):
            print(MainLoopMessages.COMPLETE_PROGRAM.value)
            return
    raise Exception(f'No action specified.')
