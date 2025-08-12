import os
import shutil


def create_save_dir(config) -> str:
    init_saver = False
    if config.experiment.save_path is None:
        save_path = './{}'.format(config.experiment.name)
        init_saver = True
    else:
        save_path = config.experiment.save_path
    if os.path.exists(save_path):
        return save_path
    else:
        if init_saver:
            choice = input(
                "Detect you have already have project named `{}`, do you want to delete and rebuild it? (y/n)".format(save_path))
            choice = choice.lower()
            if choice not in ['y', 'n']:
                print("Input error, please try again.")
            else:
                if choice == 'y':
                    shutil.rmtree(save_path)
                    os.mkdir(save_path)
                return save_path
