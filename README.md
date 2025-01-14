# HTR Annotation Tool

This annotation tool can be used for annotation of roi image crops to create dataset required for finetuning of OCR models.

## Setup
 * Clone this repositary  
 * Install dependencies `pip install -r requirements.txt`
 * Prepare data with the folder structure mentioned below.
 * Set data path folder to `DATASET_DIR` varaible in the `htr_tool.py`.

## Folder structure for data
```
DATA
 |-- doc_1
   |-- crop1.jpg
   |-- crop2.jpg
   |-- doc_1.csv
|--doc_2
   |-- crop1.jpg
   |-- crop2.jpg
   |-- doc_2.csv
 
```

Here, `crop_<x>.jpg` are the images with text or handwritting and `doc_<x>.csv` contains initial OCR results. This must contain these three columns: `image, text, isInvalid`.

```
image -> name or cropped image eg: crop_1.jpg
text -> text in the corresponding image
isInvalid -> Flag to set if the roi crop is suitable for model training.
```