import os
import yaml
import torch.distributed as dist
from yacs.config import CfgNode as CN

_C = CN()
_C.BASE = [""]

# ---------------------------------------------------------
# Data settings
# ---------------------------------------------------------

_C.DATA = CN()
_C.DATA.BATCH_SIZE = 128
_C.DATA.DATA_PATH = ""
_C.DATA.DATASET = "Strawberry"
_C.DATA.IMG_SIZE = 224

# ---------------------------------------------------------
# Model settings
# ---------------------------------------------------------

_C.MODEL = CN()

_C.MODEL.TYPE = "ViT"
# Model name
_C.MODEL.NAME = "vit-base-patch16-224"
# Number of classes, can not be overwritten
_C.MODEL.NUM_CLASSES = 3
# Checkpoint to resume, could be overwritten by command line argument
_C.MODEL.RESUME = ""
# Using pretrained model (not yet implemented)
_C.MODEL.PRETRAINED = False
_C.MODEL.PRETRAINED_PATH = ""


# ViT model settings
_C.MODEL.PATCH_SIZE = 16
_C.MODEL.NUM_HEADS = 12
_C.MODEL.EMBED_DIM = 768
_C.MODEL.NUM_LAYERS = 12
_C.MODEL.MLP_DIM = 3072


# ---------------------------------------------------------
# Training settings
# ---------------------------------------------------------

_C.TRAIN = CN()
_C.TRAIN.START_EPOCH = 0
_C.TRAIN.EPOCHS = 300
_C.TRAIN.WARMUP_EPOCHS = 20
_C.TRAIN.WEIGHT_DECAY = 0.05
_C.TRAIN.BASE_LR = 5e-4
_C.TRAIN.WARMUP_LR = 5e-7
_C.TRAIN.MIN_LR = 5e-6

_C.TRAIN.AUTO_RESUME = True
# could be overwritten by command line argument
_C.TRAIN.USE_CHECKPOINT = False

# LR scheduler
_C.TRAIN.LR_SCHEDULER = CN()
_C.TRAIN.LR_SCHEDULER.NAME = "cosine"
# Epoch interval to decay LR, used in StepLRScheduler
_C.TRAIN.LR_SCHEDULER.DECAY_EPOCHS = 30
# LR decay rate, used in StepLRScheduler
_C.TRAIN.LR_SCHEDULER.DECAY_RATE = 0.1
# Optimizer
_C.TRAIN.OPTIMIZER = CN()
_C.TRAIN.OPTIMIZER.NAME = "adamw"
# Optimizer Epsilon
_C.TRAIN.OPTIMIZER.EPS = 1e-8
# Optimizer Betas
_C.TRAIN.OPTIMIZER.BETAS = (0.9, 0.999)
# SGD momentum
_C.TRAIN.OPTIMIZER.MOMENTUM = 0.9
# local rank for DistributedDataParallel, given by command line argument
_C.LOCAL_RANK = 0

# ---------------------------------------------------------
# Other settings
# ---------------------------------------------------------
_C.SEED = 0
# Path to output folder, overwritten by command line argument
_C.OUTPUT = ""
# Tag of experiment, overwritten by command line argument
_C.TAG = "default"
# Frequency to save checkpoint
_C.SAVE_FREQ = 5
# Frequency to logging info
_C.PRINT_FREQ = 10
# Perform evaluation only, overwritten by command line argument
_C.EVAL_MODE = False


def _update_config_from_file(config, cfg_file):
    config.defrost()
    with open(cfg_file, "r") as f:
        yaml_cfg = yaml.load(f, Loader=yaml.FullLoader)

    for cfg in yaml_cfg.setdefault("BASE", [""]):
        if cfg:
            _update_config_from_file(config, os.path.join(os.path.dirname(cfg_file), cfg))
    print("=> merge config from {}".format(cfg_file))
    config.merge_from_file(cfg_file)
    config.freeze()


def update_config(config, args):
    _update_config_from_file(config, args.cfg)

    config.defrost()
    if args.opts:
        config.merge_from_list(args.opts)

    # merge from specific arguments
    if args.batch_size:
        config.DATA.BATCH_SIZE = args.batch_size
    if args.data_path:
        config.DATA.DATA_PATH = args.data_path
    if args.resume:
        config.MODEL.RESUME = args.resume
    if args.use_checkpoint:
        config.TRAIN.USE_CHECKPOINT = True
    if args.output:
        config.OUTPUT = args.output
    if args.tag:
        config.TAG = args.tag
    if args.eval:
        config.EVAL_MODE = True

    config.TRAIN.LR = args.lr

    # set local rank for distributed training
    # config.LOCAL_RANK = args.local_rank
    # if config.LOCAL_RANK is None:
    #     config.LOCAL_RANK = int(os.environ["RANK"])

    # output folder
    config.OUTPUT = os.path.join(config.OUTPUT, config.MODEL.NAME, config.TAG)

    config.freeze()


def get_config(args):
    """Get a yacs CfgNode object with default values."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    config = _C.clone()
    update_config(config, args)

    return config
