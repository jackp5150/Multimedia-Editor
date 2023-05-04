from PIL import Image
from reportlab.lib.pagesizes import letter
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
import yt_dlp as youtube_dl
import json
import xml.etree.ElementTree as ET
import os
# import win32com.client as win32
# from docx import Document
from io import BytesIO
from reportlab.pdfgen import canvas
from moviepy.editor import *
from reportlab.lib.units import inch
# from pptx import Presentation





def png_files_to_pdf(png_files, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)

    for png_file in png_files:
        img = Image.open(png_file)
        img_width, img_height = img.size
        img_aspect_ratio = img_width / img_height

        # Calculate dimensions to fit the image on the letter page while maintaining aspect ratio
        page_width, page_height = letter
        if img_aspect_ratio > 1:
            width = page_width
            height = int(page_width / img_aspect_ratio)
        else:
            height = page_height
            width = int(page_height * img_aspect_ratio)

        # Calculate the position to center the image on the page
        x = (page_width - width) / 2
        y = (page_height - height) / 2

        # Add the image to the PDF
        c.drawImage(png_file, x, y, width, height)
        c.showPage()

    c.save()

def pdf_to_png(pdf_file, output_file):
    # Load the PDF and convert each page to an image
    images = convert_from_path(pdf_file)

    # Save each image as a separate PNG file
    for i, img in enumerate(images):
        output_dir = os.path.dirname(output_file)
        output_base_name = os.path.splitext(os.path.basename(output_file))[0]
        output_png = os.path.join(output_dir, f"{output_base_name}_page_{i}.png")
        img.save(output_png, "PNG")


def pdf_to_jpeg(pdf_file, output_file):
    # Load the PDF and convert each page to an image
    images = convert_from_path(pdf_file)

    # Save each image as a separate JPEG file
    for i, img in enumerate(images):
        output_dir = os.path.dirname(output_file)
        output_base_name = os.path.splitext(os.path.basename(output_file))[0]
        output_jpeg = os.path.join(output_dir, f"{output_base_name}_page_{i}.jpeg")
        img.save(output_jpeg, "JPEG")


def png_to_jpeg(png_file, output_jpeg):
    # Open the PNG image
    img = Image.open(png_file)

    # Save the image as a JPEG file
    img.save(output_jpeg, "JPEG")

import os

def extract_audio_from_youtube(url, output_filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", f'{output_filename}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'C:/Users/jackp/Downloads/ffmpeg-2023-04-30-git-e7c690a046-essentials_build/ffmpeg-2023-04-30-git-e7c690a046-essentials_build/bin',  # Replace with the actual path if necessary
        'prefer_ffmpeg': True,
        'postprocessor_args': ['-vn'],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])



def webp_to_pdf(webp_file, output_pdf):
    # Open the WebP image
    img = Image.open(webp_file)

    # Convert the image to RGB
    img = img.convert('RGB')

    # Save the image as a PDF file
    img.save(output_pdf, "PDF")


def webp_to_png(webp_file, output_png):
    # Open the WebP image
    img = Image.open(webp_file)

    # Save the image as a PNG file
    img.save(output_png, "PNG")

def webp_to_jpeg(webp_file, output_jpeg):
    # Open the WebP image
    img = Image.open(webp_file)

    # Save the image as a JPEG file
    img.save(output_jpeg, "JPEG")


def json_to_xml(json_file, output_xml):
    # Read JSON data from file
    with open(json_file, 'r') as file:
        json_data = file.read()

    # Load JSON data
    data = json.loads(json_data)


    # Create root element
    root = ET.Element("root")

    # Convert JSON to XML
    def convert_json_to_xml(json_data, parent):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                node = ET.SubElement(parent, key)
                convert_json_to_xml(value, node)
        elif isinstance(json_data, list):
            for item in json_data:
                node = ET.SubElement(parent, "item")
                convert_json_to_xml(item, node)
        else:
            parent.text = str(json_data)

    convert_json_to_xml(data, root)

    # Save the XML tree to file
    tree = ET.ElementTree(root)
    tree.write(output_xml)

def xml_to_json(xml_file, output_json):
    # Load the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Convert XML to JSON
    def convert_xml_to_json(node):
        json_data = {}
        for element in node:
            if element.tag in json_data:
                if not isinstance(json_data[element.tag], list):
                    json_data[element.tag] = [json_data[element.tag]]
                json_data[element.tag].append(convert_xml_to_json(element))
            else:
                json_data[element.tag] = convert_xml_to_json(element)
        return json_data or node.text

    # Save the JSON data to file
    with open(output_json, "w") as f:
        json.dump(convert_xml_to_json(root), f)

def strip_audio_from_mp4(mp4_file, output_mp3):
    # Load the video file
    video = VideoFileClip(mp4_file)

    # Get the audio from the video
    audio = video.audio

    # Save the audio as an MP3 file
    audio.write_audiofile(output_mp3, codec='mp3')

def jpeg_to_pdf(jpeg_files, output_pdf):
    # Create a canvas for the PDF
    c = canvas.Canvas(output_pdf, pagesize=letter)

    for jpeg_file in jpeg_files:
        # Open the JPEG image
        img = Image.open(jpeg_file)
        img_width, img_height = img.size
        img_aspect_ratio = img_width / img_height

        # Calculate dimensions to fit the image on the letter page while maintaining aspect ratio
        page_width, page_height = letter
        if img_aspect_ratio > 1:
            width = page_width
            height = int(page_width / img_aspect_ratio)
        else:
            height = page_height
            width = int(page_height * img_aspect_ratio)

        # Calculate the position to center the image on the page
        x = (page_width - width) / 2
        y = (page_height - height) / 2

        # Add the image to the PDF
        c.drawImage(jpeg_file, x, y, width, height)
        c.showPage()

    # Save the PDF
    c.save()