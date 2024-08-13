import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from tkinter import filedialog
from PIL import Image, ImageTk

class HOI4SHM(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HOI4 SHM - Shine Maker for Hearts of Iron IV")
        self.iconphoto(False, tk.PhotoImage(file="logo.ico"))

        self.geometry("650x850")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(16, weight=1)

        self.labels = [
            "Name:", "Texture File:", "Effect File:", "Animation Texture File:", "Animation Rotation:",
            "Animation Looping (yes/no):", "Animation Time:", "Animation Delay:",
            "Rotation Offset X:", "Rotation Offset Y:", "Texture Scale X:", "Texture Scale Y:",
            "Animation Blend Mode:", "Animation Type:", "Number of Shines:"
        ]
        self.default_values = [
            "", "gfx/interface/goals/xxx.png", "gfx/FX/xxx.lua", "gfx/interface/goals/xxx.dds", "",
            "", "", "", "", "", "", "", "add", "scrolling", "1"
        ]

        self.entries = []
        self.shines_list = []

        for i, (label, default) in enumerate(zip(self.labels, self.default_values)):
            tk.Label(self, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            if label in ["Animation Blend Mode:", "Animation Type:"]:
                values = ["add", "multiply", "overlay"] if label == "Animation Blend Mode:" else ["scrolling", "rotating", "pulsing"]
                combobox = ttk.Combobox(self, values=values)
                combobox.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                combobox.set(default)
                self.entries.append(combobox)
            else:
                entry = tk.Entry(self)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                entry.insert(0, default)
                self.entries.append(entry)

        self.generate_button = tk.Button(self, text="Generate Shine", command=self.generate_shine)
        self.generate_button.grid(row=15, columnspan=2, pady=10)

        self.output_text = scrolledtext.ScrolledText(self)
        self.output_text.grid(row=16, columnspan=2, padx=10, pady=10, sticky='nsew')

        self.copy_button = tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.grid(row=17, columnspan=2, pady=10)

        self.clear_button = tk.Button(self, text="Clear content", command=self.clear_content)
        self.clear_button.grid(row=18, columnspan=2, pady=10)

        self.save_button = tk.Button(self, text="Create a file", command=self.save_to_file)
        self.save_button.grid(row=19, columnspan=2, pady=10)

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def generate_shine(self):
        def get_value(widget):
            return widget.get() if widget.get() else "x"

        values = [get_value(entry) for entry in self.entries]
        name, texturefile, effectfile, anim_texturefile, rotation, looping, time, delay, rotation_offset_x, rotation_offset_y, texture_scale_x, texture_scale_y, blend_mode, animation_type, num_shines = values
        num_shines = int(num_shines)

        for _ in range(num_shines):
            sprite_type = f'''
    SpriteType = {{
        name = "{name}_shine"
        texturefile = "{texturefile}"
        effectFile = "{effectfile}"
        animation = {{
            animationmaskfile = "{texturefile}"
            animationtexturefile = "{anim_texturefile}"
            animationrotation = {rotation}
            animationlooping = {looping}
            animationtime = {time}
            animationdelay = {delay}
            animationblendmode = "{blend_mode}"
            animationtype = "{animation_type}"
            animationrotationoffset = {{ x = {rotation_offset_x} y = {rotation_offset_y} }}
            animationtexturescale = {{ x = {texture_scale_x} y = {texture_scale_y} }}
        }}
        
        animation = {{
            animationmaskfile = "{texturefile}"
            animationtexturefile = "{anim_texturefile}"
            animationrotation = {rotation}
            animationlooping = {looping}
            animationtime = {time}
            animationdelay = {delay}
            animationblendmode = "{blend_mode}"
            animationtype = "{animation_type}"
            animationrotationoffset = {{ x = {rotation_offset_x} y = {rotation_offset_y} }}
            animationtexturescale = {{ x = {texture_scale_x} y = {texture_scale_y} }}
        }}

        legacy_lazy_load = no
    }}
            '''
            self.output_text.insert(tk.END, sprite_type + "\n\n")
            self.shines_list.append(sprite_type)

        self.output_text.see(tk.END)

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_text.get("1.0", tk.END).strip())

    def clear_content(self):
        if len(self.shines_list) > 1:
            if not messagebox.askyesno("Confirmation", "Are you sure you want to clear the contents?"):
                return

        self.output_text.delete("1.0", tk.END)
        self.shines_list.clear()

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("spriteTypes = {\n")
                file.write("\n".join(self.shines_list))
                file.write("\n}")

if __name__ == "__main__":
    app = HOI4SHM()
    app.mainloop()
