import customtkinter as ctk
import sys
import os
import matplotlib.pyplot as plt
from PIL import Image
from customtkinter import filedialog
import time

# --- NEW: PDF Generation Imports ---
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
except ImportError:
    # --- FIX: Corrected print statements (fixes Pylance Error 1) ---
    print("--------------------" * 3)
    print("ERROR: 'reportlab' library not found.")
    print("Please install it by running: pip install reportlab")
    print("--------------------" * 3)
    sys.exit(1)


# --- Set the appearance (Dark/Light/System) ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Matplotlib (LaTeX) Renderer ---

# Configure matplotlib to use a dark background for our app
plt.rcParams.update({
    'text.color': 'white',
    'figure.facecolor': '#2b2b2b',  # Matches CustomTkinter's dark 'frame'
    'savefig.facecolor': '#2b2b2b', # Matches CustomTkinter's dark 'frame'
    'savefig.edgecolor': '#2b2b2b',
    'savefig.transparent': False,
})

def create_math_image(latex_str, img_name, font_size=16):
    """
    Renders a LaTeX string into a PNG image using matplotlib's mathtext.
    Returns the path to the created image.
    """
    try:
        # Add $...$ for mathtext
        full_latex_str = f"${latex_str}$"
        
        fig = plt.figure()
        # Add text to the figure
        fig.text(0.5, 0.5, full_latex_str,
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=font_size)
        
        # Save the figure, cropping to the text
        # Use a timestamp to ensure unique filenames
        unique_img_name = f"{img_name}_{time.time_ns()}.png"
        img_path = f"./{unique_img_name}"

        plt.savefig(img_path,
                    bbox_inches='tight',   # Crop whitespace
                    pad_inches=0.1,        # Add slight padding
                    dpi=300)               # High resolution
        plt.close(fig) # Close the figure to free memory
        return img_path
    
    except Exception as e:
        print(f"Error rendering LaTeX: {e}")
        return None

