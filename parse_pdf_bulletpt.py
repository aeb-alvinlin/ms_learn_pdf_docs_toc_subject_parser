import os
import fitz
import json
import base64
import pickle


src_pdf = 'azure-ai-services-openai (中文).pdf'

class MSPDFParserAnalyzer:

    class Base64Encoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, bytes):
                return base64.b64encode(o).decode('ascii')
            return json.JSONEncoder.default(self, o)


    class TreeNode:
        def __init__(self, indent, title, page_number, titles):
            self.indent = indent
            self.title = title
            self.page_number = page_number
            self.children = []
            self.titles = titles


        def add_child(self, child):
            self.children.append(child)


        def __str__(self, level=0):
            line_feed = "  " * level + "- " + self.title
            if self.page_number != -1:
                title_text = self.titles.get(self.page_number, '')
                line_feed += f"\n  {' ' * (level * 2)}[{self.page_number}] {title_text}"
            if (not line_feed.endswith('\n')):
                line_feed += "\n"
            for child in self.children:
                line_feed += child.__str__(level + 1)
            return line_feed


    def __init__(self, src_pdf, proj_src='./.pdf_analyze_files', src_pdf_path='.pdf_source_files'):
        self.src_pdf = src_pdf
        self.proj_src = proj_src
        self.src_pdf_path = src_pdf_path
        self.proj_folder = os.getcwd()
        self.pdf_file = os.path.join(self.proj_src, self.src_pdf_path, self.src_pdf)
        self.absolute_pdf = os.path.abspath(self.pdf_file)
        self.base_name = os.path.basename(self.absolute_pdf)
        self.pdf_name, self.pdf_ext = os.path.splitext(self.base_name)
        self.tar_path = os.path.join(self.proj_src, f'{self.pdf_name}_[分析]')
        self.paragraphs_pickle = os.path.join(self.tar_path, f'__temp__{self.base_name}.pickle')
        self.output_file_path = os.path.join(self.tar_path, f'{self.pdf_name}_[段落].txt')
        self.doc = fitz.open(self.absolute_pdf)
        self.total_page_count = self.doc.page_count
        self.toc = self.doc.get_toc()
        self.titles = {}
        self.paragraphs = {}
        self.paragraph_text = ''
        self.create_output_directory()


    def create_output_directory(self):
        if not os.path.isdir(self.tar_path):
            os.makedirs(self.tar_path)


    def load_analyze_pages(self):
        if os.path.isfile(self.paragraphs_pickle):
            print(f'\n讀取已分析過的 {self.absolute_pdf} 段落...')
            with open(self.paragraphs_pickle, 'rb') as paragraphs_f:
                self.paragraphs = pickle.load(paragraphs_f)
        else:
            print(f'\n開始分析 {self.absolute_pdf} 段落...')
            for page_number in range(self.total_page_count):
                if page_number % 10 == 0:
                    print('\npage:', page_number + 1, end='')
                else:
                    print('-', end='')

                try:
                    data = self.doc[page_number].get_text('dict')
                except Exception as e:
                    print(f'第 {page_number + 1} 頁錯誤 {e}')
                    continue

                self.process_page(page_number, data)

            print(f' 已完成 {self.absolute_pdf} 段落分析！')
            print(f'儲存已分析的 {self.absolute_pdf} 段落。')
            with open(self.paragraphs_pickle, 'wb') as paragraphs_f:
                pickle.dump(self.paragraphs, paragraphs_f)


    def process_page(self, page_number, data):
        if isinstance(data, dict) and 'blocks' in data:
            data = data.get('blocks')

        if isinstance(data, list):
            for each_block in data:
                lines = each_block.get('lines')
                if lines:
                    for each_line in lines:
                        for each_span in each_line.get('spans', []):
                            self.process_span(page_number, each_span, each_block.get('number'))


    def process_span(self, page_number, each_span, block_number):
        if not isinstance(each_span, dict):
            return

        size = int(each_span.get('size'))
        flags = each_span.get('flags')
        span_text = each_span.get('text')

        if flags == 16 and size in [25]:
            if page_number not in self.paragraphs:
                self.paragraphs[page_number] = []
            if block_number not in self.paragraphs[page_number]:
                self.paragraphs[page_number].append(block_number)


    def extract_titles(self):
        for page_number, block_numbers in self.paragraphs.items():
            self.titles[page_number + 1] = ''
            try:
                block_data = self.doc[page_number].get_text('blocks')
            except Exception as e:
                print(f'{page_number} 頁, block_data 錯誤 {e}')
                continue

            for block_number in block_numbers:
                try:
                    self.titles[page_number + 1] += block_data[block_number][4].replace('\n', '') + '\n'
                except Exception as e:
                    print(f'{page_number + 1} 頁, extract_titles 錯誤 {e}')
                    continue

    def build_tree(self):
        root = self.TreeNode(0, f"---< {self.pdf_name}{self.pdf_ext} >---", -1, self.titles)
        stack = [root]

        for indent, title, page_number in self.toc:
            node = self.TreeNode(indent, title, page_number, self.titles)
            while stack and stack[-1].indent >= indent:
                stack.pop()
            stack[-1].add_child(node)
            stack.append(node)

        return root


    def print_tree(self):
        tree = self.build_tree()
        print(tree)

        with open(self.output_file_path, 'w', encoding='utf-8') as f:
            f.writelines(str(tree))

        print(f'檔案 {self.output_file_path} 段落分析已儲存。')


    def parse_analyze(self):
        self.load_analyze_pages()
        self.extract_titles()
        self.print_tree()


if __name__ == "__main__":
    #src_pdfs = os.listdir(r'E:\.ongoing_projects\.microsoft_pdf_analyze_files\.pdf_analyze_files\.pdf_source_files')
    #for src_pdf in src_pdfs:
    analyzer = MSPDFParserAnalyzer(src_pdf)
    analyzer.parse_analyze()
