import os
import datetime
import re
import json
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

def analyze_site(directory):
    result = {}
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, directory)
        if relative_path == '.':
            relative_path = ''
        result[relative_path] = {
            'type': 'directory',
            'contents': {}
        }
        for file in files:
            file_path = os.path.join(root, file)
            file_stats = os.stat(file_path)
            file_info = {
                'type': 'file',
                'size': file_stats.st_size,
                'extension': os.path.splitext(file)[1],
                'modified': datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'created': datetime.datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'permissions': oct(file_stats.st_mode)[-3:],
                'hash': calculate_file_hash(file_path)
            }
            
            if file.endswith(('.php', '.html', '.js', '.css')):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    file_info['content'] = content
                    file_info['line_count'] = len(content.split('\n'))
                    
                    if file.endswith('.php'):
                        file_info['functions'] = extract_php_functions(content)
                        file_info['classes'] = extract_php_classes(content)
                        file_info['includes'] = extract_php_includes(content)
                    elif file.endswith('.html'):
                        file_info['title'] = extract_html_title(content)
                        file_info['meta_tags'] = extract_html_meta_tags(content)
                    elif file.endswith('.js'):
                        file_info['functions'] = extract_js_functions(content)
                        file_info['variables'] = extract_js_variables(content)
                    elif file.endswith('.css'):
                        file_info['selectors'] = extract_css_selectors(content)
                        file_info['properties'] = extract_css_properties(content)

            result[relative_path]['contents'][file] = file_info
    return result

def calculate_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def extract_php_functions(content):
    return re.findall(r'function\s+(\w+)\s*\(', content)

def extract_php_classes(content):
    return re.findall(r'class\s+(\w+)', content)

def extract_php_includes(content):
    return re.findall(r'(include|require|include_once|require_once)\s+[\'"](.+?)[\'"]', content)

def extract_html_title(content):
    title = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    return title.group(1) if title else 'No title found'

def extract_html_meta_tags(content):
    return re.findall(r'<meta\s+(.+?)>', content, re.IGNORECASE)

def extract_js_functions(content):
    return re.findall(r'function\s+(\w+)\s*\(', content)

def extract_js_variables(content):
    return re.findall(r'(var|let|const)\s+(\w+)\s*=', content)

def extract_css_selectors(content):
    return re.findall(r'([^\s,{]+)\s*{', content)

def extract_css_properties(content):
    return re.findall(r'(\S+)\s*:\s*([^;]+);', content)

def generate_ai_prompts(analysis, output_dir):
    prompts = {
        "general": "This JSON file contains a detailed analysis of a web project. Use this information to understand the structure and content of the project.",
        "chatgpt.3.5": "You are ChatGPT 3.5, an AI assistant analyzing a web project. Use the provided JSON data to answer questions about the project's structure, file contents, and characteristics.",
        "chatgpt.4": "You are ChatGPT 4, an advanced AI assistant analyzing a web project. Use the provided JSON data to answer questions about the project's structure, file contents, and characteristics.",
        "claude.2": "As Claude 2, an AI assistant, your task is to analyze this web project data and provide insights on its architecture, code patterns, and potential improvements.",
        "claude.3": "As Claude 3, an advanced AI assistant, your task is to analyze this web project data and provide detailed insights on its architecture, code patterns, and potential improvements.",
        "tabnine": "You are Tabnine, an AI code assistant. Use this project analysis to help with code completion, suggesting best practices, and identifying potential issues in the codebase."
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    for ai, prompt in prompts.items():
        analysis['ai_prompt'] = prompt
        output_file = os.path.join(output_dir, f'site_analysis_{ai}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"Analysis for {ai} saved to '{output_file}'")

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class SiteAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Site Analyzer")
        master.geometry("800x600")
        master.configure(bg='#f0f0f0')

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Select directory to analyze:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.directory_entry = ttk.Entry(input_frame, width=50)
        self.directory_entry.grid(row=1, column=0, sticky='ew')

        browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_directory)
        browse_button.grid(row=1, column=1, padx=(5, 0))

        analyze_button = ttk.Button(input_frame, text="Analyze", command=self.start_analysis)
        analyze_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.progress = ttk.Progressbar(input_frame, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky='ew')

        input_frame.columnconfigure(0, weight=1)

        # Filter section
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "PHP", "HTML", "CSS", "JavaScript"]
        filter_menu = ttk.OptionMenu(filter_frame, self.filter_var, "All", *filter_options, command=self.apply_filter)
        filter_menu.pack(side=tk.LEFT)

        # Tree view and output section
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(paned_window)
        paned_window.add(tree_frame, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('Type', 'Size'), show='tree headings')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Size', text='Size')
        self.tree.column('Type', width=100)
        self.tree.column('Size', width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        output_frame = ttk.Frame(paned_window)
        paned_window.add(output_frame, weight=1)

        self.output_text = ScrolledText(output_frame, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)

    def start_analysis(self):
        directory = self.directory_entry.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory to analyze.")
            return

        self.progress.start()
        self.master.after(100, lambda: self.run_analysis(directory))

    def run_analysis(self, directory):
        analysis = analyze_site(directory)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site_analysis_output')
        generate_ai_prompts(analysis, output_dir)

        self.progress.stop()
        self.display_output(output_dir)
        self.populate_tree(analysis)

    def display_output(self, output_dir):
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, f"Analysis complete!\n\n")
        self.output_text.insert(tk.END, f"Results saved to: {output_dir}\n\n")
        self.output_text.insert(tk.END, f"Files generated:\n")
        
        for file in os.listdir(output_dir):
            if file.endswith('.json'):
                self.output_text.insert(tk.END, f"- {file}\n")

        self.output_text.insert(tk.END, "\nAnalysis successful!")

    def populate_tree(self, analysis):
        self.tree.delete(*self.tree.get_children())
        self._recursive_populate(analysis, '')

    def _recursive_populate(self, data, parent):
        for name, info in data.items():
            if info['type'] == 'directory':
                folder = self.tree.insert(parent, 'end', text=name, values=('Directory', ''))
                self._recursive_populate(info['contents'], folder)
            elif info['type'] == 'file':
                self.tree.insert(parent, 'end', text=name, values=('File', f"{info['size']} bytes"))

    def apply_filter(self, *args):
        filter_value = self.filter_var.get()
        if filter_value == "All":
            self.tree.show('tree')
        else:
            self.tree.show('tree')
            extension = f".{filter_value.lower()}"
            for item in self.tree.get_children():
                self._filter_items(item, extension)

    def _filter_items(self, item, extension):
        children = self.tree.get_children(item)
        if not children:  # It's a file
            if not self.tree.item(item, 'text').endswith(extension):
                self.tree.detach(item)
        else:  # It's a directory
            for child in children:
                self._filter_items(child, extension)
            # Hide the directory if it has no visible children
            if not self.tree.get_children(item):
                self.tree.detach(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = SiteAnalyzerGUI(root)
    root.mainloop()
