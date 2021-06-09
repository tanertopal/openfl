import os
from pathlib import Path
from hashlib import sha384
import numpy as np
from PIL import Image
from openfl.interface.interactive_api.shard_descriptor import ShardDescriptor


class KvasirShardDescriptor(ShardDescriptor):

    def __init__(self, data_folder: str = 'kvasir_data',
                 rank_worldsize: str = '1,1',
                 enforce_image_hw: str = None) -> None:
        super().__init__()

        self.data_folder = Path.cwd() / data_folder
        self.download_data(self.data_folder)

        # Settings for resizing data
        self.enforce_image_hw = tuple(int(size) for size in enforce_image_hw.split(',')) if \
            enforce_image_hw is not None else None
        # Settings for sharding the dataset
        self.rank_worldsize = tuple(int(num) for num in rank_worldsize.split(','))

        self.images_path = self.data_folder / 'segmented-images' / 'images'
        self.masks_path = self.data_folder / 'segmented-images' / 'masks'

        self.images_names = [img_name for img_name in sorted(os.listdir(
            self.images_path)) if len(img_name) > 3 and img_name[-3:] == 'jpg']
        # Sharding
        self.images_names = self.images_names[self.rank_worldsize[0] - 1::self.rank_worldsize[1]]

        # Calculating data and target shapes
        sample, target = self[0]
        self._sample_shape = [str(dim) for dim in sample.shape]
        self._target_shape = [str(dim) for dim in target.shape]

    @staticmethod
    def download_data(data_folder):
        zip_file_path = data_folder / 'kvasir.zip'
        os.makedirs(data_folder, exist_ok=True)
        os.system("wget -nc"
                  + " 'https://datasets.simula.no/hyper-kvasir/hyper-kvasir-segmented-images.zip'"
                  + f" -O {zip_file_path.relative_to(Path.cwd())}")
        ZIP_SHA384 = 'e30d18a772c6520476e55b610a4db457237f151e'\
            '19182849d54b49ae24699881c1e18e0961f77642be900450ef8b22e7'
        assert sha384(open(zip_file_path, 'rb').read(
            os.path.getsize(zip_file_path))).hexdigest() == ZIP_SHA384
        os.system(f"unzip -n {zip_file_path.relative_to(Path.cwd())}"
                  + f" -d {data_folder.relative_to(Path.cwd())}")

    def __getitem__(self, index):
        name = self.images_names[index]
        # Reading data
        img = Image.open(self.images_path / name)
        mask = Image.open(self.masks_path / name)
        if self.enforce_image_hw is not None:
            # If we need to resize data
            # PIL accepts (w,h) tuple, not (h,w)
            img = img.resize(self.enforce_image_hw[::-1])
            mask = mask.resize(self.enforce_image_hw[::-1])
        img = np.asarray(img)
        mask = np.asarray(mask)
        assert(img.shape[2] == 3)

        return (img, mask[:, :, 0].astype(np.uint8))

    def __len__(self):
        return len(self.images_names)

    @property
    def sample_shape(self):
        # int( sum( [str(dim) for dim in sample.shape] ) )
        return self._sample_shape

    @property
    def target_shape(self):
        return self._target_shape

    @property
    def dataset_description(self) -> str:
        return f'Kvasir dataset, shard number {self.rank_worldsize[0]}'\
            f' out of {self.rank_worldsize[1]}'


if __name__ == "__main__":
    import logging
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    data_folder = 'data'
    rank_worldsize = '1,2'
    enforce_image_hw = '529,622'

    kvasir_sd = KvasirShardDescriptor(
        data_folder,
        rank_worldsize=rank_worldsize,
        enforce_image_hw=enforce_image_hw)

    print(kvasir_sd.dataset_description)
    print(kvasir_sd.sample_shape, kvasir_sd.target_shape)

    from openfl.component.collaborator_manager.collaborator_manager import CollaboratorManager

    shard_name = rank_worldsize
    director_uri = 'localhost:50051'

    keeper = CollaboratorManager(
        shard_name=shard_name,
        director_uri=director_uri,
        shard_descriptor=kvasir_sd)

    keeper.start()
