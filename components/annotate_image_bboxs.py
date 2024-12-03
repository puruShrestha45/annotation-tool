from .annotate_image_controller import (
    AnnotateImageController,
    AnnotateImageOptions,
    Bbox,
    BboxUpdate,
    NoUpdate,
)
from .annotate_image_controls import AnnotateImageControlsAIO
from .helpers import get_trigger_id, Xyxy, encode_image_base64
from .image_source import ImageSource
from .label_source import LabelSource
from .image_annotations import ImageAnnotations
from .annotation_storage import AnnotationStorage

from typing import Optional
import plotly.express as px
from dash import dcc, html, Input, Output, no_update, callback, State
from dash import Output, Input, html, dcc, callback, MATCH, ALL
from dash.exceptions import PreventUpdate
from typing import Optional, List, Dict, Any
import plotly.express as px
import dash_bootstrap_components as dbc
from dataclasses import dataclass
import logging
import requests
import os
import time

logger = logging.getLogger(__name__)


class AnnotateImageBboxsAIO(html.Div):
    """Annotation component for images"""

    # A set of functions that create pattern-matching callbacks of the subcomponents
    class ids:
        bbox_labeling = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "bbox_labeling",
            "aio_id": aio_id,
        }
        image = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "image",
            "aio_id": aio_id,
        }
        folder_input = lambda aio_id: {
            "component": "AnnotateImageLabelsAIO",
            "subcomponent": "folder_input",
            "aio_id": aio_id,
        }
        folder_input_submit = lambda aio_id: {
            "component": "AnnotateImageLabelsAIO",
            "subcomponent": "folder_input_submit",
            "aio_id": aio_id,
        }
        graph_picture = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "graph_picture",
            "aio_id": aio_id,
        }
        highlight_bbox = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "highlight_bbox",
            "aio_id": aio_id,
            "idx": idx,
        }
        delete_button = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "delete_button",
            "aio_id": aio_id,
            "idx": idx,
        }
        dropdown = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "dropdown",
            "aio_id": aio_id,
            "idx": idx,
        }
        default_field_type_dropdown = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "default_field_type_dropdown",
            "aio_id": aio_id,
        }
        checkbox = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "checkbox",
            "aio_id": aio_id,
            "idx": idx,
        }
        text_field = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "text_field",
            "aio_id": aio_id,
            "idx": idx,
        }

        strike_through = lambda aio_id, idx: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "strike_through",
            "aio_id": aio_id,
            "idx": idx,
        }
        ocr_button = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "ocr_button",
            "aio_id": aio_id,
        }
        alert = lambda aio_id: {
            "component": "AnnotateImageBboxsAIO",
            "subcomponent": "alert",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        label_source: LabelSource,
        image_source: ImageSource,
        annotation_storage: AnnotationStorage = AnnotationStorage(),
        annotations_existing: Optional[ImageAnnotations] = None,
        aio_id: Optional[str] = None,
        options: AnnotateImageOptions = AnnotateImageOptions(),
    ):
        """Constructor

        Args:
            label_source (LabelSource): Label source
            image_source (ImageSource): Image source
            annotation_storage (AnnotationStorage, optional): Storage. Defaults to AnnotationStorage().
            annotations_existing (Optional[ImageAnnotations], optional): Existing annotations. Defaults to None.
            aio_id (Optional[str], optional): AIO Id to use for components. Defaults to None.
            options (AnnotateImageOptions, optional): Options. Defaults to AnnotateImageOptions().
        """
        options.check_valid()
        self.options = options
        self.label_source = label_source
        self.image_source = image_source
        self.annotation_storage = annotation_storage
        self.annotations_existing = annotations_existing

        self.controller = AnnotateImageController(
            label_source=label_source,
            image_source=image_source,
            annotation_storage=annotation_storage,
            annotations_existing=annotations_existing,
            options=options,
        )
        self.converter = BboxToShapeConverter(options=options)
        self.controls = AnnotateImageControlsAIO(
            controller=self.controller,
            refresh_layout_callback=self._create_layout,
            aio_id=aio_id,
        )
        self.aio_id = self.controls.aio_id
        self.labels = label_source.get_labels()
        self.default_field_type = self.labels[0]

        super().__init__(self.controls)  # Equivalent to `html.Div([...])`
        self._define_callbacks()

    def _create_layout(self):
        """Create layout for component"""
        logger.debug("Creating layout for component")

        curr_image_layout = self._create_layout_for_curr_image()

        instructions_txt = (
            self.options.instructions_custom
            or "Draw bounding boxes on the image, and label the classes."
        )
        instructions = html.P(instructions_txt)

        perform_ocr_button = self._create_ocr_button()

        default_field_type_dropdown = self._create_default_field_type_dropdown()

        return dbc.Row(
            [
                # self._create_folder_input_form(),
                dbc.Col(
                    [
                        html.Div(
                            curr_image_layout,
                            id=self.ids.image(self.aio_id),
                            className="align-self-start border",
                        )
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Col(dbc.Label("Default field type"), md=2),
                                default_field_type_dropdown,
                                perform_ocr_button,
                            ],
                            className="d-flex justify-content-between align-items-center",
                        ),
                        html.Div(id=self.ids.alert(self.aio_id)),
                        instructions,
                        html.Div(id=self.ids.bbox_labeling(self.aio_id)),
                    ],
                    md=6,
                    class_name="align-self-start",
                ),
            ],
            className="ml-0",
        )

    def _create_ocr_button(self):
        return dbc.Col(
            dbc.Button(
                "Perform OCR",
                color="primary",
                size="sm",
                className="mr-2",
                id=self.ids.ocr_button(self.aio_id),
            ),
            md=2,
        )

    def _create_default_field_type_dropdown(self):
        return dbc.Col(
            dcc.Dropdown(
                self.controller.labels,
                value=self.labels[0],
                id=self.ids.default_field_type_dropdown(self.aio_id),
                className="mr-5",
            ),
            md=6,
        )

    def _create_layout_for_curr_image(self):
        """Create layout for the image"""
        image = self.controller.curr.image if self.controller.curr is not None else None
        if image is None:
            return []
        fig = px.imshow(image)
        scale_factor = 1
        fig.update_layout(
            dragmode="drawrect",
            width=image.size[0] * scale_factor,
            height=image.size[1] * scale_factor,
        )
        rgb = self.options.default_bbox_color
        line_color = "rgba(%d,%d,%d,1)" % rgb
        fig.update_layout(dragmode="drawrect", newshape=dict(line_color=line_color))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        config = {
            "modeBarButtonsToAdd": ["drawrect"],
            # "editable": True,
            # "edits": {
            #     # "annotationPosition": True,
            #     # "legendPosition": False,
            #     # "legendText": False,
            #     # "titleText": False
            # },
            "scrollZoom": True,
            # "doubleClick": "reset+autosize",
            "showTips": False,
            "displaylogo": False,
        }
            # dbc.Row(html.P(f"Image: {self.controller.curr.image_name}")),
        return dcc.Graph(
                    id=self.ids.graph_picture(self.aio_id), figure=fig, config=config
                )

    def _create_bbox_layout(self):
        if self.controller.curr is None:
            logger.debug("Creating bbox layout - no curr image")
            return no_update

        if self.controller.curr.bboxs is None:
            logger.debug("Creating bbox layout - no bboxs")
            bbox_list_group = []
        else:
            logger.debug(
                f"Creating bbox layout - num bboxs: {len(self.controller.curr.bboxs)}"
            )
            bbox_list_group = [
                self._create_list_group_for_bbox_layout(bbox, idx)
                for idx, bbox in enumerate(self.controller.curr.bboxs)
            ]

        return dbc.ListGroup(bbox_list_group)

    def _create_list_group_for_bbox_layout(self, bbox: Bbox, bbox_idx: int):
        bbox.class_name = bbox.class_name or self.default_field_type
        xyxy_label = "(%s)" % ",".join([str(int(x)) for x in bbox.xyxy])
        dropdown = dcc.Dropdown(
            self.controller.labels,
            value=bbox.class_name,
            id=self.ids.dropdown(self.aio_id, bbox_idx),
        )

        if bbox.class_name == "Text Field" or bbox.class_name == "Crossed Our Value":
            field = dcc.Input(
                value=bbox.field_value or "",
                type="text",
                id=self.ids.text_field(self.aio_id, bbox_idx),
                style={"width": "100%"},
            )
        elif bbox.class_name == "Checkbox":
            field = dcc.Dropdown(
                ["checked", "unchecked"],
                value=bbox.field_value or "unchecked",
                id=self.ids.checkbox(self.aio_id, bbox_idx),
            )
        else:
            field = None

        button_delete = dbc.Button(
            "Delete",
            color="danger",
            size="sm",
            className="ml-3",
            id=self.ids.delete_button(self.aio_id, bbox_idx),
        )

        button_highlight = dbc.Button(
            "Highlight",
            color="primary",
            size="sm",
            className="mr-3",
            id=self.ids.highlight_bbox(self.aio_id, bbox_idx),
        )

        return dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(dropdown, lg=2, md=6),
                        dbc.Col(field, lg=6, md=6),
                        dbc.Col(xyxy_label, lg=2, md=6),
                        dbc.Col(
                            [button_highlight, button_delete],
                            lg=2,
                            md=6,
                            className="d-flex justify-content-center",
                        ),
                        # dbc.Col(button_delete, lg=2, md=6)
                    ],
                    className="d-flex",
                )
            ]
        )

    def _create_alert_layout(self, message=None):
        alerts = []

        # No bboxs
        # if len(self.controller.curr_bboxs) == 0:
        #     alerts.append(dbc.Alert("Start by drawing a bounding box", color="primary"))

        # Bboxs without labels
        # for bbox in self.controller.curr_bboxs:
        #     if bbox.class_name is None:
        #         alerts.append(dbc.Alert("All bounding boxes must have labels", color="warning"))
        #         break
        if message is not None:
            alerts.append(dbc.Alert(message, color="warning"))
        return alerts

    def _create_folder_input_form(self):
        return dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id=self.ids.folder_input(self.aio_id),
                        placeholder="Folder path",
                        type="text",
                        value="",
                    ),
                    md=8,
                ),
                dbc.Col(
                    dbc.Button(
                        "Submit",
                        id=self.ids.folder_input_submit(self.aio_id),
                        color="success",
                    ),
                    md=2,
                ),
            ], style={"margin-bottom": "10px"}
        )

    def _define_callbacks(self):
        """Define callbacks"""
        logger.debug("Defining callbacks")
        self._last_callback_time = 0
        self._debounce_interval = 10

        @callback(
            Output(self.ids.bbox_labeling(MATCH), "children"),
            Output(self.ids.graph_picture(MATCH), "figure"),
            Output(self.ids.alert(MATCH), "children"),
            Input(self.ids.graph_picture(MATCH), "relayoutData"),
            Input(self.ids.delete_button(MATCH, ALL), "n_clicks"),
            Input(self.ids.highlight_bbox(MATCH, ALL), "n_clicks"),
            Input(self.ids.ocr_button(MATCH), "n_clicks"),
            # Input(self.ids.folder_input_submit(MATCH), "n_clicks"),
            Input(self.ids.default_field_type_dropdown(MATCH), "value"),
            Input(self.ids.dropdown(MATCH, ALL), "value"),
            Input(self.ids.text_field(MATCH, ALL), "value"),
            Input(self.ids.checkbox(MATCH, ALL), "value"),
            State(self.ids.graph_picture(MATCH), "figure"),
            # State(self.ids.folder_input(MATCH), "value"),
        )
        def update(
            relayout_data,
            n_clicks_delete,
            n_clicks_select,
            n_clicks_ocr,
            # n_click_folder_input_submit,
            default_field_type_dropdown_value,
            dropdown_value,
            text_fields,
            checkboxes,
            figure,
            # folder_input_value
        ):
            
            
            trigger_id, idx = get_trigger_id()
            bboxes = self.controller.curr.bboxs

            if trigger_id == "graph_picture":
                if relayout_data is not None and any(
                    key in relayout_data
                    for key in [
                        "xaxis.range[0]",
                        "xaxis.range[1]",
                        "yaxis.range[0]",
                        "yaxis.range[1]",
                    ]
                ):
                    update = AnnotateImageBboxsAIO.Update(no_update, figure, no_update)
                    return update.bbox_layout, update.figure, update.alert

            cur_text_field_index = 0
            cur_checkbox_index = 0
            field_index_map = {}

            if bboxes is not None:
                for i, bbox in enumerate(bboxes):
                    if bbox.class_name == "Text Field":
                        field_index_map[i] = cur_text_field_index
                        cur_text_field_index += 1
                    elif bbox.class_name == "Checkbox":
                        field_index_map[i] = cur_checkbox_index
                        cur_checkbox_index += 1
            logger.debug(f"Update: trigger ID: {trigger_id} idx: {idx}")

            if trigger_id == "delete_button":
                logger.debug("Pressed delete_button")
                assert idx is not None, "idx should not be None"
                update = self._handle_delete_button_pressed(idx, figure)

            elif trigger_id == "highlight_bbox":
                logger.debug("Pressed highlight_bbox")
                assert idx is not None, "idx should not be None"
                update = self._handle_highlight_button_pressed(idx, figure)

            # elif trigger_id == "folder_input_submit":
            #     print(folder_input_value)
            #     update = self._update_folder(folder_input_value)
                
            elif trigger_id == "ocr_button":
                update = self._handle_ocr_button_pressed(figure)

            elif trigger_id == "default_field_type_dropdown":
                update = self._handle_default_field_type_dropdown(
                    default_field_type_dropdown_value
                )
            elif trigger_id == "dropdown":
                logger.debug(f"Changed dropdown to {dropdown_value}")
                assert idx is not None, "idx should not be None"
                update = self._handle_dropdown_changed(idx, dropdown_value[idx], figure)

            elif trigger_id == "text_field":
                value_idx = field_index_map[idx]
                print("txt", text_fields, idx, field_index_map[idx])
                # print("txt",text_fields[idx])
                logger.debug(f"Changed text_field to {text_fields}")
                assert idx is not None, "idx should not be None"
                update = self._handle_text_field_changed(
                    idx, text_fields[value_idx], figure
                )

            elif trigger_id == "checkbox":
                value_idx = field_index_map[idx]
                print("chk", checkboxes, idx, field_index_map[idx])

                print("chk", checkboxes, idx)
                # print("chk",checkboxes[idx])
                logger.debug(f"Changed text_field to {checkboxes}")
                assert idx is not None, "idx should not be None"
                update = self._handle_text_field_changed(
                    idx, checkboxes[value_idx], figure
                )
            elif trigger_id == "graph_picture":
                if relayout_data is not None and any(
                    key in relayout_data
                    for key in [
                        "xaxis.range[0]",
                        "xaxis.range[1]",
                        "yaxis.range[0]",
                        "yaxis.range[1]",
                    ]
                ):
                    update = AnnotateImageBboxsAIO.Update(no_update, figure, no_update)
                elif relayout_data is not None and "shapes" in relayout_data:
                    # A new box was drawn
                    # We receive all boxes from the data
                    update = self._handle_new_box_drawn(relayout_data)
                elif relayout_data is not None and "shapes" in " ".join(
                    list(relayout_data.keys())
                ):
                    # A box was updated
                    update = self._handle_box_updated(relayout_data)
                else:
                    logger.warning(f"Unrecognized trigger for {trigger_id}")
                    # Just draw latest
                    self.converter.refresh_figure_shapes(
                        figure, self.controller.curr_bboxs
                    )
                    update = AnnotateImageBboxsAIO.Update(
                        self._create_bbox_layout(), figure, self._create_alert_layout()
                    )
            else:
                logger.warning(f"Unrecognized trigger ID: {trigger_id}")
                # Just draw latest
                self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
                update = AnnotateImageBboxsAIO.Update(
                    self._create_bbox_layout(), figure, self._create_alert_layout()
                )

            self._last_callback_time = time.time()
            return update.bbox_layout, update.figure, update.alert

        logger.debug("Defined callbacks")

    @dataclass
    class Update:
        bbox_layout: Any
        figure: Any
        alert: Any

    # def _update_folder(self, folder_input_value):
    #     if folder_input_value is None or not os.path.exists(folder_input_value):
    #         return AnnotateImageBboxsAIO.Update(
    #             no_update, no_update, self._create_alert_layout("Folder does not exist")
    #         )
                    
    #     image_source = ImageSource(source_type=ImageSource.Type.FOLDER, folder_name=folder_input_value, folder_pattern="*.png")
    #     self.controller = AnnotateImageController(
    #         label_source=self.label_source,
    #         image_source=image_source,
    #         annotation_storage=self.annotation_storage,
    #         annotations_existing=self.annotations_existing,
    #         options=self.options,
    #     )
    #     self.converter = BboxToShapeConverter(options=self.options)
    #     self.controls = AnnotateImageControlsAIO(
    #         controller=self.controller,
    #         refresh_layout_callback=self._create_layout,
    #         aio_id=self.aio_id,
    #     )
        
    #     # self.controls.refresh_layout()
        
    #     return AnnotateImageBboxsAIO.Update(
    #         self._create_bbox_layout(), no_update, no_update
    #     )
        
        
    def _handle_ocr_button_pressed(self, figure: Dict) -> Update:
        print("ocr")

        ocr_url = self.options.ocr_url
        if not ocr_url:
            return AnnotateImageBboxsAIO.Update(
                no_update, no_update, self._create_alert_layout()
            )
        image = self.controller.curr.image if self.controller.curr is not None else None

        encoded_image = encode_image_base64(image)
        bboxes = self.controller.curr.bboxs
        indices = []

        for i, box in enumerate(bboxes):
            if box.class_name == "Text Field":
                indices.append(i)

        data = {
            "image": encoded_image,
            "bboxes": [box.xyxy for box in bboxes if box.class_name == "Text Field"],
        }

        url = self.options.ocr_url
        response = requests.post(url, json=data)

        if response.status_code != 200:
            return AnnotateImageBboxsAIO.Update(
                no_update, no_update, self._create_alert_layout()
            )

        data = response.json()
        texts = data["output"]["texts"]
        print("ocr", data)
        index = 0
        print(indices)
        for i, box in enumerate(bboxes):
            if box.class_name == "Text Field":
                # bboxes[i].field_value = texts[index].replace("<p>", "").replace("</p>", "").strip()
                field_value_new = (
                    texts[index].replace("<p>", "").replace("</p>", "").strip()
                )
                self.controller.update_bbox(
                    BboxUpdate(indices[index], field_value_new=field_value_new)
                )
                index += 1

        self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), figure, self._create_alert_layout()
        )

    def _handle_default_field_type_dropdown(
        self, default_field_type_dropdown_value
    ) -> Update:
        print(default_field_type_dropdown_value)
        self.default_field_type = default_field_type_dropdown_value
        return AnnotateImageBboxsAIO.Update(
            no_update, no_update, self._create_alert_layout()
        )

    def _handle_delete_button_pressed(self, idx: int, figure: Dict) -> Update:
        logger.debug(f"Deleting bbox idx: {idx}")
        self.controller.delete_bbox(idx)
        self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), figure, self._create_alert_layout()
        )

    def _handle_highlight_button_pressed(self, idx: int, figure: Dict) -> Update:
        self.controller.curr_bboxs[idx].is_highlighted = not self.controller.curr_bboxs[
            idx
        ].is_highlighted
        self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
        return AnnotateImageBboxsAIO.Update(
            no_update, figure, self._create_alert_layout()
        )

    def _handle_dropdown_changed(
        self, idx: int, dropdown_value_new: str, figure: Dict
    ) -> Update:
        if type(dropdown_value_new) == list:
            logger.warning("Dropdown value is list, expected string")
            return AnnotateImageBboxsAIO.Update(
                no_update, no_update, self._create_alert_layout()
            )
        if dropdown_value_new not in self.labels:
            logger.warning(
                f"Dropdown value {dropdown_value_new} not in labels {self.labels}"
            )

            return AnnotateImageBboxsAIO.Update(
                no_update, no_update, self._create_alert_layout()
            )
        assert idx is not None, "idx should not be None"

        new_field_value = NoUpdate.NO_UPDATE
        if dropdown_value_new == "Crossed Our Value":
            new_field_value = ""

        self.controller.update_bbox(
            BboxUpdate(
                idx, class_name_new=dropdown_value_new, field_value_new=new_field_value
            )
        )
        self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), figure, self._create_alert_layout()
        )

    def _handle_text_field_changed(
        self, idx: int, field_value_new: str, figure: Dict
    ) -> Update:
        if field_value_new is None:
            return AnnotateImageBboxsAIO.Update(
                no_update, no_update, self._create_alert_layout()
            )
        assert idx is not None, "idx should not be None"

        self.controller.update_bbox(BboxUpdate(idx, field_value_new=field_value_new))

        self.converter.refresh_figure_shapes(figure, self.controller.curr_bboxs)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), figure, self._create_alert_layout()
        )

    def _handle_new_box_drawn(self, relayout_data: Dict) -> Update:
        new_shape = relayout_data["shapes"][-1]
        new_bbox = self.converter.shape_to_bbox(new_shape)
        new_bbox.class_name = self.default_field_type
        new_bbox.field_value = None
        self.controller.add_bbox(new_bbox)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), no_update, self._create_alert_layout()
        )

    def _handle_box_updated(self, relayout_data: Dict) -> Update:
        # Parse shapes[0].x1 -> 0 from the brackets
        label = list(relayout_data.keys())[0]
        box_idx = int(label.split(".")[0].replace("shapes[", "").replace("]", ""))
        shapes_label = "shapes[%d]" % box_idx
        xyxy = [
            relayout_data["%s.%s" % (shapes_label, label)]
            for label in ["x0", "y0", "x1", "y1"]
        ]

        # Update
        update = BboxUpdate(box_idx, xyxy_new=xyxy)
        self.controller.update_bbox(update)
        return AnnotateImageBboxsAIO.Update(
            self._create_bbox_layout(), no_update, self._create_alert_layout()
        )


