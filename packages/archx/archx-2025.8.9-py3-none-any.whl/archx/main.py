import pyfiglet, argparse, time, os

from loguru import logger

from archx.architecture import create_architecture_dict, save_architecture_dict
from archx.event import create_event_graph, save_event_graph
from archx.metric import create_metric_dict, create_event_metrics, save_metric_dict
from archx.workload import create_workload_dict, save_workload_dict
from archx.performance import simulate_performance_all_events
from archx.utils import bcolors, write_yaml, read_yaml
from archx.interface import register_interface, unregister_interface, copy_interface


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='Archx is a framework to explore the design space of hardware architecture.')
    parser.add_argument('-r', '--run_dir', type=str, default=None,
                        help = 'Run directory to store outputs.')
    parser.add_argument('-a', '--architecture_yaml', type=str, default=None,
                        help = 'Path to architecture yaml.')
    parser.add_argument('-m', '--metric_yaml', type=str, default=None,
                        help = 'Path to metric yaml.')
    parser.add_argument('-w', '--workload_yaml', type=str, default=None,
                        help = 'Path to workload yaml.')
    parser.add_argument('-e', '--event_yaml', type=str, default=None,
                        help = 'Path to event yaml.')
    parser.add_argument('-c', '--checkpoint', type=str, default=None,
                        help = 'Path to checkpoint, which requires <.gt> format.')
    parser.add_argument('-l', '--log_level', type=str, default='INFO',
                        help = 'Level of logger.')
    parser.add_argument('-s', '--save_yaml', action='store_true', default=False, help = 'Save yaml files in run directory.')
    parser.add_argument('-ireg', '--register_interface', action='store_true', default=False, help = 'Register a new interface.')
    parser.add_argument('-iureg', '--unregister_interface', action='store_true', default=False, help = 'Unregister a new interface.')
    parser.add_argument('-icopy', '--copy_interface', action='store_true', default=False, help = 'Copy an existing interface.')
    parser.add_argument('-iname', '--interface_name', type=str, default=None, help = 'Name of the interface.')
    parser.add_argument('-idir', '--interface_dir', type=str, default=None, help = 'Directory of the interface.')

    return parser.parse_args()


def main():
    args = parse_commandline_args()
    
    # set up banner
    ascii_banner = pyfiglet.figlet_format('Archx')
    print(bcolors.Magenta + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('UnaryLab')
    print(bcolors.Yellow + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('https://github.com/UnaryLab/archx', font='term')
    print(bcolors.UNDERLINE + bcolors.Green + ascii_banner + bcolors.ENDC)

    # check not all interface options are selected
    assert (args.register_interface + args.unregister_interface + args.copy_interface <= 1), logger.error('Only one interface option can be selected at a time: <-regi>, <-uregi>, or <-copyi>.')
    
    # register interface
    if args.register_interface:
        assert args.interface_name is not None, logger.error(f'Interface name is required for registration via <-iname>.')
        assert args.interface_dir is not None, logger.error(f'Interface directory is required for registration via <-idir>.')
        register_interface(args.interface_name, args.interface_dir)
        exit(0)
    # unregister interface
    elif args.unregister_interface:
        assert args.interface_name is not None, logger.error(f'Interface name is required for unregistration via <-iname>.')
        unregister_interface(args.interface_name)
        exit(0)
    # copy interface
    elif args.copy_interface:
        assert args.interface_name is not None, logger.error(f'Interface name is required for copying via <-iname>.')
        assert args.interface_dir is not None, logger.error(f'Interface directory is required for copying via <-idir>.')
        copy_interface(args.interface_name, args.interface_dir)
        exit(0)


    # validate run dir exists and path is valid
    assert args.run_dir is not None, logger.error(f'Run directory is required via <-r> or <-run_dir>.')
    # check if run directory exists, if not create it
    if not os.path.isdir(args.run_dir):
        os.makedirs(args.run_dir)
        logger.info(f'Create run directory <{args.run_dir}>.')
    else:
        logger.info(f'Find run directory <{args.run_dir}>.')

    # set up output log
    logger.remove()
    output_log = args.run_dir + '/archx' + '-' + str(time.time()) + '.log'
    logger.add(output_log, level=args.log_level)

    # validate checkpoint
    assert args.checkpoint.endswith('.gt'), logger.error('Invalid event checkpoint format; requires <.gt>.')

    logger.success(f'\n----------------------------------------------\nStep 1: Create architectue dict\n----------------------------------------------')
    architecture_dict = create_architecture_dict(args.architecture_yaml)

    logger.success(f'\n----------------------------------------------\nStep 2: Create metric dict\n----------------------------------------------')
    metric_dict = create_metric_dict(args.metric_yaml)

    logger.success(f'\n----------------------------------------------\nStep 3: Creat workload dict\n----------------------------------------------')
    workload_dict = create_workload_dict(args.workload_yaml)
    
    logger.success(f'\n----------------------------------------------\nStep 4: Creat event graph\n----------------------------------------------')
    event_graph = create_event_graph(args.event_yaml)

    logger.success(f'\n----------------------------------------------\nStep 5: Create metrics for all events and modules\n----------------------------------------------')
    event_graph = create_event_metrics(event_graph, architecture_dict, metric_dict, run_dir=args.run_dir)
    
    logger.success(f'\n----------------------------------------------\nStep 6: Simulate performance\n----------------------------------------------')
    event_graph = simulate_performance_all_events(event_graph, architecture_dict, workload_dict)
    
    logger.success(f'\n----------------------------------------------\nStep 7: Save event graph and log\n----------------------------------------------')
    save_event_graph(event_graph=event_graph, save_path=args.checkpoint)

    if args.save_yaml:
        save_architecture_dict(architecture_dict=architecture_dict, save_path=args.run_dir + '/architecture.yaml')
        save_metric_dict(metric_dict=metric_dict, save_path=args.run_dir + '/metric.yaml')
        save_workload_dict(workload_dict=workload_dict, save_path=args.run_dir + '/workload.yaml')
        write_yaml(args.run_dir + '/event.yaml', read_yaml(args.event_yaml))
        logger.success(f'Save dictionaries to <{args.run_dir}>.')

    logger.success(f'Save log to <{output_log}>.')


if __name__ == '__main__':
    main()

