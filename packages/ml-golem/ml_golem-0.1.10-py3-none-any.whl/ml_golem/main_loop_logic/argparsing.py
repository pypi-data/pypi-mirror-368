import argparse
import random
from file_golem import FileGolem

from ml_golem.model_action import ModelAction
from ml_golem.data_transfers.overleaf_transfer import OverleafTransfer
from ml_golem.data_transfers.model_copier import ModelCopyOver, ModelCopyBack
from ml_golem.grid_search.tensorboard_logic import TensorBoardLogic
from ml_golem.grid_search.config_copier import ConfigCopier
from ml_golem.grid_search.grid_search_builder import GridJobBuilder, GridJobViewer,SequentialGridJobExecutor
from ml_golem.main_loop_logic.reserved_keywords import ReservedArgKeywords


def add_flag_argument(parser,action_list,object_type,flag_name,flag_abbreviation=None,help_text=None):
    if help_text is None:
        help_text = f'Use this flag to enable {flag_name}'

    if flag_abbreviation is None:
        parser.add_argument(f'--{flag_name}',action='store_true',help=help_text)
    else:
        parser.add_argument(f'--{flag_name}',f'-{flag_abbreviation}',action='store_true',help=help_text)

    action = lambda args: (object_type(args)() or True) if getattr(args, flag_name) else False
    action_list.append(action)
    return parser, action_list


def get_args_and_actions(app_title,system_config_path,_add_additional_args):
    action_list = []
    parser = argparse.ArgumentParser(description=app_title)

    parser.add_argument('--data_io',default = None, help='Data IO object to use')
    parser.add_argument('-d',f'--{ReservedArgKeywords.DEBUG.value}',action='store_true',help='Print debug statements')
    parser.add_argument('-st','--system_transfer',type=str, default=None, help='System that the data_io object is transfering into' )

    parser.add_argument('-s','--seed', type=int,default=random.randint(0, 2**32 - 1), help='Seed for random number')
    parser.add_argument('-c','--config_name', type=str, default=None, help='Path to relevant omega conf file')

    parser.add_argument('-cc','--copy_config', type=str, default=None, help='Copy a config file')
    action_list.append(lambda args: (ConfigCopier(args)() or True) if args.copy_config else False)


    parser.add_argument(f'-{ReservedArgKeywords.TRAIN_SHORT.value}', f'--{ReservedArgKeywords.TRAIN.value}', 
        action= 'store_true', help='Train the model')
    action_list.append(lambda args: (ModelAction(args).train(args) or True) if args.train else False)

    parser.add_argument(f'-{ReservedArgKeywords.INFER_SHORT.value}', f'--{ReservedArgKeywords.INFER.value}', action= 'store_true', help='Have the model make inferences')
    action_list.append(lambda args: (ModelAction(args).inference(args) or True) if args.infer else False)

    parser.add_argument('-w', '--wipe', action= 'store_true', help='Wipe the model and training logs')
    action_list.append(lambda args: (ModelAction(args).wipe() or True) if args.wipe else False)

    parser.add_argument('-g', '--grid_job', action= 'store_true', help='Run a grid job')
    action_list.append(lambda args: (GridJobBuilder(args)() or True) if args.grid_job else False)

    parser.add_argument('-vg','--view_grid_job', action='store_true', help='View the grid job')
    action_list.append(lambda args: (GridJobViewer(args)() or True) if args.view_grid_job else False)

    parser.add_argument(
        f'-{ReservedArgKeywords.SEQUENTIAL_GRID_JOB_SHORT.value}',
        f'--{ReservedArgKeywords.SEQUENTIAL_GRID_JOB.value}',
        nargs='+', 
        type=str,
        default=[], help='Run a sequence of grid jobs. Provide the paths to the config files as arguments.')
    action_list.append(lambda args: (SequentialGridJobExecutor(args)() or True) if len(args.sequential_grid_job) > 0 else False)

    parser.add_argument('-co', '--call_object', type=str, default=None, help='construct an object with args and call __call__')
    action_list.append(lambda args: (args.data_io.fetch_class(args.call_object)(args)() or True) if args.call_object else False)

    parser.add_argument('-co_args', '--call_object_args', type=str, default=None, help='Arguments to pass to the call_object')

    parser.add_argument('-fi', '--find_import', type=str, default=None, help='Find the import path for a given class')
    action_list.append(lambda args: (args.data_io.find_import(args.find_import) or True) if args.find_import else False)

    parser.add_argument('-ot', '--overleaf_transfer', action='store_true', help='Update git-linked Overleaf to contain the latest graphics')
    action_list.append(lambda args: (OverleafTransfer(args)() or True) if args.overleaf_transfer else False)

    parser.add_argument('-tb', '--tensorboard', action='store_true', help='run the tensorboard for a given config')
    action_list.append(lambda args: (TensorBoardLogic(args)() or True) if args.tensorboard else False)

    parser.add_argument('--copy_model_over', action='store_true', help='Copy the model checkpoints to a mounted system')
    action_list.append(lambda args: (ModelCopyOver(args)() or True) if args.copy_model_over else False)

    parser.add_argument('--copy_model_back', action='store_true', help='Copy the model checkpoints to a mounted system')
    action_list.append(lambda args: (ModelCopyBack(args)() or True) if args.copy_model_back else False)


    if _add_additional_args is not None:
        parser, action_list = _add_additional_args(parser,action_list)

    args = parser.parse_args()
    #if args.call_object_args is not None:
    co_args_string = [] if args.call_object_args is None else args.call_object_args.split(',')
    args.call_object_args = {}
    for arg in co_args_string:
        if '=' in arg:
            key, value = arg.split('=', 1)
            args.call_object_args[key.strip()] = value.strip()
        else:
            args.call_object_args[arg.strip()] = None

    if 'help' in args:
        parser.print_help()

    if 'local_config_name' in args:
        raise Exception(f'local_config_name is a reserved keyword in args, it is set as {args.local_config_name} but should be empty')
    
    if 'origin_config_name' in args:
        raise Exception(f'origin_config_name is a reserved keyword in args, it is set as {args.origin_config_name} but should be empty')

    if 'object_ancestry' in args:
        raise Exception(f'object_ancestry is a reserved keyword in args, it is set as {args.object_ancestry} but should be empty')

    if (ReservedArgKeywords.INFER.value) in (args and ReservedArgKeywords.TRAIN.value) in args:
        raise Exception(f'You cannot use both {ReservedArgKeywords.INFER.value} and {ReservedArgKeywords.TRAIN.value} at the same time. Please choose one.')

    if sum([args.train, args.infer, args.wipe]) > 1:
        raise Exception("You can only use one of --train, --infer, or --wipe at a time.")

    args.data_io =FileGolem(
        system_config_path=system_config_path,
        is_debug=args.debug,
        system_transfer = args.system_transfer
    )

    return args, action_list
