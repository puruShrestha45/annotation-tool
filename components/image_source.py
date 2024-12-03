from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple
from PIL import Image
import os
import logging
from mashumaro import DataClassDictMixin
from dash import Output, Input, html, callback, MATCH
from typing import Optional, Union, List, Callable
import uuid
import dash_bootstrap_components as dbc


logger = logging.getLogger(__name__)


class IndexBelowError(Exception):
    pass


class IndexAboveError(Exception):
    pass


class ImageSourceSelector(html.Div):
    class ids:
        folder_path = lambda aio_id: {
            'component': 'AnnotateImageLabelsAIO',
            'subcomponent': 'folder_path',
            'aio_id': aio_id
        }
    ids = ids
    
    def __init__(
        self,
        refresh_layout_callback: Callable[[], dbc.Row],
        aio_id: Optional[str] = None
        ):
        self._refresh_layout_callback = refresh_layout_callback
        
        # Allow developers to pass in their own `aio_id` if they're
        # binding their own callback to a particular component.
        if aio_id is None:
            # Otherwise use a uuid that has virtually no chance of collision.
            # Uuids are safe in dash deployments with processes
            # because this component's callbacks
            # use a stateless pattern-matching callback:
            # The actual ID does not matter as long as its unique and matches
            # the PMC `MATCH` pattern..
            self.aio_id = str(uuid.uuid4())
        else:
            self.aio_id = aio_id
            
        super().__init__(self._create_layout())
        self._define_callbacks()
    
    def _create_layout(self):
        return html.Div([
            dbc.Input(
                id=self.ids.folder_path(self.aio_id),
                type="text",
                placeholder="Enter folder path",
                className="mb-2",
            )
        ])

@dataclass
class ImageSource(DataClassDictMixin):
    """Specification for where to get images from
    """
    
    class Type(Enum):
        DEFAULT = "default"
        FOLDER = "folder"
        LIST_OF_FILES = "list_of_files"

    # Source type
    source_type: Type = Type.DEFAULT

    # Default source: list of image names and images
    images: Optional[List[Tuple[str,Image.Image]]] = field(default=None, metadata={"serialize": lambda x: None, "deserialize": lambda x: None})

    # Folder source
    folder_name: Optional[str] = None

    # Folder source: pattern to match
    folder_pattern: str = "*.jpg"

    # List of files source
    list_of_files: Optional[List[str]] = None


    def __post_init__(self):
        if self.source_type == ImageSource.Type.DEFAULT:
            assert self.images is not None, "images must be set if source_type is DEFAULT"
        elif self.source_type == ImageSource.Type.FOLDER:
            assert self.folder_name is not None, "folder_name must be set if source_type is FOLDER"
        elif self.source_type == ImageSource.Type.LIST_OF_FILES:
            assert self.list_of_files is not None, "list_of_files must be set if source_type is LIST_OF_FILES"
        else:
            raise NotImplementedError


class ImageIterator:
    """Iterator over images
    """
    

    def __init__(self, image_source: ImageSource):
        self.image_source = image_source
        self.idx_of_curr_img = -1

        self._file_names = None
        if image_source.source_type == ImageSource.Type.FOLDER:
            import glob
            assert image_source.folder_name is not None, "folder_name must be set if source_type is FOLDER"
            self._file_names = glob.glob(os.path.join(image_source.folder_name,image_source.folder_pattern))
            self.no_images = len(self._file_names)
        elif image_source.source_type == ImageSource.Type.LIST_OF_FILES:
            assert image_source.list_of_files is not None, "list_of_files must be set if source_type is LIST_OF_FILES"
            self._file_names = image_source.list_of_files
            self.no_images = len(self._file_names)
        else:
            assert image_source.images is not None, "images must be set if source_type is DEFAULT"
            self.no_images = len(image_source.images)
    

    def _image_at_idx(self, idx: int) -> Tuple[int,str,Image.Image]:
        logger.debug(f"Loading image at index {idx}")
        if self.image_source.source_type == ImageSource.Type.DEFAULT:
            assert self.image_source.images is not None, "images must be set if source_type is DEFAULT"
            ret = self.image_source.images[idx]
            return idx, ret[0], ret[1]
        else:
            assert self._file_names is not None, "file_names must be set if source_type is not DEFAULT"
            return idx, self._file_names[idx], Image.open(self._file_names[idx])


    def next(self) -> Tuple[int,str,Image.Image]:
        if self.idx_of_curr_img >= self.no_images-1:
            self.idx_of_curr_img = self.no_images
            raise IndexAboveError
        
        self.idx_of_curr_img += 1
        if self.idx_of_curr_img >= self.no_images:
            raise IndexAboveError
        result = self._image_at_idx(self.idx_of_curr_img)

        return result


    def prev(self) -> Tuple[int,str,Image.Image]:
        if self.idx_of_curr_img <= 0:
            self.idx_of_curr_img = -1
            raise IndexBelowError
        
        self.idx_of_curr_img -= 1
        result = self._image_at_idx(self.idx_of_curr_img)
        return result


    def __iter__(self):
        return self

