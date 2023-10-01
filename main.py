import tkinter as tk
import webbrowser
from tkinter import ttk
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import sqlite3
from fpdf import FPDF
import os

# create a DB

conn = sqlite3.connect('recipe_book.db')
c = conn.cursor()

# create tables

c.execute(""" CREATE TABLE if not exists recipes (
    recipe_id INTEGER PRIMARY KEY, 
    recipe_name TEXT,
    chef_name TEXT, 
    time_needed INT,
    type_meal TEXT,
    gluten NUMERIC,
    lactose NUMERIC,
    egg NUMERIC,
    peanut NUMERIC,
    shellfish NUMERIC,
    sesame NUMERIC,
    fish NUMERIC,
    soya NUMERIC,
    vegan NUMERIC,
    vegetarian NUMERIC,
    pescetarian NUMERIC,
    preparation_steps TEXT, 
    recipe_image BLOB

)
""")

c.execute(""" CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT
)
""")

c.execute(""" INSERT INTO ingredients (
    ingredient 
    ) 
    VALUES 
    ("apples"), 
    ("oranges"), 
    ("bananas"), 
    ("milk"), 
    ("beef"), 
    ("eggs"), 
    ("rice"), 
    ("peppers"), 
    ("cabbage"), 
    ("potatoes"), 
    ("cucumbers"), 
    ("chocolate")
""")

c.execute(""" CREATE TABLE if not exists recipe_ingredients(
    ri_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INT, 
    ingredient_id INT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
)
""")

ingredients_query = """
SELECT ingredient 
FROM ingredients 
INNER JOIN recipe_ingredients ON ingredients.ingredient_id = recipe_ingredients.ingredient_id
WHERE recipe_ingredients.recipe_id = ?
"""

count_recipes_query = """
SELECT COUNT(recipe_id)
FROM recipes
"""

c.execute(count_recipes_query)
current_recipe_id = c.fetchone()[0]

get_all_query = """
SELECT * 
FROM recipes 
WHERE recipe_id = ?
"""

ingredients = []
c.execute('''SELECT * FROM ingredients''')
for row in c:
    ingredients.append(row)
ingredients_list_index = []
for i in range(0, len(ingredients)):
    ingredients_list_index.append(ingredients[i][0])
ingredients_list = []
for i in range(0, len(ingredients)):
    ingredients_list.append(ingredients[i][1])

conn.commit()

bgc = "#F4DEB3"
btn_color = "#FFC594"
active_btn_color = "#DEAA88"

root = tk.Tk()
root.title("Recipe Book")
root.geometry("850x650")
root.configure(background=bgc)


def clear_all():
    global picture_bool

    for ent in (entry_name_of_recipe, entry_name_chef, type_of_recipe):
        ent.delete(0, tk.END)

    txt_preparation.delete("1.0", tk.END)
    for allergen in (
            gluten_var, lactose_var, egg_var, peanut_var, shellfish_var, sesame_var, fish_var, soya_var, vegan_var,
            vegetarian_var, pescetarian_var):
        allergen.set(False)

    time_needed_var.set(30)
    ingredients_listbox.selection_clear(0, tk.END)
    type_of_recipe.current(0)
    lbl_recipe_picture.configure(image="")
    picture_bool = False


def confirm_clear_all():
    answer = tkinter.messagebox.askyesno(title="Confirmation",
                                         message="Are you sure you want to start over?")
    if answer:
        clear_all()


def save_recipe():
    global current_recipe_id
    current_recipe_id += 1

    data_insert_query = """INSERT INTO recipes 
    (recipe_id,
    recipe_name,
    chef_name, 
    time_needed,
    type_meal,  
    gluten, 
    lactose, 
    egg, 
    peanut, 
    shellfish, 
    sesame, 
    fish, 
    soya, 
    vegan, 
    vegetarian, 
    pescetarian, 
    preparation_steps, 
    recipe_image)
    VALUES
    (?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?, ?, ?, ? )
     """
    rec_name = (current_recipe_id,
                entry_name_of_recipe.get(), entry_name_chef.get(), time_needed_var.get(), type_of_recipe.get(),
                gluten_var.get(), lactose_var.get(),
                egg_var.get(), peanut_var.get(), shellfish_var.get(), sesame_var.get(), fish_var.get(),
                soya_var.get(),
                vegan_var.get(), vegetarian_var.get(), pescetarian_var.get(), txt_preparation.get("1.0", tk.END),
                picture_food)

    data_insert_tuple = rec_name

    c.execute(data_insert_query, data_insert_tuple)
    conn.commit()

    ing = ingredients_listbox.curselection()

    for el in ing:
        c.execute("INSERT INTO recipe_ingredients(recipe_id, ingredient_id) VALUES(?,?)", (current_recipe_id, el + 1))
        conn.commit()

    tkinter.messagebox.showinfo(title="Recipe saved", message="The recipe has been successfully saved.")


