import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from tkinter import filedialog
import json
import os

CONFIG_FILE = "config.json"

class HOI4SHM(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HOI4 SHM - Shine Maker for Hearts of Iron IV")
        self.iconphoto(False, tk.PhotoImage(file="logo.ico"))
        self.geometry("650x950")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Main")
        self.setup_main_tab()


    def setup_main_tab(self):
        self.tab1.grid_columnconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(1, weight=3)
        self.tab1.grid_rowconfigure(16, weight=1)
        pass

        self.labels = [
            "Name:", "Texture File:", "Effect File:", "Animation Texture File:", "Animation Rotation:",
            "Animation Looping (yes/no):", "Animation Time:", "Animation Delay:",
            "Rotation Offset X:", "Rotation Offset Y:", "Texture Scale X:", "Texture Scale Y:",
            "Animation Blend Mode:", "Animation Type:"
        ]
        self.default_values = [
            "", "gfx/interface/goals/xxx.png", "gfx/FX/xxx.lua", "gfx/interface/goals/xxx.dds", "",
            "", "", "", "", "", "", "", "add", "scrolling"
        ]

        self.entries = []
        self.shines_list = []

        self.load_config()

        for i, (label, default) in enumerate(zip(self.labels, self.default_values)):
            tk.Label(self.tab1, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            value = self.config_values.get(label[:-1], default)
            if label in ["Animation Blend Mode:", "Animation Type:"]:
                values = ["add", "multiply", "overlay"] if label == "Animation Blend Mode:" else ["scrolling", "rotating", "pulsing"]
                combobox = ttk.Combobox(self.tab1, values=values)
                combobox.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                combobox.set(value)
                self.entries.append(combobox)
            else:
                entry = tk.Entry(self.tab1)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                entry.insert(0, value)
                self.entries.append(entry)

        self.clear_fields_button = tk.Button(self.tab1, text="Clear fields", command=self.clear_fields)
        self.clear_fields_button.grid(row=14, columnspan=2, pady=10)

        self.generate_button = tk.Button(self.tab1, text="Generate Shine", command=self.generate_shine)
        self.generate_button.grid(row=15, columnspan=2, pady=10)

        editor_frame = tk.Frame(self.tab1)
        editor_frame.grid(row=16, columnspan=2, padx=10, pady=10, sticky='nsew')
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(1, weight=1)

        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                                    background="#1e1e1e", foreground="#858585", state='disabled')
        self.line_numbers.grid(row=0, column=0, sticky='ns')

        self.output_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD)
        self.output_text.grid(row=0, column=1, sticky='nsew')
        self.output_text.config(font=("Courier", 10), background="#1e1e1e", foreground="#dcdcdc", insertbackground="#ffffff")

        self.output_text.bind('<KeyRelease>', self.update_line_numbers)
        self.output_text.bind('<MouseWheel>', self.update_line_numbers)
        self.output_text.bind('<ButtonRelease-1>', self.update_line_numbers)
        self.output_text.bind('<KeyPress>', self.auto_close_brackets)
        self.output_text.bind('<Return>', self.auto_indent)

        self.context_menu = tk.Menu(self.tab1, tearoff=0)
        self.context_menu.add_command(label="Open in New Window", command=self.open_in_new_window)

        self.output_text.bind("<Button-3>", self.show_context_menu)

        self.copy_button = tk.Button(self.tab1, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.grid(row=17, columnspan=2, pady=10)

        self.clear_button = tk.Button(self.tab1, text="Clear content", command=self.clear_content)
        self.clear_button.grid(row=18, columnspan=2, pady=10)

        self.save_button = tk.Button(self.tab1, text="Create a file", command=self.save_to_file)
        self.save_button.grid(row=19, columnspan=2, pady=10)

        self.highlight_var = tk.BooleanVar(value=True)
        self.highlight_check = tk.Checkbutton(self.tab1, text="Syntax Highlighting", variable=self.highlight_var, command=self.toggle_syntax_highlighting)
        self.highlight_check.grid(row=20, columnspan=2, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.center_window()
        self.update_line_numbers()

        self.new_window = None
        self.syncing = False

    def auto_close_brackets(self, event):
        closing_brackets = {'(': ')', '{': '}', '[': ']', '"': '"', "'": "'"}
        char = event.char
        if char in closing_brackets:
            self.output_text.insert(tk.INSERT, closing_brackets[char])
            self.output_text.mark_set(tk.INSERT, f"{self.output_text.index(tk.INSERT)}-1c")
        self.update_line_numbers()

    def auto_indent(self, event):
        current_line = self.output_text.index(tk.INSERT).split('.')[0]
        line_content = self.output_text.get(f"{current_line}.0", f"{current_line}.end")
        indent = len(line_content) - len(line_content.lstrip())

        if line_content.strip().endswith(':') or line_content.strip().endswith('{'):
            indent += 4

        self.output_text.insert(tk.INSERT, '\n' + ' ' * indent)
        return None


    def update_line_numbers(self, event=None, text_widget=None, line_numbers=None):
        if not text_widget or not line_numbers:
            text_widget = self.output_text
            line_numbers = self.line_numbers

        line_numbers.config(state='normal')
        line_numbers.delete('1.0', tk.END)
        current_line = text_widget.index('@0,0').split('.')[0]
        while True:
            dline = text_widget.dlineinfo(f'{current_line}.0')
            if dline is None:
                break
            line_numbers.insert(tk.END, f'{current_line}\n')
            current_line = str(int(current_line) + 1)
        line_numbers.config(state='disabled')

    def toggle_syntax_highlighting(self):
        if self.highlight_var.get():
            self.apply_syntax_highlighting()
        else:
            self.clear_syntax_highlighting()

    def apply_syntax_highlighting(self, text_widget=None):
        if not text_widget:
            text_widget = self.output_text

        self.clear_syntax_highlighting(text_widget)

        keywords = ['SpriteType', 'name', 'texturefile', 'effectFile', 'animation', 'animationmaskfile',
                    'animationtexturefile', 'animationrotation', 'animationlooping', 'animationtime',
                    'animationdelay', 'animationblendmode', 'animationtype', 'animationrotationoffset',
                    'animationtexturescale', 'legacy_lazy_load']
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'

        text_widget.tag_configure("keyword", foreground="#569CD6")
        text_widget.tag_configure("string", foreground="#CE9178")
        text_widget.tag_configure("xy", foreground="#9A32CD")
        text_widget.tag_configure("value", foreground="#FFA500")
        text_widget.tag_configure("braces", foreground="#40E0D0")

        text = text_widget.get("1.0", tk.END)

        for keyword in keywords:
            start_idx = '1.0'
            while True:
                start_idx = text_widget.search(keyword, start_idx, tk.END, nocase=False, regexp=True)
                if not start_idx:
                    break
                end_idx = f'{start_idx}+{len(keyword)}c'
                text_widget.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

        start_idx = '1.0'
        while True:
            start_idx = text_widget.search(r'"[^"]*"', start_idx, tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f'{start_idx}+{len(text_widget.get(start_idx, tk.END).split("\n")[0])}c'
            text_widget.tag_add("string", start_idx, end_idx)
            start_idx = end_idx

        start_idx = '1.0'
        while True:
            start_idx = text_widget.search(r'\b\d+\b', start_idx, tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f'{start_idx}+{len(text_widget.get(start_idx, tk.END).split("\n")[0].split()[0])}c'
            text_widget.tag_add("value", start_idx, end_idx)
            start_idx = end_idx

        for brace in ['{', '}']:
            start_idx = '1.0'
            while True:
                start_idx = text_widget.search(brace, start_idx, tk.END)
                if not start_idx:
                    break
                end_idx = f'{start_idx}+1c'
                text_widget.tag_add("braces", start_idx, end_idx)
                start_idx = end_idx

    def clear_syntax_highlighting(self, text_widget=None):
        if not text_widget:
            text_widget = self.output_text

        text_widget.tag_remove("keyword", "1.0", tk.END)
        text_widget.tag_remove("string", "1.0", tk.END)
        text_widget.tag_remove("value", "1.0", tk.END)
        text_widget.tag_remove("braces", "1.0", tk.END)

    def open_in_new_window(self):
        if self.new_window:
            self.new_window.lift()
            return

        self.new_window = tk.Toplevel(self)
        self.new_window.title("Code Output")
        self.new_window.geometry("650x850")

        editor_frame = tk.Frame(self.new_window)
        editor_frame.pack(expand=True, fill=tk.BOTH)
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(1, weight=1)

        line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                               background="#1e1e1e", foreground="#858585", state='disabled')
        line_numbers.grid(row=0, column=0, sticky='ns')

        text_widget = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD)
        text_widget.grid(row=0, column=1, sticky='nsew')
        text_widget.insert(tk.END, self.output_text.get('1.0', tk.END))
        text_widget.config(font=("Courier", 10), background="#1e1e1e", foreground="#dcdcdc", insertbackground="#ffffff")

        text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(event, text_widget, line_numbers))
        text_widget.bind('<MouseWheel>', lambda event: self.update_line_numbers(event, text_widget, line_numbers))
        text_widget.bind('<ButtonRelease-1>', lambda event: self.update_line_numbers(event, text_widget, line_numbers))
        text_widget.bind('<KeyPress>', self.auto_close_brackets)
        text_widget.bind('<Return>', lambda event: self.auto_indent(event))

        text_widget.bind('<KeyRelease>', lambda event: self.sync_windows(text_widget))
        self.output_text.bind('<KeyRelease>', lambda event: self.sync_windows(self.output_text))

        if self.highlight_var.get():
            self.apply_syntax_highlighting(text_widget)

        self.update_line_numbers(text_widget=text_widget, line_numbers=line_numbers)

        self.new_window.protocol("WM_DELETE_WINDOW", self.close_new_window)

    def sync_windows(self, source_widget):
        if self.syncing:
            return

        try:
            self.syncing = True
            if source_widget == self.output_text:
                if self.new_window:
                    text_widget = self.new_window.children['!frame'].children['!scrolledtext']
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert(tk.END, self.output_text.get('1.0', tk.END))
                    self.apply_syntax_highlighting(text_widget)
            else:
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert(tk.END, source_widget.get('1.0', tk.END))
                self.apply_syntax_highlighting(self.output_text)
            self.update_line_numbers()
        finally:
            self.syncing = False

    def close_new_window(self):
        self.new_window.destroy()
        self.new_window = None

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_text.get("1.0", tk.END))
        messagebox.showinfo("Copied", "Content copied to clipboard!")

    def clear_content(self):
        confirm = messagebox.askokcancel("Confirm", "Are you sure you want to clear the content?")
        if confirm:
            self.output_text.delete("1.0", tk.END)

    def clear_fields(self):
        confirm = messagebox.askokcancel("Confirm", "Are you sure you want to clear all fields?")
        if confirm:
            for entry, default_value in zip(self.entries, self.default_values):
                entry.delete(0, tk.END)
                entry.insert(0, default_value)

    def save_to_file(self):
        file_content = self.output_text.get("1.0", tk.END)
        if not file_content.strip():
            messagebox.showwarning("Warning", "There is no content to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(file_content)
            messagebox.showinfo("Saved", f"Content saved to {file_path}")

    def generate_shine(self):
        name = self.entries[0].get()
        texturefile = self.entries[1].get()
        effectfile = self.entries[2].get()
        animationtexturefile = self.entries[3].get()
        animationrotation = self.entries[4].get()
        animationlooping = self.entries[5].get()
        animationtime = self.entries[6].get()
        animationdelay = self.entries[7].get()
        animationrotationoffset_x = self.entries[8].get()
        animationrotationoffset_y = self.entries[9].get()
        animationtexturescale_x = self.entries[10].get()
        animationtexturescale_y = self.entries[11].get()
        animationblendmode = self.entries[12].get()
        animationtype = self.entries[13].get()

        shine_code = f"""SpriteType {{
    name = "{name}"
    texturefile = "{texturefile}"
    effectFile = "{effectfile}"
    animation = {{
        animationmaskfile = "{animationtexturefile}"
        animationrotation = {animationrotation}
        animationlooping = {animationlooping}
        animationtime = {animationtime}
        animationdelay = {animationdelay}
        animationblendmode = "{animationblendmode}"
        animationtype = "{animationtype}"
        animationrotationoffset = {{
            x = {animationrotationoffset_x}
            y = {animationrotationoffset_y}
        }}
        animationtexturescale = {{
            x = {animationtexturescale_x}
            y = {animationtexturescale_y}
        }}
    }}
}}"""

        self.shines_list.append(shine_code)
        self.output_text.insert(tk.END, shine_code + "\n\n")
        self.update_line_numbers()

        if self.highlight_var.get():
            self.apply_syntax_highlighting()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                self.config_values = json.load(config_file)
        else:
            self.config_values = {}

    def save_config(self):
        for i, label in enumerate(self.labels):
            self.config_values[label[:-1]] = self.entries[i].get()
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(self.config_values, config_file)

    def on_closing(self):
        self.save_config()
        if self.new_window:
            self.new_window.destroy()
        self.destroy()

if __name__ == "__main__":
    app = HOI4SHM()
    app.mainloop()