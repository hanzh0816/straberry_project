import os
import time
import datetime
import numpy as np
import torch
from tqdm import tqdm
import torch.nn as nn
import torch.nn.functional as F
from timm.utils import accuracy, AverageMeter
from accelerate import Accelerator
import wandb
from datasets import build_loader
from utils import (
    parse_option,
    build_scheduler,
    create_logger,
    save_checkpoint,
    set_logger,
    wandb_init,
)
from models import build_model, save_model


@torch.no_grad()
def validate(accelerator, config, data_loader, processor, model, criterion):
    model.eval()

    batch_time = AverageMeter()
    loss_meter = AverageMeter()
    acc1_meter = AverageMeter()

    end = time.time()
    for idx, (inputs, labels) in enumerate(data_loader):
        inputs = inputs.to(device)
        if processor is not None:
            inputs = processor(images=inputs, return_tensors="pt")
            inputs["pixel_values"] = inputs["pixel_values"].to(device)

        labels = labels.to(device)

        outputs = model(**inputs)
        logits = outputs.logits
        loss = criterion(logits, labels.long())
        loss_meter.update(loss.item(), labels.size(0))

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
                f"Loss {loss_meter.val:.3f} ({loss_meter.avg:.3f})\t"
                f"Mem {memory_used:.0f}MB"
            )
    logger.info(f" * Acc@1 {acc1_meter.avg:.3f}")
    return {"acc1": acc1_meter.avg, "val_loss": loss_meter.avg}


def train_one_epoch(
    accelerator,
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

    t = tqdm(data_loader, disable=not accelerator.is_main_process)
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
        # loss.backward()
        accelerator.backward(loss)
        optimizer.step()

        loss_meter.update(loss.item(), labels.size(0))
        batch_time.update(time.time() - end)
        end = time.time()
        if accelerator.is_main_process and (idx % config.PRINT_FREQ == 0):
            lr = optimizer.param_groups[0]["lr"]
            memory_used = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
            logger.info(
                f"Train: [{epoch}/{config.TRAIN.EPOCHS}][{idx}/{num_steps}]\t"
                f"time {batch_time.val:.4f} ({batch_time.avg:.4f})\t"
                f"loss {loss_meter.val:.4f} ({loss_meter.avg:.4f})\t"
                f"mem {memory_used:.0f}MB"
            )

    if accelerator.is_main_process:
        epoch_time = time.time() - start
        logger.info(
            f"EPOCH {epoch} training takes {datetime.timedelta(seconds=int(epoch_time))}"
        )
    return {"train_loss": loss_meter.avg}


def main(accelerator, config, logger):
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

    # 设置优化器
    optimizer = torch.optim.AdamW(
        model.parameters(),
        eps=config.TRAIN.OPTIMIZER.EPS,
        betas=config.TRAIN.OPTIMIZER.BETAS,
        lr=config.TRAIN.BASE_LR,
        weight_decay=config.TRAIN.WEIGHT_DECAY,
    )
    # prepare
    data_loader_train, model, optimizer = accelerator.prepare(
        data_loader_train, model, optimizer
    )

    # 损失函数设置
    criterion = nn.CrossEntropyLoss()
    logger.info("Start training")
    start_time = time.time()

    max_accuracy = 0.0
    for epoch in range(config.TRAIN.START_EPOCH, config.TRAIN.EPOCHS):
        # 设置sampler epoch
        train_metrics = train_one_epoch(
            accelerator,
            config,
            processor,
            model,
            criterion,
            data_loader_train,
            optimizer,
            epoch,
        )

        if accelerator.is_main_process:
            val_metrics = validate(
                accelerator, config, data_loader_val, processor, model, criterion
            )
            acc1 = val_metrics["acc1"]
            if epoch % config.SAVE_FREQ == 0 and (acc1 > max_accuracy):
                unwrapped_model = accelerator.unwrap_model(model)
                save_model(unwrapped_model, config)

            metric = {**train_metrics, **val_metrics}
            metric["lr"] = optimizer.state_dict()["param_groups"][0]["lr"]
            wandb.log(metric)

            print(f"Accuracy of the network on the valid images: {acc1:.1f}%")
            logger.info(f"Accuracy of the network on the valid images: {acc1:.1f}%")
            max_accuracy = max(max_accuracy, acc1)
            logger.info(f"Max accuracy: {max_accuracy:.2f}%")

            total_time = time.time() - start_time
            total_time_str = str(datetime.timedelta(seconds=int(total_time)))
            logger.info("Training time {}".format(total_time_str))


if __name__ == "__main__":
    # print(os.path.dirname(__file__))
    # os.chdir(os.path.dirname(__file__))

    accelerator = Accelerator()
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = accelerator.device
    _, config = parse_option()

    seed = config.SEED
    torch.manual_seed(seed)
    np.random.seed(seed)

    logger = set_logger(config)
    wandb_init(config, device=device)
    main(accelerator, config, logger)