def confirm_save_recipe():
    if entry_name_of_recipe.get() and entry_name_chef.get() and txt_preparation.get("1.0",
                                                                                    tk.END) and picture_bool and ingredients_listbox.curselection():

        answer = tkinter.messagebox.askyesno(title="Confirmation",
                                             message="Are you sure you have nothing more to add to your recipe?")
        if answer:
            save_recipe()
    else:
        tkinter.messagebox.showerror("Error", "Please fill in all fields before saving the recipe.")


def display_recipe_book():

    if current_recipe_id < 1:
        tkinter.messagebox.showerror(title="No recipes available",
                                     message="The recipe book is currently empty. \nPlease enter a recipe and try again.")
    else:

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 40)

        pdf.cell(0, 20, 'My Recipe Book', 0, 1, 'C')
        pdf.ln(30)

        c.execute(count_recipes_query)
        recipe_count = c.fetchone()

        for index in range(0, recipe_count[0]):

            c.execute(get_all_query, (index + 1,))
            all_info = c.fetchall()
            field_names = [a[0] for a in c.description]

            pdf.add_page()

            # recipe name

            pdf.set_font('Arial', 'B', 25)
            pdf.cell(0, 20, all_info[0][1], 0, 1, 'C')

            # meal type anf chef's name
            pdf.set_font('Arial', '', 14)
            pdf.cell(0, 15, f"A {all_info[0][4]} recipe by {all_info[0][2]}", 0, 1, 'C')

            # save the image for the current recipe

            with open(f'filename{index}.PNG', 'wb') as food_picture_current:
                food_picture_current.write(all_info[0][-1])

            pdf.image(f'filename{index}.PNG', x=pdf.w - 150, y=None, w=100, h=100/1.5)
            os.remove(f'filename{index}.PNG')

            # time needed
            pdf.set_font('Arial', 'I', 12)

            pdf.cell(0, 15, f"Time needed: {all_info[0][3]} minutes", 0, 1, 'C')

            # find out which diet the recipe is suitable for
            meal_preferences = []
            for ind in range(-3, -6, -1):
                if all_info[0][ind]:
                    meal_preferences.append(field_names[ind])

            suitable = ", ".join(meal_preferences)

            if all_info[0][-3] or all_info[0][-4] or all_info[0][-5]:
                pdf.cell(0, 10, f"{all_info[0][1]} is suitable for people on a {suitable} diet.", 0, 1)

            # find out if the meal contains allergens
            allergens_in_meal = []
            for ind in range(5, 13):
                if all_info[0][ind]:
                    allergens_in_meal.append(field_names[ind])

            allergens = ", ".join(allergens_in_meal)

            if (all_info[0][5] or all_info[0][6] or all_info[0][7] or all_info[0][8] or all_info[0][9] or all_info[0][
                10] or all_info[0][11] or all_info[0][12]):
                pdf.cell(0, 10, f"This recipe contains the following allergens: {allergens}.", 0, 1)

            # get the ingredient list for each recipe

            pdf.set_font('Arial', '', 14)
            current_recipe_ingredients = []
            c.execute(ingredients_query, (index + 1,))

            for current_recipe_ingredient in c:
                current_recipe_ingredients.append(current_recipe_ingredient[0])

            ingredients_needed = ", ".join(current_recipe_ingredients)

            pdf.cell(0, 20, f"Ingredients needed: {ingredients_needed}.", 0, 1)

            # preparation steps

            pdf.multi_cell(0, 20, all_info[0][-2], 0, 1)



        pdf.output('my_recipe_book.pdf', 'F')
        path = 'my_recipe_book.pdf'
        webbrowser.open_new(path)


