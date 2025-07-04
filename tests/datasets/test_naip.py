# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
import torch
import torch.nn as nn
from pyproj import CRS

from torchgeo.datasets import (
    NAIP,
    DatasetNotFoundError,
    IntersectionDataset,
    UnionDataset,
)


class TestNAIP:
    @pytest.fixture
    def dataset(self) -> NAIP:
        root = os.path.join('tests', 'data', 'naip')
        transforms = nn.Identity()
        return NAIP(root, transforms=transforms)

    def test_getitem(self, dataset: NAIP) -> None:
        x = dataset[dataset.bounds]
        assert isinstance(x, dict)
        assert isinstance(x['crs'], CRS)
        assert isinstance(x['image'], torch.Tensor)

    def test_len(self, dataset: NAIP) -> None:
        assert len(dataset) == 2

    def test_and(self, dataset: NAIP) -> None:
        ds = dataset & dataset
        assert isinstance(ds, IntersectionDataset)

    def test_or(self, dataset: NAIP) -> None:
        ds = dataset | dataset
        assert isinstance(ds, UnionDataset)

    def test_plot(self, dataset: NAIP) -> None:
        query = dataset.bounds
        x = dataset[query]
        dataset.plot(x, suptitle='Test')
        plt.close()

    def test_no_data(self, tmp_path: Path) -> None:
        with pytest.raises(DatasetNotFoundError, match='Dataset not found'):
            NAIP(tmp_path)

    def test_invalid_query(self, dataset: NAIP) -> None:
        with pytest.raises(
            IndexError, match='query: .* not found in index with bounds:'
        ):
            dataset[0:0, 0:0, pd.Timestamp.min : pd.Timestamp.min]
