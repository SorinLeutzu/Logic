import tkinter as tk
from tkinter import messagebox
import subprocess
import shutil

def generate_mace4_code(height_relationships):
  
    individuals = set()
    for taller, shorter in height_relationships:
        individuals.add(taller)
        individuals.add(shorter)
    
    mace4_code = []
    mace4_code.append("% Define individuals")
    mace4_code.append("formulas(assumptions).")
    
   
    individuals = sorted(individuals)  
    for i, person1 in enumerate(individuals):
        for person2 in individuals[i + 1:]:
            mace4_code.append(f"    {person1} != {person2}.")

    # dding asymmetry and irreflexivity constraints for 'taller'
    mace4_code.append("\n    % Define taller relationship as asymmetric and irreflexive")
    mace4_code.append("    all x ( -taller(x, x) ). % No one is taller than themselves")
    mace4_code.append("    all x all y ( taller(x, y) -> -taller(y, x) ). % If x is taller than y, y cannot be taller than x")
    
    # adding constraints
    mace4_code.append("\n    % Problem constraints")
    for taller, shorter in height_relationships:
        mace4_code.append(f"    taller({taller}, {shorter}).")
    
    mace4_code.append("end_of_list.\n")
  
   
    mace4_code.append("formulas(goals).")
    mace4_code.append("    % Find the shortest person")
    mace4_code.append("    exists x ( all y ( y != x -> taller(y, x) ) ). % x is the shortest if everyone else is taller than x")
    mace4_code.append("end_of_list.")
    
    # writing the mace4 code to the input  file
    with open("heights.in", "w") as file:
        file.write("\n".join(mace4_code))


def extract_model_section(file_path):
    try:
        with open(file_path, 'r') as file:
           
            lines = file.readlines()
            in_model_section = False
            model_lines = []

            for line in lines:
                if "MODEL" in line:
                    in_model_section = True
                elif "end of model" in line and in_model_section:
                    break
                if in_model_section:
                    model_lines.append(line.strip())

            return "\n".join(model_lines)
    except FileNotFoundError:
        return f"Error: The file {file_path} does not exist."

class HeightRelationshipsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Height Relationships")
        
        self.num_people = tk.IntVar()
        self.people = []
        self.height_relationships = []
        
        self.init_gui()
    
    def init_gui(self):
        tk.Label(self.root, text="Enter number of people:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.num_people).grid(row=0, column=1)
        tk.Button(self.root, text="Submit", command=self.set_people_count).grid(row=0, column=2)
        
        self.name_frame = tk.Frame(self.root)
        self.name_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.relationship_frame = tk.Frame(self.root)
        self.relationship_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.relationship_list_frame = tk.Frame(self.root)
        self.relationship_list_frame.grid(row=3, column=0, columnspan=3, pady=10)
    
    def set_people_count(self):
        count = self.num_people.get()
        if count <= 0:
            messagebox.showerror("Error", "Please enter a valid number of people.")
            return
        
        self.people = [tk.StringVar() for _ in range(count)]
        
        tk.Label(self.name_frame, text="Enter Names:").grid(row=0, column=0, columnspan=3)
        for i in range(count):
            tk.Label(self.name_frame, text=f"Person {i + 1}:").grid(row=i + 1, column=0)
            tk.Entry(self.name_frame, textvariable=self.people[i]).grid(row=i + 1, column=1)
        
        tk.Button(self.name_frame, text="Add Relationships", command=self.set_relationships).grid(row=count + 1, column=0, columnspan=3, pady=10)
    
    def set_relationships(self):
        names = [person.get() for person in self.people]
        if any(not name for name in names):
            messagebox.showerror("Error", "Please fill in all names.")
            return
        
        self.relationship_frame.destroy()
        self.relationship_frame = tk.Frame(self.root)
        self.relationship_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.taller_var = tk.StringVar()
        self.shorter_var = tk.StringVar()
        
        tk.Label(self.relationship_frame, text="Add Height Relationships:").grid(row=0, column=0, columnspan=3)
        tk.OptionMenu(self.relationship_frame, self.taller_var, *names).grid(row=1, column=0)
        tk.Label(self.relationship_frame, text="is taller than").grid(row=1, column=1)
        tk.OptionMenu(self.relationship_frame, self.shorter_var, *names).grid(row=1, column=2)
        
        tk.Button(self.relationship_frame, text="Add Relationship", command=self.add_relationship).grid(row=2, column=0, columnspan=3, pady=5)
        tk.Button(self.relationship_frame, text="Check using Mace4", command=self.check_with_mace4).grid(row=3, column=0, columnspan=3, pady=5)
        
        self.update_relationship_list()
    
    def add_relationship(self):
        taller = self.taller_var.get()
        shorter = self.shorter_var.get()
        
        if not taller or not shorter:
            messagebox.showerror("Error", "Please select both names.")
            return
        if taller == shorter:
            messagebox.showerror("Error", "A person cannot be taller than themselves.")
            return
        
        self.height_relationships.append((taller, shorter))
        self.update_relationship_list()
    
    def update_relationship_list(self):
        for widget in self.relationship_list_frame.winfo_children():
            widget.destroy()
        tk.Label(self.relationship_list_frame, text="Current height relationships:").grid(row=0, column=0, columnspan=3)
        for i, (taller, shorter) in enumerate(self.height_relationships):
            tk.Label(self.relationship_list_frame, text=f"{taller} is taller than {shorter}").grid(row=i + 1, column=0, columnspan=3)
    
    

    def check_with_mace4(self):
        if not self.height_relationships:
            messagebox.showerror("Error", "Please add at least one height relationship.")
            return

        generate_mace4_code(self.height_relationships)

        try:
          
            mace4_command = shutil.which("mace4")
            if mace4_command is None:
              
                result = subprocess.run(
                    ["bash", "-i", "-c", "alias mace4"],
                    text=True,
                    capture_output=True,
                    check=True,
                )
                alias_output = result.stdout.strip()
                if alias_output.startswith("alias mace4="):
            
                    mace4_command = alias_output.split("=", 1)[1].strip("'\"")
                else:
                    raise FileNotFoundError("Could not resolve alias for mace4.")
            
          
            with open("heights.out", "w") as output_file:
                subprocess.run(
                    [mace4_command, "-f", "heights.in"],
                    text=True,
                    stdout=output_file,
                    stderr=subprocess.STDOUT,
                    check=True,
                )

            
            with open("heights.out", "r") as output_file:
                output = output_file.read()
        except FileNotFoundError:
            messagebox.showerror("Error", "Mace4 is not installed or not found.")
            return
        except subprocess.CalledProcessError as e:
            f"Error occurred:\n{e.stderr}"

        # display the result in a separate window
        result_window = tk.Toplevel(self.root)
        result_window.title("Mace4 result")
        tk.Label(result_window, text="Mace4 output:").pack()
        text_widget = tk.Text(result_window, wrap=tk.WORD, height=20, width=80)
        text_widget.pack()
        text_widget.insert(tk.END,output )
        text_widget.config(state=tk.DISABLED)



if __name__ == "__main__":
    root = tk.Tk()
    app = HeightRelationshipsApp(root)
    root.mainloop()