def upload_recipe_picture():
    global picture_food, picture_bool

    file_types = [("PNG", "*.png")]
    file_name = tk.filedialog.askopenfilename(filetypes=file_types)

    if not file_name:
        return
    else:
        img = Image.open(file_name).resize((225, 150))
        img = ImageTk.PhotoImage(img)
        lbl_recipe_picture.image = img
        lbl_recipe_picture["image"] = img

        picture_food = open(file_name, 'rb')
        picture_food = picture_food.read()

        if picture_food:
            picture_bool = True


recipe_frame = tk.Frame(root, background=bgc)
recipe_frame.pack()

lbl_heading = tk.Label(recipe_frame, text="Create your own recipe book", font=("Calibre", 25, "bold"), padx=10, pady=20,
                       background=bgc)
lbl_heading.grid(row=0, column=0, columnspan=4)

lbl_name_of_recipe = tk.Label(recipe_frame, text="Name of the recipe: ", font=("Calibre", 12), padx=10, pady=20,
                              background=bgc)
lbl_name_of_recipe.grid(row=1, column=0)

entry_name_of_recipe = tk.Entry(recipe_frame, font=("Calibre", 12))
entry_name_of_recipe.grid(row=1, column=1, padx=10, pady=20)

# time needed in minutes

lbl_time_needed = tk.Label(recipe_frame, text="Time needed (min): ", font=("Calibre", 12), padx=10, pady=20,
                           background=bgc)
lbl_time_needed.grid(row=1, column=2, padx=5, pady=5)

time_needed_var = tk.StringVar()
time_needed_var.set(30)
time_needed = tk.Spinbox(recipe_frame,
                         from_=0, to=180, textvariable=time_needed_var, font=("Calibre", 12), state="readonly")
time_needed.grid(row=1, column=3, padx=5, pady=5)

# chef's name
lbl_name_chef = tk.Label(recipe_frame, text="Chef\'s name: ", font=("Calibre", 12), padx=10, pady=20, background=bgc)
lbl_name_chef.grid(row=2, column=0)

entry_name_chef = tk.Entry(recipe_frame, font=("Calibre", 12))
entry_name_chef.grid(row=2, column=1, padx=10, pady=20)

# meal type

lbl_type_of_recipe = tk.Label(recipe_frame, text="What is the recipe for? ", font=("Calibre", 12), padx=10, pady=20,
                              background=bgc)
lbl_type_of_recipe.grid(row=2, column=2, padx=5, pady=5)

type_of_recipe = ttk.Combobox(recipe_frame, width=27, values=["main meal", "beverage", "dessert", "snack"],
                              state="readonly")
type_of_recipe.grid(row=2, column=3, padx=5, pady=5)
type_of_recipe.current(0)

# allergens
allergen_labelframe = tk.LabelFrame(recipe_frame, text="Allergens", font=("Calibre", 12), background=bgc)
allergen_labelframe.grid(row=3, column=0, padx=5, pady=5, columnspan=2, sticky="news")

gluten_var = tk.BooleanVar()
gluten_checkbox = tk.Checkbutton(allergen_labelframe, text="gluten", variable=gluten_var)
gluten_checkbox.grid(row=0, column=0)

lactose_var = tk.BooleanVar()
lactose_checkbox = tk.Checkbutton(allergen_labelframe, text="lactose", variable=lactose_var)
lactose_checkbox.grid(row=0, column=1)

egg_var = tk.BooleanVar()
egg_checkbox = tk.Checkbutton(allergen_labelframe, text="egg", variable=egg_var)
egg_checkbox.grid(row=0, column=2)

peanut_var = tk.BooleanVar()
peanut_checkbox = tk.Checkbutton(allergen_labelframe, text="peanut", variable=peanut_var)
peanut_checkbox.grid(row=0, column=3)

shellfish_var = tk.BooleanVar()
shellfish_checkbox = tk.Checkbutton(allergen_labelframe, text="shellfish", variable=shellfish_var)
shellfish_checkbox.grid(row=1, column=0)

sesame_var = tk.BooleanVar()
sesame_checkbox = tk.Checkbutton(allergen_labelframe, text="sesame", variable=sesame_var)
sesame_checkbox.grid(row=1, column=1)

