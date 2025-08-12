from mcp.server.fastmcp import FastMCP
from utils import download_pdf, validate_url
from storage import upload_to_cloud  # 可选存储功能
import fitz
import base64
from io import BytesIO
from typing import Dict, List, Union, Optional
import os
import config

mcp = FastMCP("PDFToolsService", port=9025)


@mcp.tool()
def pdf_url_to_images(
        pdf_url: str,
        format: str = "png",
        zoom: float = 2.0,
        page_range: Optional[List[int]] = None,
        output_type: str = "base64"
) -> Dict[str, Union[List[Dict], str, int]]:
    """
    从PDF URL转换图片，返回Base64或存储URL

    参数:
    - pdf_url: PDF文件的公开URL
    - format: 图片格式 (png/jpg)，默认为png
    - zoom: 缩放比例 (0.5-5.0)，默认2.0
    - page_range: 指定转换的页码 (如 [0,2] 表示第1、3页)
    - output_type: 返回类型 - "base64"或"url"

    返回:
    {
        "page_count": 总页数,
        "pages": [
            {
                "page": 页码,
                "image": "base64字符串" 或 "图片URL",
                "format": 图片格式
            }
        ],
        "status": "success" 或 "error",
        "message": 状态描述
    }
    """
    # try:
    # 1. 验证URL安全性
    validate_url(pdf_url)

    # 2. 下载PDF
    pdf_content = download_pdf(pdf_url)

    # 3. 验证PDF大小
    max_size = config.PDF_MAX_SIZE_MB * 1024 * 1024
    if len(pdf_content) > max_size:
        raise ValueError(f"PDF超过大小限制 ({config.PDF_MAX_SIZE_MB}MB)")

    # 4. 打开PDF
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        target_pages = page_range or list(range(len(doc)))
        results = []

        # 5. 逐页处理
        for pg_num in target_pages:
            page = doc.load_page(pg_num)
            pix = page.get_pixmap(
                matrix=fitz.Matrix(zoom, zoom)
            )
            img_data = pix.tobytes()

            # 6. 按输出类型处理结果
            if output_type == "base64":
                results.append({
                    "page": pg_num,
                    "image": base64.b64encode(img_data).decode("utf-8"),
                    "format": format
                })
            elif output_type == "url" and config.UPLOAD_ENABLED:
                image_url = upload_to_cloud(img_data, format)
                results.append({
                    "page": pg_num,
                    "url": image_url,
                    "format": format
                })
            else:
                results.append({
                    "page": pg_num,
                    "format": format,
                    "size_bytes": len(img_data)
                })

        return {
            "page_count": len(doc),
            "pages": results,
            "status": "success",
            "message": f"成功转换 {len(results)} 页"
        }

    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "message": str(e),
    #         "pages": [],
    #         "page_count": 0
    #     }


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()