from typing import TypeVar

from ..asset.base_asset import BaseAsset

AssetType = TypeVar('AssetType', bound=BaseAsset)


class Portfolio:
    def __init__(self, *args: BaseAsset):
        self.assets: list[BaseAsset] = list(args)

    def add(self, asset: BaseAsset):
        for index in range(len(self.assets)):
            if self.assets[index] != asset:
                continue

            self.assets[index] += asset
            break
        else:
            self.assets.append(asset)

    def sub(self, asset: BaseAsset):
        for index in range(len(self.assets)):
            if self.assets[index] != asset:
                continue

            self.assets[index] -= asset
            break
        else:
            self.assets.append(-asset)

        self.assets = [i for i in self.assets if not (i.is_empty and i.is_closeable)]

    def __add__(self, other: BaseAsset | list[BaseAsset]):
        if isinstance(other, BaseAsset):
            self.add(other)

        if isinstance(other, list):
            for asset in other:
                assert isinstance(asset, BaseAsset), f"只允许添加资产, 实际为{type(asset)}"
                self.add(asset)

        return self

    def __sub__(self, other: BaseAsset | list[BaseAsset]):
        if isinstance(other, BaseAsset):
            self.sub(other)

        if isinstance(other, list):
            for asset in other:
                assert isinstance(asset, BaseAsset), f"只允许减少资产, 实际为{type(asset)}"
                self.sub(asset)

        return self

    def __getitem__(self, item: type[AssetType]) -> list[AssetType]:
        return [i for i in self.copy.assets if isinstance(i, item)]

    def __iter__(self):
        return iter(self.copy.assets)

    @property
    def copy(self) -> "Portfolio":
        return Portfolio(*[asset.copy for asset in self.assets])

    def __repr__(self):
        return f"资产: {self.assets}"

    __str__ = __repr__


__all__ = ["Portfolio"]