fish_var = tk.BooleanVar()
fish_checkbox = tk.Checkbutton(allergen_labelframe, text="fish", variable=fish_var)
fish_checkbox.grid(row=1, column=2)

soya_var = tk.BooleanVar()
soya_checkbox = tk.Checkbutton(allergen_labelframe, text="soya", variable=soya_var)
soya_checkbox.grid(row=1, column=3)

# dietary preferences

meal_type_labelframe = tk.LabelFrame(recipe_frame, text="Meal type", font=("Calibre", 12), background=bgc)
meal_type_labelframe.grid(row=3, column=2, padx=5, pady=5, columnspan=2, sticky="news")

vegan_var = tk.BooleanVar()
vegan_checkbox = tk.Checkbutton(meal_type_labelframe, text="vegan", variable=vegan_var)
vegan_checkbox.grid(row=0, column=1)

vegetarian_var = tk.BooleanVar()
vegetarian_checkbox = tk.Checkbutton(meal_type_labelframe, text="vegetarian", variable=vegetarian_var)
vegetarian_checkbox.grid(row=0, column=2)

pescetarian_var = tk.BooleanVar()
pescetarian_checkbox = tk.Checkbutton(meal_type_labelframe, text="pescetarian", variable=pescetarian_var)
pescetarian_checkbox.grid(row=0, column=3)

for i in (
        gluten_checkbox, lactose_checkbox, egg_checkbox, peanut_checkbox, shellfish_checkbox, sesame_checkbox,
        fish_checkbox,
        soya_checkbox, vegan_checkbox,
        vegetarian_checkbox, pescetarian_checkbox):
    i.configure(onvalue=True,
                offvalue=False, font=("Calibre", 12), background=bgc, activebackground=active_btn_color)

# enter ingredients
lbl_ingredients = tk.Label(recipe_frame, text="Ingredients: ", font=("Calibre", 12), padx=10, pady=20, background=bgc)
lbl_ingredients.grid(row=4, column=0, padx=5, pady=5)

ingredients_listbox = tk.Listbox(recipe_frame, font=("Calibre", 12), height=5,
                                 selectmode='extended')
ingredients_listbox.grid(row=4, column=1, padx=5, pady=5)

for i in ingredients:
    ingredients_listbox.insert(i[0], i[1])

# enter preparation steps
lbl_preparation = tk.Label(recipe_frame, text="Preparation steps: ", font=("Calibre", 12), padx=10, pady=20,
                           background=bgc)
lbl_preparation.grid(row=4, column=2, padx=5, pady=5)

txt_preparation = tk.Text(recipe_frame, font=("Calibre", 12, "bold"), height=5, width=20)
txt_preparation.grid(row=4, column=3, padx=5, pady=5)

# upload a picture
picture_bool = False
lbl_recipe_picture = tk.Label(recipe_frame, font=("Calibre", 12), padx=10, pady=20,
                              background=bgc)
lbl_recipe_picture.grid(row=5, column=0, columnspan=2, rowspan=4, padx=5, pady=5, sticky="news")

btn_upload_picture = tk.Button(recipe_frame, text="Upload Picture", command=upload_recipe_picture,
                               font=("Calibre", 12, "bold"), background=btn_color, activebackground=active_btn_color)
btn_upload_picture.grid(row=5, column=2, columnspan=2, padx=5, pady=5, sticky="news")

# button clear

btn_clear = tk.Button(recipe_frame, text="Clear All", command=confirm_clear_all, font=("Calibre", 12, "bold"),
                      background=btn_color, activebackground=active_btn_color)
btn_clear.grid(row=6, column=2, columnspan=2, padx=5, pady=5, sticky="news")

# button save

btn_save = tk.Button(recipe_frame, text="Add Recipe", command=confirm_save_recipe, font=("Calibre", 12, "bold"),
                     background=btn_color, activebackground=active_btn_color)
btn_save.grid(row=7, column=2, columnspan=2, padx=5, pady=5, sticky="news")

# button view book
btn_view_book = tk.Button(recipe_frame, text="View Recipe Book", command=display_recipe_book,
                          font=("Calibre", 12, "bold"), background=btn_color, activebackground=active_btn_color)
btn_view_book.grid(row=8, column=2, columnspan=2, padx=5, pady=5, sticky="news")


root.mainloop()
