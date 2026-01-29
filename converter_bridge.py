import subprocess
import os
import sys
from pathlib import Path
import json


def convert_image_to_avif(input_path, output_path, quality=80, speed=6):
    """調用Node.js轉換器進行AVIF轉換"""
    try:
        # 調用我們的Node.js轉換器
        script_dir = Path(__file__).parent
        converter_path = script_dir / "src" / "converter.js"

        # 使用Node.js運行轉換
        result = subprocess.run(
            [
                "node",
                "-e",
                f"""
import {{ convertToAvif }} from '{converter_path}';
import {{ fileURLToPath }} from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

convertToAvif('{input_path}', '{output_path}', {{
    quality: {quality},
    speed: {speed}
}}).then(result => {{
    console.log(JSON.stringify(result));
}}).catch(error => {{
    console.error('Error:', error.message);
    process.exit(1);
}});
""",
            ],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception(f"轉換失敗: {result.stderr}")

    except Exception as e:
        raise Exception(f"轉換過程出錯: {str(e)}")


def batch_convert_to_avif(input_dir, output_dir, quality=80, speed=6, concurrent=4):
    """批量轉換目錄中的圖片到AVIF"""
    try:
        script_dir = Path(__file__).parent
        converter_path = script_dir / "src" / "batch.js"

        # 使用Node.js批量轉換器
        result = subprocess.run(
            [
                "node",
                "-e",
                f"""
import {{ batchConvert }} from '{converter_path}';
import {{ fileURLToPath }} from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__dirname);

batchConvert('{input_dir}', '{output_dir}', {{
    quality: {quality},
    speed: {speed},
    concurrent: {concurrent}
}}).then(result => {{
    console.log(JSON.stringify(result));
}}).catch(error => {{
    console.error('Error:', error.message);
    process.exit(1);
}});
""",
            ],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception(f"批量轉換失敗: {result.stderr}")

    except Exception as e:
        raise Exception(f"批量轉換過程出錯: {str(e)}")


def get_image_info(image_path):
    """獲取圖片基本信息"""
    try:
        # 使用Python的PIL庫獲取圖片信息
        try:
            from PIL import Image
        except ImportError:
            return {"error": "PIL庫未安裝"}

        import os

        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": os.path.getsize(image_path),
                "size_mb": os.path.getsize(image_path) / (1024 * 1024),
            }
    except Exception as e:
        return {"error": str(e)}