class BboxToShapeConverter:
    def __init__(self, options: AnnotateImageOptions):
        """Converter betweeen bbox and shape formats

        Args:
            options (AnnotateImageOptions): Options
        """
        options.check_valid()
        self.options = options

    def refresh_figure_shapes(self, figure: Dict, bboxs: Optional[List[Bbox]]):
        """Set shapes in the given figure dict from the provided bboxs

        Args:
            figure (Dict): Figure dict
            bboxs (Optional[List[Bbox]]): Bboxs
        """
        figure["layout"]["shapes"] = self.bboxs_to_shapes(bboxs)

    def shape_to_bbox(self, shape: Dict) -> Bbox:
        """Convert shape to bbox

        Args:
            shape (Dict): Shape

        Returns:
            Bbox: Bbox
        """
        xyxy: Xyxy = [shape[c] for c in ["x0", "y0", "x1", "y1"]]
        return Bbox(xyxy, None, None)

    def bboxs_to_shapes(self, bboxs: Optional[List[Bbox]]) -> List[Dict]:
        """Convert bboxs to shapes

        Args:
            bboxs (Optional[List[Bbox]]): Bboxs

        Returns:
            List[Dict]: Shapes
        """
        if bboxs is None:
            return []
        return [self.bbox_to_shape(bbox) for bbox in bboxs]

    def bbox_to_shape(self, bbox: Bbox) -> Dict:
        """Convert bbox to shape

        Args:
            bbox (Bbox): Bbox

        Returns:
            Dict: Shape
        """
        # Line color
        if bbox.class_name is None:
            rgb = self.options.default_bbox_color
            if bbox.is_highlighted:
                rgb = (255, 0, 0)
        else:
            rgb = self.options.get_assign_color_for_class(bbox.class_name)
        line_color = "rgba(%d,%d,%d,1)" % rgb

        # Fill color
        if bbox.is_highlighted:
            fill_color = "rgba(%d,%d,%d,0.45)" % rgb
        else:
            fill_color = "rgba(0,0,0,0)"

        return {
            "editable": True,
            "visible": True,
            "showlegend": False,
            "legend": "legend",
            "legendgroup": "",
            "legendgrouptitle": {"text": ""},
            "legendrank": 1000,
            "label": {"text": "", "texttemplate": ""},
            "xref": "x",
            "yref": "y",
            "layer": "above",
            "opacity": 1,
            "line": {"color": line_color, "width": 4, "dash": "solid"},
            "fillcolor": fill_color,
            "fillrule": "evenodd",
            "type": "rect",
            "x0": bbox.xyxy[0],
            "y0": bbox.xyxy[1],
            "x1": bbox.xyxy[2],
            "y1": bbox.xyxy[3],
        }
