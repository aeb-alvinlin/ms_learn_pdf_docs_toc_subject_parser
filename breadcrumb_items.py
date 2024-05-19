import fitz  # PyMuPDF
import json
import base64
import pickle
import os


src_pdf = 'azure-azure-functions (中文).pdf'


class Base64Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('ascii')
        return json.JSONEncoder.default(self, o)


def extract_toc(pdf_path):
    """
    Extract the Table of Contents (TOC) from a PDF file.
    """
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return toc


def extract_titles(pdf_path):
    """
    Extract titles from the PDF file.
    This is a simplified version and might need more complex logic based on your PDF structure.
    """

    titles = {}
    paragraphs = {}
    x_origin = None
    y_origin = None
    x = None
    y = None
    code_mode = False
    line_mode = False
    chapter_digit = 0
    paragraph_text = ''

    doc = fitz.open(absolute_pdf)
    total_page_count = doc.page_count
    start_page = 0
    end_page = total_page_count

    for page_number in range(end_page):
        if page_number % 10 == 0:
            print('\npage:', page_number + 1, end='')
        else:
            print('-', end='')
        try:
            data = doc[page_number].get_text('dict')
        except Exception as e:
            print(f'第 {page_number + 1} 頁錯誤 {e}')
            continue

        previous_number = None

        if isinstance(data, dict):
            if 'blocks' in data:
                data = data.get('blocks')

        if isinstance(data, list):
            previous_origin = None
            for counter, each_block in enumerate(data):
                number = each_block.get('number')
                type = each_block.get('type')
                bbox = each_block.get('bbox')
                lines = each_block.get('lines')

                if lines:
                    for each_line in lines:
                        l_spans = each_line.get('spans')
                        l_wmode = each_line.get('wmode')
                        l_dir = each_line.get('dir')
                        l_bbox = each_line.get('bbox')

                        for each_span in l_spans:
                            if not isinstance(each_span, dict):
                                continue
                            size = int(each_span.get('size'))
                            flags = each_span.get('flags')
                            font = each_span.get('font')
                            color = each_span.get('color')
                            ascender = each_span.get('ascender')
                            tdescender = each_span.get('descender')
                            origin = each_span.get('origin')
                            bbox = each_span.get('bbox')
                            span_text = each_span.get('text')
                            if (flags == 16) and size in [25]:
                                if not page_number in paragraphs:
                                    paragraphs[page_number] = []
                                if not number in paragraphs[page_number]:
                                    paragraphs[page_number].append(number)

        if paragraphs.get(page_number):
            titles[page_number + 1] = ''
            try:
                block_data = doc[page_number].get_text('blocks')
            except Exception as e:
                print(f'{page_number} 頁, block_data 錯誤 {e}')
                continue
            for block_number in paragraphs[page_number]:
                try:
                    titles[page_number + 1] += block_data[block_number][4].replace('\n', '') + '\n'
                except Exception as e:
                    print(f'{page_number + 1} 頁, f_out 錯誤 {e}')
                    continue
    return titles


proj_src = r'./.pdf_analyze_files'
src_pdf_path = '.pdf_source_files'
proj_folder = os.getcwd()
pdf_file = os.path.join(proj_src, src_pdf_path, src_pdf)
absolute_pdf = os.path.abspath(pdf_file)
base_name = os.path.basename(absolute_pdf)
pdf_name, pdf_ext = os.path.splitext(base_name)
tar_path = os.path.join(proj_src, f'{pdf_name}_[分析]')
if not os.path.isdir(tar_path):
    os.makedirs(tar_path)
# 将树状结构保存到文件
# Load or Extract TOC from the PDF
toc_pickle = os.path.join(tar_path, f'{base_name}_toc.pickle')
if os.path.isfile(toc_pickle):
    with open(toc_pickle, 'rb') as toc_f:
        toc = pickle.load(toc_f)
else:
    toc = extract_toc(absolute_pdf)
    with open(toc_pickle, 'wb') as toc_f:
        pickle.dump(toc, toc_f)

# 建立一個方便尋找頁數標題的字典
titles_pickle = os.path.join(tar_path, f'{base_name}_titles.pickle')
if os.path.isfile(titles_pickle):
    with open(titles_pickle, 'rb') as titles_f:
        titles = pickle.load(titles_f)
else:
    titles = extract_titles(absolute_pdf)
    with open(titles_pickle, 'wb') as titles_f:
        pickle.dump(titles, titles_f)

# 儲存當前的路徑
current_path = []

# 生成最終的結果列表
result = []

# 遍歷 TOC 生成樹狀結構
for item in toc:
    indent, title, page_number = item

    # 如果縮進比當前路徑的長度小或相等，修剪路徑
    if indent <= len(current_path):
        current_path = current_path[:indent -1]

    # 新增當前標題到路徑中
    current_path.append(title)

    # 如果 page_number 不等於 -1，則生成結果行
    if page_number != -1:
        breadcrumb = ' > '.join(current_path)
        result.append(f"** {breadcrumb} **\n  [{page_number}] {titles.get(page_number, title)}")

# 輸出結果
output_file_path = os.path.join(tar_path, f'{pdf_name}_breadcrumb.txt')
with open(output_file_path, 'w', encoding='utf-8') as f:
    for line in result:
        f.write(line)


print(f"Tree structure saved to {output_file_path}")