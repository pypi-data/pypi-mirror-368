# Copyright (c) OpenMMLab. All rights reserved.
_base_ = [
    './base1.py',
    './base4.py'
]

item3 = False
item4 = 'test'
item8 = '{{fileBasename}}'
item9 = {{_base_.item1}}
item10 = {{_base_.item7.b.c}}
