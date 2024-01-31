import os
import time
import datetime
import numpy as np
import torch
from tqdm import tqdm
import torch.nn as nn
import torch.nn.functional as F
from timm.utils import accuracy, AverageMeter

from datasets import build_loader
from utils import (
    parse_option,
    build_scheduler,
    create_logger,
    save_checkpoint,
    set_logger,
)
from models import build_model, save_model


@torch.no_grad()
def validate(config, data_loader, processor, model):
    model.eval()

    batch_time = AverageMeter()
    acc1_meter = AverageMeter()

    end = time.time()
    for idx, (inputs, labels) in enumerate(data_loader):
        if processor is not None:
            inputs = processor(images=inputs, return_tensors="pt")
            inputs["pixel_values"] = inputs["pixel_values"].to(device)

        labels = labels.to(device)

        outputs = model(**inputs)
        logits = outputs.logits
        predicts = F.softmax(logits, dim=1)
        [acc1] = accuracy(predicts, labels)
        acc1_meter.update(acc1.item(), labels.size(0))
        # acc5_meter.update(acc5.item(), target.size(0))
        batch_time.update(time.time() - end)
        end = time.time()

        if idx % config.PRINT_FREQ == 0:
            memory_used = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
            logger.info(
                f"Test: [{idx}/{len(data_loader)}]\t"
                f"Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t"
                f"Acc@1 {acc1_meter.val:.3f} ({acc1_meter.avg:.3f})\t"
                f"Mem {memory_used:.0f}MB"
            )
    logger.info(f" * Acc@1 {acc1_meter.avg:.3f}")
    return acc1_meter.avg


def train_one_epoch(
    config,
    processor,
    model,
    criterion,
    data_loader,
    optimizer,
    epoch,
):
    model.train()
    optimizer.zero_grad()

    batch_time = AverageMeter()
    loss_meter = AverageMeter()

    num_steps = len(data_loader)
    start = time.time()
    end = time.time()
    
    t = tqdm(data_loader)
    t.set_description("Processing:")
    for idx, (inputs, labels) in enumerate(t):
        if processor is not None:
            inputs = processor(images=inputs, return_tensors="pt")
            inputs["pixel_values"] = inputs["pixel_values"].to(device)

        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(**inputs)
        logits = outputs.logits

        loss = criterion(logits, labels.long())
        loss.backward()
        optimizer.step()

        loss_meter.update(loss.item(), labels.size(0))
        batch_time.update(time.time() - end)
        end = time.time()
        if idx % config.PRINT_FREQ == 0:
            lr = optimizer.param_groups[0]["lr"]
            memory_used = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
            logger.info(
                f"Train: [{epoch}/{config.TRAIN.EPOCHS}][{idx}/{num_steps}]\t"
                f"time {batch_time.val:.4f} ({batch_time.avg:.4f})\t"
                f"loss {loss_meter.val:.4f} ({loss_meter.avg:.4f})\t"
                f"mem {memory_used:.0f}MB"
            )

    epoch_time = time.time() - start
    logger.info(f"EPOCH {epoch} training takes {datetime.timedelta(seconds=int(epoch_time))}")


def main(config, logger):
    (
        dataset_train,
        dataset_val,
        dataset_test,
        data_loader_train,
        data_loader_val,
        data_loader_test,
    ) = build_loader(config)

    logger.info(f"Creating model:{config.MODEL.TYPE}/{config.MODEL.NAME}")
    processor, model = build_model(config)
    model.cuda()

    # 设置优化器
    optimizer = torch.optim.AdamW(
        model.parameters(),
        eps=config.TRAIN.OPTIMIZER.EPS,
        betas=config.TRAIN.OPTIMIZER.BETAS,
        lr=config.TRAIN.BASE_LR,
        weight_decay=config.TRAIN.WEIGHT_DECAY,
    )

    # 损失函数设置
    criterion = nn.CrossEntropyLoss()
    logger.info("Start training")
    start_time = time.time()

    max_accuracy = 0.0
    for epoch in range(config.TRAIN.START_EPOCH, config.TRAIN.EPOCHS):
        # 设置sampler epoch
        train_one_epoch(
            config,
            processor,
            model,
            criterion,
            data_loader_train,
            optimizer,
            epoch,
        )
        acc1 = validate(config, data_loader_val, processor, model)
        print(f"Accuracy of the network on the valid images: {acc1:.1f}%")
        logger.info(f"Accuracy of the network on the valid images: {acc1:.1f}%")
        max_accuracy = max(max_accuracy, acc1)
        logger.info(f"Max accuracy: {max_accuracy:.2f}%")

        if epoch % config.SAVE_FREQ == 0:
            save_model(model, config)

    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    logger.info("Training time {}".format(total_time_str))


if __name__ == "__main__":
    # print(os.path.dirname(__file__))
    # os.chdir(os.path.dirname(__file__))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _, config = parse_option()

    seed = config.SEED
    torch.manual_seed(seed)
    np.random.seed(seed)

    logger = set_logger(config)
    main(config, logger)
