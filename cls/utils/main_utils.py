import os
import torch
import argparse
import functools
import logging
from timm.scheduler.cosine_lr import CosineLRScheduler
from timm.scheduler.step_lr import StepLRScheduler
from configs import get_config
import wandb


def build_scheduler(config, optimizer, n_iter_per_epoch):
    num_steps = int(config.TRAIN.EPOCHS * n_iter_per_epoch)
    warmup_steps = int(config.TRAIN.WARMUP_EPOCHS * n_iter_per_epoch)
    decay_steps = int(config.TRAIN.LR_SCHEDULER.DECAY_EPOCHS * n_iter_per_epoch)

    lr_scheduler = None
    if config.TRAIN.LR_SCHEDULER.NAME == "cosine":
        lr_scheduler = CosineLRScheduler(
            optimizer,
            t_initial=num_steps,
            lr_min=config.TRAIN.MIN_LR,
            warmup_lr_init=config.TRAIN.WARMUP_LR,
            warmup_t=warmup_steps,
            cycle_limit=1,
            t_in_epochs=False,
        )
    elif config.TRAIN.LR_SCHEDULER.NAME == "step":
        lr_scheduler = StepLRScheduler(
            optimizer,
            decay_t=decay_steps,
            decay_rate=config.TRAIN.LR_SCHEDULER.DECAY_RATE,
            warmup_lr_init=config.TRAIN.WARMUP_LR,
            warmup_t=warmup_steps,
            t_in_epochs=False,
        )

    return lr_scheduler


def parse_option():
    parser = argparse.ArgumentParser("ViT training and evaluation script", add_help=False)
    parser.add_argument(
        "--cfg",
        type=str,
        required=True,
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options by adding 'KEY VALUE' pairs. ",
        default=None,
        nargs="+",
    )

    # easy config modification
    parser.add_argument("--batch-size", type=int, help="batch size for single GPU")
    parser.add_argument("--data-path", type=str, help="path to dataset")

    parser.add_argument("--resume", help="resume from checkpoint")
    parser.add_argument(
        "--use-checkpoint",
        action="store_true",
        help="whether to use gradient checkpointing to save memory",
    )
    parser.add_argument(
        "--output",
        default="output",
        type=str,
        metavar="PATH",
        help="root of output folder, the full path is <output>/<model_name>/<tag> (default: output)",
    )
    parser.add_argument("--tag", help="tag of experiment")
    parser.add_argument("--eval", action="store_true", help="Perform evaluation only")
    parser.add_argument("--lr", type=float, default=0.0005)

    # distributed training
    # parser.add_argument(
    #     "--local-rank", type=int, help="local rank for DistributedDataParallel"
    # )

    args, unparsed = parser.parse_known_args()
    config = get_config(args)
    return args, config


def save_checkpoint(
    config,
    epoch,
    model,
    max_accuracy,
    optimizer,
    optimizer_lif,
    lr_scheduler,
    lr_scheduler_lif,
    logger,
):
    save_state = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "optimizer_lif": optimizer_lif.state_dict() if optimizer_lif != None else None,
        "lr_scheduler": lr_scheduler.state_dict(),
        "lr_scheduler_lif": lr_scheduler_lif.state_dict() if lr_scheduler_lif != None else None,
        "max_accuracy": max_accuracy,
        "epoch": epoch,
        "config": config,
    }

    save_path = os.path.join(config.OUTPUT, f"ckpt_epoch.pth")
    logger.info(f"{save_path} saving......")
    torch.save(save_state, save_path)
    logger.info(f"{save_path} saved !!!")


def set_logger(config):
    # 日志设置
    os.makedirs(config.OUTPUT, exist_ok=True)
    logger = create_logger(output_dir=config.OUTPUT, name=f"{config.MODEL.NAME}")
    path = os.path.join(config.OUTPUT, "config.json")
    with open(path, "w") as f:
        f.write(config.dump())
    logger.info(f"Full config saved to {path}")

    # print config
    logger.info(config.dump())
    return logger


@functools.lru_cache()
def create_logger(output_dir, name=""):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # create formatter
    fmt = "[%(asctime)s %(name)s] (%(filename)s %(lineno)d): %(levelname)s %(message)s"

    # create file handlers
    file_handler = logging.FileHandler(os.path.join(output_dir, f"log.txt"), mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(file_handler)

    return logger


def wandb_init(config, device):
    wandb.init(
        project="Strawberry",
        config=config,
        entity="snn-training",
        job_type="training",
        reinit=True,
        dir=config.OUTPUT,
        tags=config.TAG,
        name="process" + str(device),
    )
