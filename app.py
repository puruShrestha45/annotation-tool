# Import the library

from components.annotate_image_bboxs import AnnotateImageBboxsAIO
from components.image_source import ImageSource
from components.label_source import LabelSource
from components import (
    StorageType,
    AnnotateImageOptions,
    AnnotationStorage,
    load_image_anns_from_storage,
)

# Other imports
from dash import Dash, html
import dash_bootstrap_components as dbc
from skimage import data
from PIL import Image
import os
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Custom Annotation Tool')
parser.add_argument('--data_dir', type=str, required=True, help='Directory containing images to annotate')
args = parser.parse_args()

data_dir = args.data_dir



# Set up the image and label sources
image_source = ImageSource(source_type=ImageSource.Type.FOLDER, folder_name=data_dir, folder_pattern="*.png")
label_source = LabelSource(labels=["Text Field", "Crossed Our Value", "Checkbox", "Crossed Section"])

storage = AnnotationStorage(
    storage_types=[
        StorageType.JSON,  # Default storage type
    ],
    json_file=os.path.join(data_dir,"annotations.json"),
)
annotations_existing = load_image_anns_from_storage(storage)




app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(
    [
        html.H1("Annotate Images"),
        AnnotateImageBboxsAIO(
            label_source=label_source,
            image_source=image_source,
            annotation_storage=storage,
            options=AnnotateImageOptions(ocr_url="http://127.0.0.1:8001/predict/bboxes"),
            annotations_existing=annotations_existing,
        ),
    ],
    fluid=True,
)
app.run(debug=True)