# --- Main Application ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Main Window Configuration ---
        self.title("Derivation Helper (LaTeX Edition)")
        self.geometry("800x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Store image references to prevent garbage collection
        self.image_references = []
        # --- Store temp image paths for cleanup ---
        self.temp_image_files = [] 

        # --- 1. Title Label ---
        self.title_label = ctk.CTkLabel(self, text="Dr Syed Tauseef's Derivation Helper",
                                        font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- 2. Input Frame ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.entries = {}
        # --- FIX: Use proper 'β' symbol in labels and constant values ---
        self.entries["Pr"] = self.create_input_row("Pr:", 0, "Pr", "0.71", "Enter Value")
        self.entries["y"] = self.create_input_row("y:", 1, "y", "", "Keep Constant")
        self.entries["beta"] = self.create_input_row("β:", 2, "β", "", "Keep Constant")
        self.entries["k1"] = self.create_input_row("k1(β):", 3, "k_1(β)", "2.5", "Enter Value")
        self.entries["k0"] = self.create_input_row("ko(β):", 4, "k_o(β)", "", "Keep Constant")

        # --- 3. Execute Button ---
        self.execute_button = ctk.CTkButton(self, text="Execute Derivation",
                                            font=ctk.CTkFont(size=16, weight="bold"),
                                            command=self.run_derivation)
        self.execute_button.grid(row=2, column=0, padx=20, pady=20)

        # --- 4. Output Scrollable Frame ---
        self.output_frame = ctk.CTkScrollableFrame(self, label_text="Derivation Steps", 
                                                   label_font=ctk.CTkFont(size=14, weight="bold"))
        self.output_frame.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.placeholder_label = ctk.CTkLabel(self.output_frame, 
                                              text="Your derivation steps will appear here...",
                                              font=ctk.CTkFont(size=14, slant="italic"),
                                              text_color="gray")
        self.placeholder_label.grid(row=0, column=0, padx=10, pady=10)

        # --- 5. Footer ---
        self.footer_label = ctk.CTkLabel(self, text="Licensed and author Dr Syed Tauseef",
                                         font=ctk.CTkFont(size=12))
        self.footer_label.grid(row=4, column=0, padx=20, pady=(10, 20))
        
        # --- NEW: Bind window close event to cleanup temp files ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Cleanup temp image files before closing the window."""
        self.cleanup_temp_files()
        self.destroy()

    def cleanup_temp_files(self):
        """Iterates and deletes all temporary image files."""
        for img_file in self.temp_image_files:
            try:
                if os.path.exists(img_file):
                    os.remove(img_file)
            except Exception as e:
                print(f"Warning: could not delete temp file {img_file}. Error: {e}")
        self.temp_image_files.clear()


    def create_input_row(self, label_text, row, const_val, entry_val, default_mode):
        label = ctk.CTkLabel(self.input_frame, text=label_text, 
                             font=ctk.CTkFont(size=14))
        label.grid(row=row, column=0, padx=(20, 10), pady=10, sticky="w")

        entry = ctk.CTkEntry(self.input_frame, font=ctk.CTkFont(size=14))
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        toggle = ctk.CTkSegmentedButton(self.input_frame,
                                        values=["Keep Constant", "Enter Value"],
                                        font=ctk.CTkFont(size=12),
                                        command=lambda mode, e=entry, cv=const_val: self.on_toggle(mode, e, cv))
        toggle.grid(row=row, column=2, padx=(10, 20), pady=10)
        
        toggle.set(default_mode)
        if default_mode == "Keep Constant":
            entry.insert(0, const_val)
            entry.configure(state="disabled")
        else:
            entry.insert(0, entry_val)
            entry.configure(state="normal")
            
        return entry

    def on_toggle(self, mode, entry_widget, const_val):
        if mode == "Keep Constant":
            entry_widget.configure(state="normal")
            entry_widget.delete(0, "end")
            entry_widget.insert(0, const_val)
            entry_widget.configure(state="disabled")
        else:
            entry_widget.configure(state="normal")
            entry_widget.delete(0, "end")

    def run_derivation(self):
        # 1. Clear old results
        for widget in self.output_frame.winfo_children():
            widget.destroy()
        
        # --- Clean up old temp images ---
        self.cleanup_temp_files()
        
        self.image_references.clear() # Clear old images

        # 2. Get all values
        # We use repr() to get a string '0.71' or "'Pr'"
        # Then we strip the outer quotes to get 0.71 or Pr
        pr = self.entries["Pr"].get().strip("'\"")
        y = self.entries["y"].get().strip("'\"")
        beta = self.entries["beta"].get().strip("'\"")
        k1 = self.entries["k1"].get().strip("'\"")
        k0 = self.entries["k0"].get().strip("'\"")

        # --- Store values for PDF function ---
        self.current_values = {"pr": pr, "y": y, "beta": beta, "k1": k1, "k0": k0}

        # 3. Generate derivation content (list of dicts)
        derivation_content = self.get_derivation_content(pr, y, beta, k1, k0)
        # --- Store content for PDF function ---
        self.current_derivation_content = derivation_content

        # --- 4. Add "Download PDF" button to the results frame ---
        self.pdf_button = ctk.CTkButton(self.output_frame, 
                                        text="Download PDF of Results",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        command=self.download_pdf)
        self.pdf_button.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")


        # 5. Add content to the scrollable frame
        row_counter = 1 # Start at row 1 (PDF button is at row 0)
        for item in derivation_content:
            if item["type"] == "text":
                font_size = item.get("size", 14)
                font_weight = item.get("weight", "normal")
                justify = item.get("justify", "left")
                pady = item.get("pady", (0, 10))

                label = ctk.CTkLabel(self.output_frame,
                                     text=item['content'],
                                     font=ctk.CTkFont(size=font_size, weight=font_weight),
                                     justify=justify,
                                     anchor="w")
                label.grid(row=row_counter, column=0, padx=10, pady=pady, sticky="w")
                row_counter += 1
            
            elif item["type"] == "latex":
                # Render the LaTeX string to an image file
                img_path = create_math_image(item["content"], f"temp_img_{row_counter}", item.get("size", 16))
                
                if img_path:
                    # --- Store temp file path for cleanup ---
                    self.temp_image_files.append(img_path)

                    # Open the image with PIL
                    pil_image = Image.open(img_path)
                    
                    # --- FIX: Resize image if it's too wide ---
                    # 800 (app) - 40 (frame pad) - 40 (img pad) - 20 (scrollbar) = 700
                    max_width = 700 
                    original_width, original_height = pil_image.size
                    
                    if original_width > max_width:
                        # Calculate new height to maintain aspect ratio
                        aspect_ratio = original_height / original_width
                        new_height = int(max_width * aspect_ratio)
                        new_size = (max_width, new_height)
                    else:
                        new_size = pil_image.size
                    # --- End of FIX ---

                    # Create a CTkImage with the (potentially) new size
                    ctk_image = ctk.CTkImage(light_image=pil_image, size=new_size)
                    
                    # Store reference
                    self.image_references.append(ctk_image)

                    # Create a label to display the image
                    img_label = ctk.CTkLabel(self.output_frame, image=ctk_image, text="")
                    img_label.grid(row=row_counter, column=0, padx=20, pady=10, sticky="w")
                    row_counter += 1
                    

    # --- Function to handle PDF Download ---
    def download_pdf(self):
        """Asks for a save location and generates a PDF of the results."""
        
        # 1. Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Save Derivation as PDF"
        )
        if not filename:
            return # User cancelled
            
        # 2. Get inputs and derivation content
        values = self.current_values
        derivation_content = self.current_derivation_content
        
        # 3. Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []
        
        # 4. Add Title
        story.append(Paragraph("Dr Syed Tauseef's Derivation Report", styles['h1']))
        story.append(Spacer(1, 0.25 * inch))
        
        # 5. Add Inputs
        story.append(Paragraph("Input Values", styles['h2']))
        story.append(Paragraph(f"Pr: {values['pr']}", styles['Normal']))
        story.append(Paragraph(f"y: {values['y']}", styles['Normal']))
        story.append(Paragraph(f"β: {values['beta']}", styles['Normal']))
        story.append(Paragraph(f"k1(β): {values['k1']}", styles['Normal']))
        story.append(Paragraph(f"ko(β): {values['k0']}", styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))

        # 6. Add Derivation Steps
        story.append(Paragraph("Derivation Steps", styles['h2']))
        
        temp_pdf_images = []
        try:
            for item in derivation_content:
                if item["type"] == "text":
                    # Convert bold/size to simple style
                    if item.get("weight") == "bold":
                        style = styles['h3']
                    else:
                        style = styles['Normal']
                    # Replace \n with <br/> for PDF paragraphs
                    text_content = item['content'].replace('\n', '<br/>')
                    story.append(Paragraph(text_content, style))
                    story.append(Spacer(1, 0.1 * inch))
                
                elif item["type"] == "latex":
                    # Create a new temp image just for the PDF
                    img_path = create_math_image(item["content"], f"temp_pdf_img", item.get("size", 16))
                    if img_path:
                        temp_pdf_images.append(img_path)
                        # Add image to PDF, scaling it to fit width
                        rl_img = ReportLabImage(img_path, width=6.5 * inch, height=None)
                        rl_img.drawHeight = rl_img.drawHeight * (6.5 * inch / rl_img.drawWidth) # Maintain aspect ratio
                        rl_img.drawWidth = 6.5 * inch
                        story.append(rl_img)
                        story.append(Spacer(1, 0.1 * inch))
            
            # 7. Build the PDF
            doc.build(story)

            # 8. Show "Saved!" message in the app
            saved_label = ctk.CTkLabel(self.output_frame,
                                       text=f"✔ Successfully saved to:\n{filename}",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color="green", anchor="w", justify="left")
            saved_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
            # Overwrite the button
            if hasattr(self, 'pdf_button'):
                self.pdf_button.grid_forget()
            
            # Make the "Saved!" message disappear after 5 seconds
            saved_label.after(5000, saved_label.destroy)

        except Exception as e:
            print(f"Error creating PDF: {e}")
            # Show error message
            error_label = ctk.CTkLabel(self.output_frame,
                                       text=f"Error creating PDF: {e}",
                                       text_color="red", anchor="w", justify="left")
            error_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        finally:
            # 9. Clean up all temp PDF images
            for img in temp_pdf_images:
                try:
                    if os.path.exists(img):
                        os.remove(img)
                except Exception as e:
                    print(f"Warning: could not delete temp_pdf file {img}. Error: {e}")


    def get_derivation_content(self, pr, y, beta, k1, k0):
        """
        Generates the derivation steps as a list of dicts.
        Each dict has a 'type' ('text' or 'latex') and 'content'.
        """
        
        # Helper to format values for LaTeX
        def f(val):
            try:
                # If it's a number, just return it as a string
                float(val)
                return val
            except ValueError:
                # It's a string.
                # Handle specific known constants
                if val == "β":
                    return r"\beta"
                if val == "k_1(β)":
                    return r"k_1(\beta)"
                if val == "k_o(β)":
                    return r"k_o(\beta)"
                
                # Handle general variables
                if val.isalpha() and len(val) > 1:
                    # e.g., "Pr" -> "\mathrm{Pr}"
                    return fr"\mathrm{{{val}}}"
                
                # Default: return the value as is (e.g., "y")
                return val

        # --- Define formatted variables *once* for clarity ---
        pr_val = f(pr)
        y_val = f(y)
        beta_val = f(beta)
        k1_val = f(k1)
        k0_val = f(k0)

        parts = []

        # --- Part 1: Eq (28) -> (29) ---
        parts.append({
            "type": "text", "content": f"Your specific Equation (28) is structured as:",
            "size": 15, "weight": "bold", "pady": (5, 5)
        })
        parts.append({
            "type": "latex",
            # --- FIX: Corrected KeyError (k0_k0_val -> k0) ---
            "content": r"\tilde{{\theta}}({y},s) = \frac{{1}}{{s}} \exp\left( -{y} \sqrt{{\frac{{ {pr} s^{{1-{beta}}} }}{{ {k1}/s + {k0} }} }} \right)".format(
                y=y_val, pr=pr_val, beta=beta_val, k1=k1_val, k0=k0_val
            ),
            "size": 20 # Larger font for main equations
        })
        
        # --- NEW: Add full Eq (29) ---
        parts.append({
            "type": "text", "content": "This is rearranged into the full series form (Eq 29):",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            # --- FIX: Denominator K!! -> K! l! ---
            "content": r"\tilde{{\theta}}(y,s) = \frac{{1}}{{s}} + \sum_{{K=1}}^{{\infty}} \sum_{{l=0}}^{{\infty}} \left[ \frac{{ ({pr})^{{K/2}} (-{y})^K (-1)^l ({k1})^l \Gamma(K/2 + l) }}{{ K! l! ({k0})^{{K/2 + l}} \Gamma(K/2) s^{{1 - (1-{beta})K/2 + l}} }} \right]".format(
                pr=pr_val, y=y_val, k1=k1_val, k0=k0_val, beta=beta_val
            ),
            "size": 20
        })

        # --- Part 2: Eq (29) -> (30) ---
        parts.append({
            "type": "text", "content": f"--- Step 2: Applying the Inverse Laplace Transform (Eq 30) ---",
            "size": 16, "weight": "bold", "pady": (20, 10)
        })
        parts.append({
            "type": "text", "content": "We apply the inverse Laplace transform (L⁻¹) to the general term inside the summation.\n"
                                      "The key rule we need is:", "pady": (0, 5)
        })
        parts.append({
            "type":"latex",
            "content": r"\mathcal{{L}}^{{-1}} \left\{ \frac{{1}}{{s^v}} \right\} = \frac{{t^{{v-1}}}}{{\Gamma(v)}}",
            "size": 18
        })
        parts.append({
            "type": "text", "content": "1. First, we identify the 'Constant Part' [C]:",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            # --- FIX: Denominator K!! -> K! l! ---
            "content": r"[C] = \frac{{ ({pr})^{{K/2}} (-{y})^K (-1)^l ({k1})^l \Gamma(K/2 + l) }}{{ K! l! ({k0})^{{K/2 + l}} \Gamma(K/2) }}".format(
                pr=pr_val, y=y_val, k1=k1_val, k0=k0_val
            ),
            "size": 18
        })
        parts.append({
            "type": "text", "content": "2. Next, we identify the 's-Part' and its exponent 'v':",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            "content": r"[s\text{{-Part}}] = \frac{{1}}{{s^{{1 - (1-{beta})K/2 + l}}}} \quad \Rightarrow \quad v = 1 - (1-{beta})K/2 + l".format(
                beta=beta_val
            ),
            "size": 18
        })
        parts.append({
            "type": "text", "content": "3. We apply the rule:",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            "content": r"v-1 = (1 - (1-{beta})K/2 + l) - 1 = l - (1-{beta})K/2".format(
                beta=beta_val
            ),
            "size": 18
        })
        parts.append({
            "type": "latex",
            "content": r"\Gamma(v) = \Gamma(1 - (1-{beta})K/2 + l)".format(
                beta=beta_val
            ),
            "size": 18
        })
        parts.append({
            "type": "text", "content": "4. Re-assembling the term [C] * t^(v-1) / Γ(v):",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            # --- FIX 1: Denominator K!! -> K! l! ---
            # --- FIX 2: Exponent t^(l + ...) -> t^(l - ...) ---
            "content": r"\frac{{[C] \cdot t^{{v-1}}}}{{\Gamma(v)}} = \frac{{ ({pr})^{{K/2}} (-{y})^K (-1)^l ({k1})^l \Gamma(K/2 + l) t^{{l - (1-{beta})K/2}} }}{{ K! l! ({k0})^{{K/2 + l}} \Gamma(K/2) \Gamma(1 - (1-{beta})K/2 + l) }}".format(
                pr=pr_val, y=y_val, k1=k1_val, k0=k0_val, beta=beta_val
            ),
            "size": 20
        })
        
        # --- NEW: Add the full Eq (30) ---
        parts.append({
            "type": "text", "content": "5. Finally, placing this back into the full solution (Eq 30):",
            "size": 15, "weight": "bold", "pady": (10, 5)
        })
        parts.append({
            "type": "latex",
            # --- FIX 1: Denominator K!! -> K! l! ---
            # --- FIX 2: Exponent t^(l + ...) -> t^(l - ...) ---
            "content": r"\theta(y,t) = 1 + \sum_{{K=1}}^{{\infty}} \sum_{{l=0}}^{{\infty}} \left[ \frac{{ ({pr})^{{K/2}} (-{y})^K (-1)^l ({k1})^l \Gamma(K/2 + l) t^{{l - (1-{beta})K/2}} }}{{ K! l! ({k0})^{{K/2 + l}} \Gamma(K/2) \Gamma(1 - (1-{beta})K/2 + l) }} \right]".format(
                pr=pr_val, y=y_val, k1=k1_val, k0=k0_val, beta=beta_val
            ),
            "size": 20
        })

        # --- NEW: Re-instated the note about the typo ---
        parts.append({
            "type": "text", "content": "--- NOTE ON MATH LOGIC (TYPO IN EQ 30) ---",
            "size": 16, "weight": "bold", "pady": (20, 10)
        })
        parts.append({
            # --- FIX: Pylance Error 2 (missing 'content' key) ---
            "type": "text",
            "content": "Our derivation for the exponent of 't' is (v-1) = l - (1-β)K/2. This follows the Laplace rule.\n"
                        "The paper's original Eq (30) shows the exponent as: l + (1-β)K/2.\n\n"
                        "This is a common type of sign-flip typo in complex academic papers.",
            "justify": "left"
        })
        
        # --- NEW: Add note about the k1=0, k0=1 case ---
        parts.append({
            "type": "text", "content": "--- Note on Simplified Case (for Graphing) ---",
            "size": 16, "weight": "bold", "pady": (20, 10)
        })
        parts.append({
            "type": "text",
            "content": "You mentioned a simplified case for graphing where k1=0 and k0=1.\n"
                       "If we apply this to Eq (28), the denominator (k1/s + k0) becomes 1.\n"
                       "This simplifies the entire problem *before* the series expansion,\n"
                       "leading to a different, simpler solution (not a double summation).",
            "justify": "left"
        })
        
        parts.append({
            "type": "text", "content": "Derivation Complete!",
            "size": 16, "weight": "bold", "pady": (20, 20), "justify": "center"
        })

        return parts

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram exited.")
        # Try to clean up on exit, though app object might not be fully init
        try:
            app.cleanup_temp_files()
        except NameError:
            pass # App not defined yet
        sys.exit(0)
# Trigger new build
