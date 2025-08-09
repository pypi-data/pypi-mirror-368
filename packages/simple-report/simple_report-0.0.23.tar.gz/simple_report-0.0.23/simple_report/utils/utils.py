import base64
from urllib.parse import quote
from io import BytesIO, StringIO


def base64_image(image: bytes, mime_type: str) -> str:
    """Encode the image for an URL using base64
    Args:
        image: the image
        mime_type: the mime type
    Returns:
        A string starting with "data:{mime_type};base64,"
    """
    base64_data = base64.b64encode(image)
    image_data = quote(base64_data)
    return f"data:{mime_type};base64,{image_data}"


def plot_360_n0sc0pe(figure, image_format) -> str: #config, 
    """Quickscope the plot to a base64 encoded string.
    Args:
        config: Settings
        image_format: png or svg, overrides config.
    Returns:
        A base64 encoded version of the plot in the specified image format.
    """

    mime_types = {"png": "image/png", "svg": "image/svg+xml"}
    if image_format not in mime_types:
        raise ValueError('Can only 360 n0sc0pe "png" or "svg" format.')

    if image_format == "svg":
        image_str = StringIO()
        figure.savefig(image_str, format=image_format)
        result_string = image_str.getvalue()
    else:
        image_bytes = BytesIO()
        figure.savefig(image_bytes, format=image_format)
        result_string = base64_image(
            image_bytes.getvalue(), mime_types[image_format]
        )
    return result_string
