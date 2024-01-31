import os
import shutil
import torch
import numpy as np
import random
from torchvision import datasets, transforms
import torch.distributed as dist
from timm.data import Mixup
from timm.data import create_transform
from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD
from timm.models.layers import to_2tuple
import torch.utils.data


def collate_fn(batch):
    """
    对batch数据进行处理
    :param batch: [一个getitem的结果，getitem的结果,getitem的结果]
    :return: 元组
    """
    reviews, labels = zip(*batch)
    # print(reviews)
    # print(labels)
    # reviews = torch.Tensor(reviews)
    labels = torch.Tensor(labels)
    return reviews, labels


def divide_dataset(src_path, dst_path):
    class_names = os.listdir(src_path)
    print(class_names)
    for name in class_names:
        for i in ["train", "val", "test"]:
            path = os.path.join(dst_path, i, name)
            if not os.path.exists(path):
                os.makedirs(path)

    for class_name in class_names:
        pic_names = os.listdir(os.path.join(src_path, class_name))

        random.shuffle(pic_names)
        # 按照8：1：1比例划分

        train_list = pic_names[: int(len(pic_names) * 0.8)]
        valid_list = pic_names[int(len(pic_names) * 0.8) : int(0.9 * len(pic_names))]
        test_list = pic_names[int(0.9 * len(pic_names)) :]

        for pic_name in train_list:
            shutil.copy(
                os.path.join(src_path, class_name, pic_name),
                os.path.join(dst_path, "train", class_name, pic_name),
            )
        for pic_name in test_list:
            shutil.copy(
                os.path.join(src_path, class_name, pic_name),
                os.path.join(dst_path, "test", class_name, pic_name),
            )
        for pic_name in valid_list:
            shutil.copy(
                os.path.join(src_path, class_name, pic_name),
                os.path.join(dst_path, "val", class_name, pic_name),
            )


def build_transform(is_train, config):
    # if is_train:
    #     transform = create_transform(
    #         input_size=config.DATA.IMG_SIZE,
    #         is_training=True,
    #     )
    #     return transform

    t = []
    t.append(
        transforms.Resize(
            size=to_2tuple(config.DATA.IMG_SIZE),
        )
    )
    t.append(transforms.ToTensor())
    # t.append(transforms.Normalize(IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD))
    return transforms.Compose(t)


def build_dataset(is_train, prefix, config):
    transform = build_transform(is_train, config)
    root = os.path.join(config.DATA.DATA_PATH, prefix)
    dataset = datasets.ImageFolder(root, transform=transform)
    return dataset


def build_loader(config):
    """
    构建多GPU dataloader
    """
    dataset_train = build_dataset(is_train=True, prefix="train", config=config)
    # print(f"local rank {config.LOCAL_RANK} / global rank {dist.get_rank()} successfully build train dataset")
    dataset_val = build_dataset(is_train=False, prefix="val", config=config)
    # print(f"local rank {config.LOCAL_RANK} / global rank {dist.get_rank()} successfully build valid dataset")
    dataset_test = build_dataset(is_train=False, prefix="test", config=config)
    # print(f"local rank {config.LOCAL_RANK} / global rank {dist.get_rank()} successfully build test dataset")

    # single GPU dataloader
    data_loader_train = torch.utils.data.DataLoader(
        dataset=dataset_train,
        batch_size=config.DATA.BATCH_SIZE,
        shuffle=True,
        drop_last=True,
    )
    # DDP dataloader
    # num_tasks = dist.get_world_size()
    # global_rank = dist.get_rank()

    # sampler_train = torch.utils.data.DistributedSampler(
    #     dataset_train, num_replicas=num_tasks, rank=global_rank, shuffle=True
    # )
    # data_loader_train = torch.utils.data.DataLoader(
    #     dataset=dataset_train,
    #     sampler=sampler_train,
    #     batch_size=config.DATA.BATCH_SIZE,
    #     drop_last=True,
    # )

    data_loader_val = torch.utils.data.DataLoader(
        dataset=dataset_val,
        batch_size=config.DATA.BATCH_SIZE,
        shuffle=False,
        drop_last=False,
    )
    data_loader_test = torch.utils.data.DataLoader(
        dataset=dataset_test,
        batch_size=config.DATA.BATCH_SIZE,
        shuffle=False,
        drop_last=False,
    )

    return (
        dataset_train,
        dataset_val,
        dataset_test,
        data_loader_train,
        data_loader_val,
        data_loader_test,
    )


if __name__ == "__main__":
    pass
