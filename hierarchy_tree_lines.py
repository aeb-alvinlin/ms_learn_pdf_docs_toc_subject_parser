import os
import fitz
import json
import base64

src_pdf = 'semantic-kernel.pdf'


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


class TreeNode:
    def __init__(self, indent, title, page_number):
        self.indent = indent
        self.title = title
        self.page_number = page_number
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self, level=0, is_last=False, prefix=''):
        ret = prefix + ("└─ " if is_last else "├─ ") + self.title
        if self.page_number != -1:
            page_title = titles.get(self.page_number, "《沒有標題》\n")
            ret += f"\n{prefix}{'    ' if is_last else '│   '}[  {self.page_number}] - {page_title}"
        if self.children:
            ret += "\n"
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            ret += child.__str__(level + 1, is_last_child, child_prefix)
        return ret

def build_tree(toc):
    root = TreeNode(0, f"< {src_pdf} >", -1)
    stack = [root]

    for indent, title, page_number in toc:
        node = TreeNode(indent, title, page_number)
        while stack and stack[-1].indent >= indent:
            stack.pop()
        stack[-1].add_child(node)
        stack.append(node)

    return root


# 将树状结构保存到文件
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



x_origin = None
y_origin = None
x = None
y = None
code_mode = False
line_mode = False
chapter_digit = 0
paragraphs = {}
paragraph_text = ''

doc = fitz.open(absolute_pdf)
total_page_count = doc.page_count
start_page = 0
end_page = total_page_count
toc = doc.get_toc()
titles = {}

print()

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

# 将树状结构保存到文件
tree = build_tree(toc)
output_file_path = os.path.join(tar_path, f'{pdf_name}_tree_structure.txt')
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(str(tree))

print(f"Tree structure saved to {output_file_path}")
