_base_ = ['../../_base_/models/x3d.py', '../../_base_/default_runtime.py']

# dataset settings
dataset_type = 'VideoDataset'
data_root = 'data/kinetics400/videos_train'
data_root_val = 'data/kinetics400/videos_val'
ann_file_train = 'data/kinetics400/kinetics400_train_list_videos.txt'
ann_file_val = 'data/kinetics400/kinetics400_val_list_videos.txt'
ann_file_test = 'data/kinetics400/kinetics400_val_list_videos.txt'

train_pipeline = [
    dict(type='DecordInit'),
    dict(
        type='SampleFrames',
        clip_len=13,
        frame_interval=6,
        num_clips=1,
        # target_fps=30
    ),
    dict(type='DecordDecode'),
    dict(type='RandomRescale', scale_range=(182, 228)),
    dict(type='RandomCrop', size=160),
    dict(type='Flip', flip_ratio=0.5),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

val_pipeline = [
    dict(type='DecordInit'),
    dict(
        type='SampleFrames',
        clip_len=13,
        frame_interval=6,
        num_clips=1,
        test_mode=True,
        # target_fps=30,
    ),
    dict(type='DecordDecode'),
    dict(type='Resize', scale=(-1, 182)),
    dict(type='CenterCrop', crop_size=160),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

test_pipeline = [
    dict(type='DecordInit'),
    dict(
        type='SampleFrames',
        clip_len=13,
        frame_interval=6,
        num_clips=10,
        test_mode=True,
        # target_fps=30,
    ),
    dict(type='DecordDecode'),
    dict(type='Resize', scale=(-1, 182)),
    dict(type='ThreeCrop', crop_size=182),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

train_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_train,
        data_prefix=dict(video=data_root),
        pipeline=train_pipeline))

val_dataloader = dict(
    batch_size=16,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_val,
        data_prefix=dict(video=data_root_val),
        pipeline=val_pipeline,
        test_mode=True))

test_dataloader = dict(
    batch_size=1,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_val,
        data_prefix=dict(video=data_root_val),
        pipeline=test_pipeline,
        test_mode=True))

val_evaluator = dict(type='AccMetric')
test_evaluator = val_evaluator
test_cfg = dict(type='TestLoop')

train_cfg = dict(
    type='EpochBasedTrainLoop', max_epochs=300, val_begin=1, val_interval=1)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')

# learning policy
param_scheduler = [
    dict(type='LinearLR', start_factor=0.1, by_epoch=True, begin=0, end=35),
    dict(
        type='CosineAnnealingLR',
        T_max=300,
        eta_min=0,
        by_epoch=True,
        begin=0,
        end=300,
        convert_to_iter_based=True)
]

optim_wrapper = dict(
    optimizer=dict(
        type='SGD', lr=0.8, momentum=0.9, weight_decay=5e-5, nesterov=True),
    paramwise_cfg=dict(norm_decay_mult=0))

default_hooks = dict(
    checkpoint=dict(interval=3, max_keep_ckpts=5), logger=dict(interval=20))

custom_hooks = [dict(type='PreciseBNHook', num_iters=10)]
# Default setting for scaling LR automatically
#   - `enable` means enable scaling LR automatically
#       or not by default.
#   - `base_batch_size` = (8 GPUs) x (8 samples per GPU).
auto_scale_lr = dict(enable=True, base_batch_size=1024)
