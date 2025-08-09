# coding: utf-8
# Author: Gauthier Patin
# Licence: GNU GPL v3.0

####### IMPORT STATEMENTS #######

import pandas as pd
from pathlib import Path
from typing import Optional, Union
import json
import os
from ipywidgets import Layout
import ipywidgets as ipw
from IPython.display import display, clear_output
import re


####### GENERAL VARIABLES #######

style = {"description_width": "initial"}
config_file = Path(__file__).parent / 'db_config.json'


####### MSDB PACKAGE FUNCTIONS #######

def register_db_name(db_name:Optional[str] = None, db_path:Optional[str] = None, widgets:Optional[bool] = True):
    """Register the name and the folder location of databases in the db_config.json file. Use this function when you already have the database files on your computer but not registered inside the msdb package.

    Parameters
    ----------

    db_name : Optional[str], optional
        Name of the database that you wish to register, by default None

    db_path : Optional[str], optional
        The path of folder where the where the databases files are located, by default None

    widgets : Optional[bool], optional
        Whether to display widgets to register the database, by default True
        When False, you will have to pass in arguments for the db_name and db_path

    
    Returns
    -------
    ipywdigets or string
    If the parameter "widgets" is set to True, it will return several ipywidgets from which you you will be able to register the database. When "widgets" is set to False, it will automatically register the database and will return a string.
    """

    wg_path_folder = ipw.Text(
        description = 'Path folder',
        placeholder = 'Location of the databases folder on your computer',
        value = db_path,
        style = style, 
        layout=Layout(width="50%", height="30px"),
    )

    wg_name_db = ipw.Text(
        description = 'DB name',
        placeholder = "Enter a db name",
        value = db_name,        
        style = style,
        layout=Layout(width="20%", height="30px"),
    )        

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()


    def add_new_db(name,path):
        
        # check whether the path folder is valid
        if not Path(path).exists():
            with button_record_output:
                print(f'The path you entered {path} is not valid. Process aborted !')
            return 'invalid path'
        
        # Retrieve the config info
        config = get_config_file()

        # Existing databases
        databases = config["databases"]

        # Update config with user data
        databases[name] = {'path_folder': path}
        config['databases'] = databases

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    
    
    def button_record_pressed(b):
        """
        Save the databases info in the db_config.json file.
        """

        button_record_output.clear_output(wait=True)

        function = add_new_db(wg_name_db.value, wg_path_folder.value)

        if function != "invalid path":
            with button_record_output:
                print(f'Database info ({wg_name_db.value}) recorded in the db_config.json file.')
         

    if widgets:
        recording.on_click(button_record_pressed)

        display(ipw.VBox([wg_name_db, wg_path_folder]))
        display(ipw.HBox([recording, button_record_output]))

    else:
        return add_new_db(name=db_name, path=db_path)


def create_db(db_name:Optional[str] = None, path_folder:Optional[str] = None, widgets:Optional[bool] = True):
    """Create and register new databases. This function creates the database files inside the designated path_folder and it also registers the name of the database inside the db_config.json file.

    If you only want to register the database, use the `register_db_name` function.

    Parameters
    ----------
    db_name : Optional[str], optional
        Name of the database that will later be used to refer to the database files, by default None
    
    path_folder : Optional[str], optional
        Absolute path of the folder where the database files should be created, by default None
    
    widgets : Optional[bool], optional
        Whether to display widgets to create the database, by default True
        When False, you will have to pass in arguments for the name_db and path_folder

    
    Returns
    -------
    ipywdigets or string
    If the parameter "widgets" is set to True, it will return several ipywidgets from which you you will be able to create and register the database. When "widgets" is set to False, it will automatically create and register the database and will return a string.
    """

    # Define the python widgets

    wg_name_db = ipw.Text(
        description='Database Name',
        placeholder='Enter a name (without space)',
        value=db_name,
        layout=Layout(width="50%", height="30px"),
        style=style
    )

    wg_path_folder = ipw.Text(
        description='Folder location',
        value=path_folder,
        layout=Layout(width="50%", height="30px"),
        style=style
    )

    recording = ipw.Button(
        description='Create databases',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )        
            
    button_record_output = ipw.Output()

    # Define function to register the database in the config file
    def register_db(name_db, path_folder):
        
        with open(config_file, "r") as f:
            config = json.load(f)

        # Existing databases
        databases = config["databases"]

        # Update config with user data
        databases[name_db] = {'path_folder':path_folder}
        config['databases'] = databases            

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    
    # Define function to create the database files
    def create_db_files(path_folder):

        # Convert the path_folder to a Path object
        path_folder = Path(path_folder)

        # Create the project info file
        db_project = pd.DataFrame(columns=['project_id','institution','start_date','end_date','project_leader','co-researchers','keywords', 'methods'])            
        db_project.to_csv(path_folder / 'projects_info.csv', index=False)

        # Create the object info file
        db_object = pd.DataFrame(columns=['object_id','object_category','object_type','object_technique','object_title','object_name','object_creator','object_date','object_owner','object_material','support','colorants_name','binding','ratio','thickness_um','color','status','project_id', 'object_comment'])
        db_object.to_csv(path_folder / 'objects_info.csv', index=False)

        # Create several text files
        with open(path_folder / 'analytical_methods.txt', 'w') as f:                
            f.write("Macro-XRF\n")
            f.write("Raman\n")
            f.write("XRD\n")
            f.write("XRF\n")
                        
        with open(path_folder / 'devices.txt', 'w') as f:
            f.write('Id,name,description,process_function\n')
                
        with open(path_folder / 'white_standards.txt', 'w') as f:
            f.write('ID,description\n')            

        with open(path_folder / 'object_creators.txt', 'w') as f:
            f.write('surname,name')

        with open(path_folder / 'object_techniques.txt', 'w') as f:
            f.write("China ink\n")
            f.write("acrylinc\n")
            f.write("aquatinte\n")
            f.write("black ink\n")
            f.write("black pencil\n")
            f.write("chalk\n")
            f.write("charcoal\n")
            f.write("monotypie\n")
            f.write("dye\n")
            f.write("felt-tip ink\n")
            f.write("frescoe\n")
            f.write("gouache\n")
            f.write("ink\n")
            f.write("linoleum print\n")
            f.write("lithograh\n")
            f.write("mezzotinte\n")
            f.write("oil paint\n")
            f.write("pastel\n")
            f.write("tin-glazed\n")
            f.write("watercolor\n")
            f.write("wood block print\n")        

        with open(path_folder / 'object_types.txt', 'w') as f:            
            f.write("banknote\n")
            f.write("book\n")
            f.write("BWS\n")       
            f.write("ceramic\n")
            f.write("colorchart\n")
            f.write("drawing\n")
            f.write("notebook\n")
            f.write("paint-out\n")
            f.write("painting\n")
            f.write("photograph\n")
            f.write("print\n")
            f.write("sculpture\n")
            f.write("seals\n")
            f.write("spectralon\n")
            f.write("tapistry\n")
            f.write("textile\n")
            f.write("wallpainting\n")

        with open(path_folder / 'object_materials.txt', 'w') as f:
            f.write("blue paper\n")
            f.write("canvas\n")
            f.write("cardboard\n")
            f.write("ceramic\n")
            f.write("coloured paper\n")
            f.write("cotton\n")
            f.write("Japanese paper\n")
            f.write("none\n")
            f.write("opacity chart\n")
            f.write("paper\n")
            f.write("parchment\n")
            f.write("rag paper\n")
            f.write("stone\n")
            f.write("transparent paper\n")
            f.write("wax\n")
            f.write("wood\n")
            f.write("woodpulp paper\n")
            f.write("wool\n")            

        with open(path_folder / 'institutions.txt', 'w') as f:
            f.write('name,acronym')

        with open(path_folder / 'users_info.txt', 'w') as f:
            f.write('name,surname,initials')

    if widgets:
        # Define the function when pressing the button
        def button_record_pressed(b):
            """
            Create the databases.
            """

            button_record_output.clear_output(wait=True)           
            
            # Run the functions previously defined
            register_db(name_db=wg_name_db.value, path_folder=wg_path_folder.value)
            create_db_files(path_folder=wg_path_folder.value)    
                    
            # Print output messages
            with button_record_output:
                print(f'The database {wg_name_db.value} was created and recorded in the db_config.json file.')
                print(f'The database files have been created in the following folder: {wg_path_folder.value}')

            
        recording.on_click(button_record_pressed)

        display(ipw.VBox([wg_name_db,wg_path_folder]))
        display(ipw.HBox([recording, button_record_output]))

    else:

        # Stop the script if name_db is missing
        if db_name == None:
            print('Please enter a valid name_db value.')
            return
        
        # Stop the script if path_folder is missing
        if path_folder == None:
            print('Please enter a valid path_folder value.')
            return
        
        # Stop the script if the path_folder value is not valid
        if not Path(path_folder).exists():
            print('The path_folder that you entered is not valid. Make sure that the folder where you want to save your databases has been created.')
            return

        # Run the functions previously defined
        register_db(name_db=db_name, path_folder=path_folder)
        create_db_files(path_folder=path_folder) 

        # Print output messages
        print(f'The database {db_name} was created and recorded in the db_config.json file.')
        print(f'The database files have been created in the following folder: {path_folder}')


def get_config_file():
    """Retrieve the content of the db_config.json file, which contains information related to the databases that you created. The name and the folder path of each registered databases is stored in this json file.    

    
    Returns
    -------
    A dictionary
    It returns the content of the db_config.json file as a python dictionary object.
    """
    
    with open(config_file, 'r') as file:
            config = json.load(file)
            return config


def get_db_names():
    """Retrieve the names of the registered databases.
    
    No arguments is required.

    Returns
    -------
    List
    It returns the names of the registered databases as string inside a list.
    """

    config_file = Path(__file__).parent / 'db_config.json'

    with open(config_file, 'r') as file:
            config = json.load(file)
            db_names = list(config['databases'].keys())
            if len(db_names) > 0:
                return db_names
            else:
                print('No databases have been registered.')
                return None  


def delete_db(db_name:Optional[str] = None):
    """Remove a database from the db_config.json file. It does not delete the database files, you will have to manually delete these files.


    Parameters
    ----------
    db_name : Optional[str], optional
        Name of the database that you wish to delete, by default None
    
    
    Returns
    -------
    ipywdigets
    It returns ipywidget objects from which you can select the name of the database to be deleted and confirm its removal from the db_config.json file.
    """

    existing_db_names = get_db_names()

    if isinstance(db_name, str) and db_name not in existing_db_names:

        print(f'The db_name you entered ({db_name}) is not valid. The db_name parameter has been reassigned to None to allow you to select a database name from the ipywidget dropdown.')

        db_name = None

    
    wg_name_db = ipw.Dropdown(
        description = 'DB name',
        value = db_name,
        options = get_db_names(),
        style = style,
        layout=Layout(width="20%", height="30px"),
    )

    config_file = Path(__file__).parent / 'db_config.json'

    recording = ipw.Button(
        description='Delete DB',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()

    def button_record_pressed(b):
        """
        Delete the database info in the db_config.json file.
        """

        button_record_output.clear_output(wait=True)

        with open(config_file, "r") as f:
            config = json.load(f)

        # Existing databases
        databases = config["databases"]

        # Delete the database
        del databases[wg_name_db.value]        
        config['databases'] = databases            

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

            
        with button_record_output:
            print(f'Database info ({wg_name_db.value}) removed from the db_config.json file.')

    recording.on_click(button_record_pressed)

    display(ipw.VBox([wg_name_db]))
    display(ipw.HBox([recording, button_record_output]))


def update_db_folder(db_name:Optional[str] = None, path_folder:Optional[str] = None, widgets:Optional[bool] = True):
    """Modify the path_folder of an existing database registered in the db_config.json file. Select the database name and enter a new path_folder.

    Parameters
    ----------
    db_name : Optional[str], optional
        Name of the database for which the info will change, by default None

    path_folder : Optional[str], optional
        Location of the databases folder on your computer, by default None

    wdigets : Optional[bool], optional
        Whether to use the ipywidgets, by default True
        When False, it automatically modify the database info based on the given parameter values.

    Returns
    -------
    ipywdigets or string
    If the parameter "widgets" is set to True, it will return several ipywidgets from which you you will be able to update the path folder of the database files. When "widgets" is set to False, it will automatically update the folder and will return a string.
    """

    existing_db_names = get_config_file()['databases']

    if len(existing_db_names) == 0:
        db_names = []
    else:
        db_names = list(existing_db_names.keys())

    wg_path_folder = ipw.Text(
        description = 'Path folder',
        placeholder = 'Location of the databases folder on your computer',
        value = path_folder,
        style = style, 
        layout=Layout(width="50%", height="30px"),
    )

    wg_name_db = ipw.Combobox(
        description = 'DB name',
        placeholder = "Enter a db name",
        value = db_name,
        options = db_names,
        style = style,
        layout=Layout(width="20%", height="30px"),
    )        

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()
    

    if widgets:

        def button_record_pressed(b):
            """
            Save the databases info in the db_config.json file.
            """

            button_record_output.clear_output(wait=True)

            # check whether the path folder is valid
            if not Path(wg_path_folder.value).exists(): 
                with button_record_output:
                    print(f'The path you entered ({wg_path_folder.value}) is not valid. Make sure it exists. Process aborted !')
                return

            # open the config file
            with open(config_file, "r") as f:
                config = json.load(f)

            # Existing databases
            databases = config["databases"]

            # Update config with user data
            databases[wg_name_db.value] = {'path_folder':wg_path_folder.value}
            config['databases'] = databases            

            # Save the updated config back to the JSON file
            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)
                
            with button_record_output:
                print(f'The new path_folder ({wg_path_folder.value}) has been successfully recorded in the db_config.json file.')

            
        recording.on_click(button_record_pressed)

        display(ipw.VBox([wg_name_db, wg_path_folder]))
        display(ipw.HBox([recording, button_record_output]))

    else:

        # check whether the path folder is valid
        if not Path(wg_path_folder.value).exists():            
            print(f'The path you entered ({wg_path_folder.value}) is not valid. Make sure it exists. Process aborted !')
            return

        with open(config_file, "r") as f:
            config = json.load(f)

        # Existing databases
        databases = config["databases"]

        # Update config with user data
        databases[wg_name_db.value] = {'path_folder':wg_path_folder.value}
        config['databases'] = databases

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)


####### DB CLASS #######

class DB:

    def __init__(self, db_name:Optional[str] = None, config_file:Optional[str] = Path(__file__).parent / 'db_config.json') -> None:
        """Instantiate a DB class object.

        Parameters
        ----------

        db_name : Optional[str]
            Name of the databases, by default None
            When None, it retrieves the first databases info registered in the db_config.json file
        
        config_file : Optional[str|Path]
            Location of the configuration file, by default Path(__file__).parent/'db_config.json'
                
        """

        self.db_name = db_name       
        self.config_file = config_file

        # Check whether the db_config.json file exists
        self._init_config()                  

        # Check whether databases were created
        if len(get_config_file()['databases']) == 0:
            print('There are no databases registered. Create a database to start using the functions available through the DB class.')
            return None
        
        # Check whether the name_db value is valid or select the first registered database name
        existing_dbs = get_db_names()
        
        if db_name == None:
            self.db_name = get_db_names()[0]    # Select the first registered database name    
            
        elif self.db_name not in existing_dbs:
            print(f'The name_db value you entered ({self.db_name}) has not been registered. Please select a registered database name.')
            return
        
        self.folder_db = Path(get_config_file()['databases'][self.db_name]['path_folder'])

    
    def _init_config(self):
        """Check whether the db_config.json exists.
        """

        if not os.path.exists(self.config_file):
            print(f'The file {self.config_file} has been deleted ! Please re-install the msdb package.')
            return None
        
    
    def __repr__(self):
        return f'DB class - name = {self.db_name}  - folder = {self.folder_db}'

    
    def add_creators(self):
        """Record a new object creator in the object_creators.txt file
        """

        # Function to update the text file if the initials are unique
        def update_text_file(name, surname):            
                        
            df_creators = self.get_creators()
            df_creators = pd.concat([df_creators, pd.DataFrame(data=[name,surname], index=['name','surname']).T])
            df_creators = df_creators.sort_values(by='surname')
            df_creators.to_csv(self.folder_db/'object_creators.txt',index=False)
               
            print(f"Added: {surname}, {name}")

        # Define ipython widgets
        name_widget = ipw.Text(        
            value='',
            placeholder='Enter a name (optional)',
            description='Name', 
            style=style              
        )

        surname_widget = ipw.Text(        
            value='',
            placeholder='Enter a surname',
            description='Surname',    
            style=style         
        )

        recording = ipw.Button(
            description='Record creator',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
        

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the creator info in the objet_creators.txt file.
            """

            button_record_output.clear_output(wait=True)

            name = name_widget.value.strip()
            surname = surname_widget.value.strip()

            with button_record_output:

                if surname: # ensure the surname field is complete
                    update_text_file(name, surname)
                else:
                    
                    print("Please enter at least a surname.")


        recording.on_click(button_record_pressed)

        display(surname_widget,name_widget)
        display(ipw.HBox([recording, button_record_output]))


    def add_devices(self):
        """Record a new analytical device in the devices.txt file
        """

        # Function to update the text file if the initials are unique
        def update_text_file(id, name, description):  

            df_devices = self.get_devices()

            existing_devices = df_devices['ID'].values

            if id in existing_devices:
                print(f'The ID you entered ({id}) has already been attributed to another device:')   
                print(df_devices[df_devices['ID'] == id])  
                        
            else:
                df_devices = pd.concat([df_devices, pd.DataFrame(data=[id,name,description], index=['ID','name','description']).T])
                df_devices = df_devices.sort_values(by='ID')
                df_devices.to_csv(self.folder_db / 'devices.txt',index=False)
                
                print(f"Device added: {id}, {name}")

        # Define ipython widgets
        wg_id = ipw.Text(        
            value='',
            placeholder='Enter an ID',
            description='Device ID',  
            style=style,
            layout=Layout(width="40%", height="30px")             
        )

        wg_name = ipw.Text(        
            value='',
            placeholder='Enter name',
            description='Device name',
            style=style,
            layout=Layout(width="40%", height="30px")             
        )

        wg_description = ipw.Text(        
            value='',
            placeholder='Briefly describe the device purpose (Optional)',
            description='Device description',   
            style=style,
            layout=Layout(width="40%", height="30px")       
        )

        recording = ipw.Button(
            description='Record device',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
        

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the device info in the devices.txt file.
            """

            button_record_output.clear_output(wait=True)

            id = wg_id.value.strip()
            name = wg_name.value.strip()
            description = wg_description.value.strip()

            with button_record_output:
                
                if id and name: # ensure the id and name fields are complete
                    update_text_file(id, name, description)
                else:                    
                    print("Please enter at least an ID and a name.")


        recording.on_click(button_record_pressed)

        display(wg_id,wg_name,wg_description)
        display(ipw.HBox([recording, button_record_output]))


    def add_institutions(self):        
        """Record a new institution in the institutions.txt file
        """

        # Function to get the existing initials from the file
        def get_existing_acronyms(file_path):
            try:
                df_institutions = self.get_institutions()
                existing_acronyms = df_institutions['acronym'].values                
                return existing_acronyms
            except FileNotFoundError:
                # If the file does not exist, return an empty set
                return set()
            
        # Function to update the text file if the initials are unique
        def update_text_file(file_path, name, acronym):
            # Check if the acronym already exists
            existing_acronyms = get_existing_acronyms(file_path)
                        
            if acronym in existing_acronyms:
                print(f"Acronym '{acronym}' already exists. Please use a different acronym.")
            else:
                df_institutions = self.get_institutions()
                df_institutions = pd.concat([df_institutions, pd.DataFrame(data=[name,acronym], index=['name','acronym']).T])
                df_institutions = df_institutions.sort_values(by='name')
                df_institutions.to_csv(self.folder_db/'institutions.txt',index=False)
               
                print(f"Added: {name} : {acronym}")

        # Define ipython widgets
        name_widget = ipw.Text(        
            value='',
            placeholder='Enter a name',
            description='Name', 
            style=style,
            layout=Layout(width="40%", height="30px")              
        )

        acronym_widget = ipw.Text(        
            value='',
            placeholder='Enter an acronym',
            description='Acronym', 
            style=style,
            layout=Layout(width="40%", height="30px")            
        )

        recording = ipw.Button(
            description='Record institution',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the person info in the persons.txt file.
            """

            button_record_output.clear_output(wait=True)

            name = name_widget.value.strip()            
            acronym = acronym_widget.value.strip()

            with button_record_output:

                if name and acronym: # ensure all fields are filled
                    update_text_file(self.folder_db / 'institutions.txt', name, acronym)
                else:
                    
                    print("Please enter all fields (Name, Acronym)")

        recording.on_click(button_record_pressed)

        display(name_widget,acronym_widget)
        display(ipw.HBox([recording, button_record_output]))       
    
    
    def add_lamps(self):
        """Record a new lamp in the lamps.txt file

        Returns
        -------
        ipywidgets
            fill in the ID and description of the lamp to be registered. 
        """
        

        # Function to get the existing lamps ID from the file
        def get_existing_lamps():
            try:
                df_lamps = self.get_lamps()
                existing_lamps = df_lamps['ID'].values                
                return existing_lamps
            except FileNotFoundError:
                # If the file does not exist, return an empty set
                return set()
            
        # Function to update the text file if the ID is unique
        def update_text_file(ID, description):
            # Check if the ID already exists
            existing_lamps = get_existing_lamps()
                        
            if ID in existing_lamps:
                print(f"ID '{ID}' already exists. Please use a different ID.")
            else:
                df_lamps = self.get_lamps()
                df_lamps = pd.concat([df_lamps, pd.DataFrame(data=[ID,description], index=['ID','description']).T])
                df_lamps = df_lamps.sort_values(by='ID')
                df_lamps.to_csv(self.folder_db/'lamps.txt',index=False)
               
                print(f"Added: {ID} : {description}")

        # Define ipython widgets
        wg_ID = ipw.Text(        
            value='',
            placeholder='Enter an ID',
            description='ID', 
            layout=Layout(width="40%", height="30px"),
            style=style,              
        )

        wg_description = ipw.Text(        
            value='',
            placeholder='Enter a brief description',
            description='Description', 
            layout=Layout(width="40%", height="30px"),
            style=style,            
        )

        recording = ipw.Button(
            description='Record lamp',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the lamp info in the lamps.txt file.
            """

            button_record_output.clear_output(wait=True)

            id = wg_ID.value.strip()            
            description = wg_description.value.strip()

            with button_record_output:

                if id and description: # ensure all fields are filled
                    update_text_file(id, description)
                else:                    
                    print("Please enter all fields (ID, description)")

        recording.on_click(button_record_pressed)

        display(wg_ID,wg_description)
        display(ipw.HBox([recording, button_record_output]))
    
    
    def add_materials(self, name:Optional[str] = None):
        """Register a new object material.

        Parameters
        ----------
        name : Optional[str], optional
            Name of the material, by default None
            When None, the ipywidget text will be empty and you will have to fill it.

        Returns
        -------
        ipywidgets
            fill in the name of the material to be registered. 
        """

        # Define ipython widgets

        wg_material = ipw.Text(        
            value=name,
            placeholder='Enter a name',
            description='Material',  
            style=style,
            layout=Layout(width="40%", height="30px")             
        )    

        recording = ipw.Button(
            description='Record material',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_record_output = ipw.Output()


        # Define the path of the users database file

        databases_folder = self.folder_db
        materials_filename = 'object_materials.txt'


        # Define some functions
        def update_text_file(new_value):

            # Check if the material has already been registered 
            existing_materials = self.get_materials()  

            if new_value in existing_materials:
                print(f'The material "{new_value}" has already been registered.')

            else:
                existing_materials.append(str(new_value).lower())         
                existing_materials = sorted(existing_materials)
                
                with open(databases_folder / materials_filename, 'w') as f:
                        f.write('\n'.join(existing_materials))

                f.close()            
                
                print(f"Material added: {new_value}")
        

        def button_record_pressed(b):
            """
            Save the type name in the object_materials.txt file.
            """

            button_record_output.clear_output(wait=True)
            material_name = wg_material.value.strip()
            
            with button_record_output:            
                
                if material_name: # ensure all fields are filled
                    update_text_file(material_name)
                else:                    
                    print("Please enter a material name")
    
    
        # Link the widget button to the function
        recording.on_click(button_record_pressed)

        # Display the widgets
        display(wg_material)
        display(ipw.HBox([recording, button_record_output]))
    
    
    def add_methods(self):        
        """Record a new analytical method in the analytical_methods.txt file
        """

        # Function to get the existing acronym from the file
        def get_existing_acronyms():
            try:
                df_methods = self.get_methods()
                existing_acronyms = df_methods['acronym'].values                
                return existing_acronyms
            except FileNotFoundError:
                # If the file does not exist, return an empty set
                return set()
            
        # Function to update the text file if the initials are unique
        def update_text_file(acronym, name):
            # Check if the acronym already exists
            existing_acronyms = list(get_existing_acronyms())
                        
            if acronym in existing_acronyms:
                print(f"Acronym '{acronym}' already exists. Please use a different acronym.")
            else:
                df_methods = self.get_methods()
                df_methods = pd.concat([df_methods, pd.DataFrame(data=[acronym, name], index=['acronym', 'name']).T])
                df_methods = df_methods.sort_values(by='acronym')
                df_methods.to_csv(self.folder_db/'analytical_methods.txt',index=False)
               
                print(f"Added: {acronym} : {name}")

        # Define ipython widgets
        name_widget = ipw.Text(        
            value='',
            placeholder='Enter a name',
            description='Name', 
            style=style,
            layout=Layout(width="40%", height="30px")              
        )

        acronym_widget = ipw.Text(        
            value='',
            placeholder='Enter an acronym',
            description='Acronym',   
            style=style,
            layout=Layout(width="40%", height="30px")          
        )

        recording = ipw.Button(
            description='Record method',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the person info in the persons.txt file.
            """

            button_record_output.clear_output(wait=True)

            name = name_widget.value.strip()            
            acronym = acronym_widget.value.strip()

            with button_record_output:

                if name and acronym: # ensure all fields are filled
                    update_text_file(acronym,name)
                else:
                    
                    print("Please enter all fields (Name, Acronym)")

        recording.on_click(button_record_pressed)

        display(acronym_widget,name_widget)
        display(ipw.HBox([recording, button_record_output])) 
    
    
    def add_objects(self, project_id:Optional[str] = ''):
        """Add a new object in the database file 'objects_info.csv'

        Parameters
        ----------
        project_id : Optional[str], optional
            Project ID related to the object, by default ''
            If the object is not coupled to a given project, then it falls under the 'noProject' category.

        Returns
        -------
        ipywidgets
            It returns several ipywidgets inside which one can enter the information related to the object.
        """

        db_projects = self.get_projects()
        projects_list = list(db_projects['project_id'].values)

        db_objects = self.get_objects()
        existing_columns = list(db_objects.columns)

        creators_file = pd.read_csv(self.folder_db / 'object_creators.txt')
        creators = [f'{x[0]}, {x[1]}' if isinstance(x[1],str) else x[0] for x in creators_file.values]
        
        types_file = open(self.folder_db / r'object_types.txt', 'r').read()
        types = types_file.split("\n")        

        techniques_file = open(self.folder_db / r'object_techniques.txt', 'r').read().strip()
        techniques = sorted(techniques_file.split("\n"), key=str.lower)        

        materials_file = open(self.folder_db  / r'object_materials.txt', 'r').read()
        materials = sorted(materials_file.split("\n"), key=str.lower)        

        owners_file = pd.read_csv(self.folder_db / 'institutions.txt')
        owners = tuple(owners_file['name'].values)
               

        # Define ipython widgets

        project_id = ipw.Combobox(
            value = project_id,
            placeholder='Project',
            options = projects_list,
            description = 'Project ID',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        )

        object_id = ipw.Text(        
            value='',
            placeholder='Inv. N°',
            description='Object ID',
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,   
        )

        object_category = ipw.Dropdown(
            options=['heritage','model','reference','sample'],
            value='heritage',
            description='Category',
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        )    

        object_creator1 = ipw.Combobox(
            placeholder = 'Surname, Name',
            options = creators,
            description = 'Creator 1',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        ) 

        object_creator2 = ipw.Combobox(
            placeholder = 'Surname, Name (optional)',
            options = creators,
            description = 'Creator 2',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        ) 

        object_creator3 = ipw.Combobox(
            placeholder = 'Surname, Name (optional)',
            options = creators,
            description = 'Creator 3',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        ) 

        object_date = ipw.Text(
            value='',
            placeholder='Enter a date',
            description='Date',
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,         
        )  

        object_owner = ipw.Combobox(
            placeholder = 'Enter an institution/owner',
            options = owners,
            description = 'Object owner',
            ensure_option = False,
            disabled = False,
            layout=Layout(width='99%',height="30px"),
            style = style

        )

        object_title = ipw.Textarea(        
            value='',
            placeholder='Enter the title',
            description='Title',
            disabled=False,
            layout=Layout(width='99%',height="100%"),
            style=style,   
        )  

        object_name = ipw.Text(        
            value='',
            placeholder='Enter a short object (no space, no underscore)',
            description='Name',
            disabled=False,
            layout=Layout(width='99%',height="30px"),
            style=style,   
        )

        object_type = ipw.Combobox(
            placeholder = 'General classification',
            options=types,
            description='Type',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="99%", height="30px"),
            style=style,
        )

        object_techniques = ipw.Combobox(  
            placeholder='Choose a technique',          
            options = techniques,
            description = '',
            ensure_option=False,       
            layout=Layout(width="65%", height="180px"),
            style=style,
        )  

        object_techniques_selected = ipw.SelectMultiple(            
            options=[], 
            description='Techniques',           
            ensure_option=False,
            rows=6,
            disabled=False,
            layout=Layout(width="99%", height="160px"),
            style=style,
        ) 

        object_materials = ipw.Combobox(
            placeholder='Choose a material',
            options=materials,
            description='',
            ensure_option=True,
            layout=Layout(width="65%", height="180px"),
            style=style,
        )
        
        object_materials_selected = ipw.SelectMultiple(            
            options=[], 
            description='Materials',           
            ensure_option=False,
            rows=6,
            disabled=False,
            layout=Layout(width="99%", height="160px"),
            style=style,
        )

        recording = ipw.Button(
            description='Record object',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
            #icon='check' # (FontAwesome names without the `fa-` prefix)
        )        
        

        button_record_output = ipw.Output()    

        # Create a button to remove selected techniques
        remove_technique_button = ipw.Button(
            description='Remove selected',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me to remove the selected techniques',
            icon='',  # 'check'
            layout=Layout(width="35%", height="30px"),
            style=style,
        )   

        # Create a button to remove selected materials
        remove_material_button = ipw.Button(
            description='Remove selected',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me to remove the selected materials',
            icon='',
            layout=Layout(width="35%", height="30x"),
            style=style,
        ) 
    
               
                
        # Combobox for additional parameters (if any)
        additional_params = [col for col in existing_columns if col not in [
            'project_id',
            'object_id',
            'object_category',
            'object_type',
            'object_technique',
            'object_title',
            'object_name',
            'object_creator',
            'object_date',
            'object_owner',
            'object_material']]

        additional_param_widgets = {}
        for param in additional_params:
            additional_param_widgets[param] = ipw.Combobox(
                description=param,
                options=[],  # You can populate this with options if needed
                placeholder=f"Enter {param} value",
                style=style
            )  

        # Function to add selected material to the SelectMultiple
        def object_materials_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                selected_material = change['new']
                if selected_material and selected_material not in object_materials_selected.value:
                    object_materials_selected.options = list(object_materials_selected.options) + [selected_material]  

        # Function to add selected technique to the SelectMultiple
        def object_techniques_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                selected_technique = change['new']
                if selected_technique and selected_technique not in object_techniques_selected.value:
                    object_techniques_selected.options = list(object_techniques_selected.options) + [selected_technique]     

        # Function to remove selected techniques
        def on_remove_technique_button_click(b):
            # Get the indices of the selected options
            selected_indices = object_techniques_selected.index
            # Remove the selected options from the SelectMultiple
            object_techniques_selected.options = [option for i, option in enumerate(object_techniques_selected.options) if i not in selected_indices]

        # Function to remove selected materials
        def on_remove_material_button_click(b):
            # Get the indices of the selected options
            selected_indices = object_materials_selected.index
            # Remove the selected options from the SelectMultiple
            object_materials_selected.options = [option for i, option in enumerate(object_materials_selected.options) if i not in selected_indices]
        
        
        # Observe changes in the Combobox widgets
        object_materials.observe(object_materials_change)
        object_techniques.observe(object_techniques_change)

        # Set the button click event handler
        remove_technique_button.on_click(on_remove_technique_button_click)
        remove_material_button.on_click(on_remove_material_button_click)

        def button_record_pressed(b):
            """
            Save the object info in the object database file (objects_info.csv).
            """        
            

            with button_record_output:
                button_record_output.clear_output(wait=True)

                db_objects_file = self.folder_db / 'objects_info.csv'
                db_objects = pd.read_csv(db_objects_file)    

                # Check whether object_id is unique
                if object_id.value in db_objects['object_id'].values:
                    with button_record_output:
                        print(f'Object not recorded: the object ID you entered ({object_id.value}) has already been assigned.')
                    return
                                
                creators = [f'{x[0]}, {x[1]}' if isinstance(x[1],str) else x[0] for x in self.get_creators().values]

                owners_file = open(self.folder_db  / r'institutions.txt', 'r').read().splitlines()
                owners = owners_file             

                types_file = open(self.folder_db / r'object_types.txt', 'r').read().splitlines()
                types = types_file    

                if object_creator2.value == '':
                    object_creators = object_creator1.value

                elif object_creator3.value == '':
                    object_creators = '_'.join([object_creator1.value, object_creator2.value])
                
                else:
                    object_creators = '_'.join([object_creator1.value, object_creator2.value, object_creator3.value])       
                                                     

                new_row = pd.DataFrame({                    
                    'project_id': project_id.value,
                    'object_id' : object_id.value,                   
                    'object_category': object_category.value, 
                    'object_type': object_type.value, 
                    "object_technique": "_".join(object_techniques_selected.options),
                    "object_title": object_title.value,
                    'object_name': object_name.value,
                    'object_creator': object_creators,                        
                    'object_date': object_date.value,
                    'object_owner': object_owner.value,
                    'object_material': "_".join(object_materials_selected.options)},                       
                    index=[0] 
                    ) 


                if object_creator1.value not in creators:

                    creator_surname = object_creator1.value.split(',')[0].strip()
                    try:
                        creator_name = object_creator1.value.split(',')[1].strip()
                    except IndexError:
                        creator_name = ''
                    
                    df_creators = pd.read_csv(self.folder_db / 'object_creators.txt')
                    df_creators = pd.concat([df_creators, pd.DataFrame(data=[creator_surname,creator_name], index=['surname','name']).T])
                    df_creators.to_csv(self.folder_db / 'object_creators.txt', index=False)
                               
                if object_creator2.value not in creators:

                    creator_surname = object_creator2.value.split(',')[0].strip()
                    try:
                        creator_name = object_creator2.value.split(',')[1].strip()
                    except IndexError:
                        creator_name = ''
                    
                    df_creators = pd.read_csv(self.folder_db / 'object_creators.txt')
                    df_creators = pd.concat([df_creators, pd.DataFrame(data=[creator_surname,creator_name], index=['surname','name']).T])
                    df_creators.to_csv(self.folder_db / 'object_creators.txt', index=False)


                if object_type.value not in types:
                    types.append(str(object_type.value))
                    types = sorted(types, key=str.casefold)

                    with open(self.folder_db / 'object_types.txt', 'w') as f:
                        f.write('\n'.join(types).strip())
                    f.close()                                 
                

                # Add additional parameters to the new record
                for param, widget in additional_param_widgets.items():
                    new_row[param] = widget.value

                db_objects_new = pd.concat([db_objects, new_row],)
                db_objects_new.to_csv(db_objects_file, index= False)
                print(f'Object {object_id.value} added to database.')

        recording.on_click(button_record_pressed)

        display(
            ipw.HBox([
                ipw.VBox([object_id,project_id,object_creator1,object_creator2,object_creator3,object_date,object_owner,object_category,object_type,object_title, object_name], layout=Layout(width="30%", height="400px"), style=style,),
                ipw.VBox([ipw.HBox([object_techniques,remove_technique_button]),object_techniques_selected,ipw.HBox([object_materials,remove_material_button]),object_materials_selected], layout=Layout(width="30%", height="400px"), style=style),
                ipw.VBox([*[widget for widget in additional_param_widgets.values()]], layout=Layout(width="30%", height="400px"), style=style)
                ]))
                
        display(ipw.HBox([recording, button_record_output]))
        

    def add_users(self):
        """Record a new person in the users_info.txt file
        """

        # Function to get the existing initials from the file
        def get_existing_initials(file_path):
            try:
                df_persons = self.get_users()
                existing_initials = df_persons['initials']                
                return existing_initials
            except FileNotFoundError:
                # If the file does not exist, return an empty set
                return set()
            
        # Function to update the text file if the initials are unique
        def update_text_file(file_path, name, surname, initials):
            # Check if the initials already exist
            existing_initials = get_existing_initials(file_path)
            
            if initials in existing_initials:
                print(f"Initials '{initials}' already exist. Please use different initials.")
            else:
                df_persons = self.get_users()
                df_persons = pd.concat([df_persons, pd.DataFrame(data=[name,surname,initials], index=['name','surname','initials']).T])
                df_persons = df_persons.sort_values(by='name')
                df_persons.to_csv(self.folder_db/'users_info.txt',index=False)
               
                print(f"Added: {name}, {surname} : {initials}")


        # Define ipython widgets
        name_widget = ipw.Text(        
            value='',
            placeholder='Enter a name',
            description='Name',               
        )

        surname_widget = ipw.Text(        
            value='',
            placeholder='Enter a surname',
            description='Surname',             
        )
        
        initials_widget = ipw.Text(        
            value='',
            placeholder='Enter initials in capital letters',
            description='Initials',             
        )

        recording = ipw.Button(
            description='Record user',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
        

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the person info in the users_info.txt file.
            """

            button_record_output.clear_output(wait=True)

            name = name_widget.value.strip()
            surname = surname_widget.value.strip()
            initials = initials_widget.value.strip()

            with button_record_output:

                if name and surname and initials: # ensure all fields are filled
                    update_text_file(self.folder_db / 'users_info.txt', name, surname, initials)
                else:
                    
                    print("Please enter all fields (Name, Surname, Initials)")

            

        recording.on_click(button_record_pressed)

        display(name_widget,surname_widget,initials_widget)
        display(ipw.HBox([recording, button_record_output]))


    def add_projects(self, project_id:Optional[str] = None):
        """Add a new project in the projects_info.csv file

        Parameters
        ----------
        project_id : Optional[str], optional
            ID number of the new project, by default None


        Returns
        -------
        ipywidgets
            It returns several ipywidgets inside which one can enter the information related to the project.
        
        """

        db_projects = self.get_projects()
        existing_columns = list(db_projects.columns)
        institutions = tuple(self.get_institutions()['name'].values)    
        persons = tuple([f'{x[0]}, {x[1]}' for x in self.get_users()[['name','surname']].values])    
        methods = list(self.get_methods()['acronym'].values)

        # Define ipython widgets
        project_Id = ipw.Text(        
            value=project_id,
            placeholder='Type something',
            description='Project Id',
            disabled=False,
            layout=Layout(width="95%", height="30px"),
            style=style,   
        )

        institution = ipw.Combobox(
            placeholder = 'Enter an institution',
            options = institutions,              
            description = 'Institution',
            ensure_option=False,
            disabled=False,
            layout=Layout(width="95%", height="30px"),
            style=style,
        )
        
        startDate = ipw.DatePicker(
            description='Start date',
            disabled=False,
            layout=Layout(width="90%", height="30px"),
            style=style,
        )

        endDate = ipw.DatePicker(
            description='End date',
            disabled=False,
            layout=Layout(width="90%", height="30px"),
            style=style,
        )

        project_leader = ipw.Combobox(
            placeholder = 'Enter a name or a surname',
            options=persons,            
            description='Project leader',
            disabled=False,
            layout=Layout(width="90%", height="30px"),
            style=style,
        )

        coresearchers = ipw.SelectMultiple(
            value=['none'],
            options=['none'] + list(persons), 
            description='Co-researchers',
            rows=10,
            disabled=False,
            layout=Layout(width="90%", height="135px"),
            style=style,
        )

        wg_methods = ipw.SelectMultiple(
            value=['none'],
            options=['none'] + list(methods), 
            description='Methods',
            rows=10,
            disabled=False,
            layout=Layout(width="90%", height="170px"),
            style=style,
        )
        

        recording = ipw.Button(
            description='Record project',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',
            #layout=Layout(width="50%", height="30px"),
            #style=style,
            #icon='check' # (FontAwesome names without the `fa-` prefix)
        )
        

        project_keyword = ipw.Text(
            placeholder = 'Describe project in 1 or 2 words',
            description = 'Project keywords',
            disabled = False,
            layout=Layout(width="95%", height="30px"),
            style = style,
        )

        # Combobox for additional parameters (if any)
        additional_params = [col for col in existing_columns if col not in ['project_id', 'institution', 'start_date', 'end_date', 'project_leader', 'co-researchers', 'keywords', 'methods']]
        additional_param_widgets = {}
        for param in additional_params:
            additional_param_widgets[param] = ipw.Combobox(
                description=param,
                options=[],  # You can populate this with options if needed
                placeholder=f"Enter {param} value"
            )

        button_record_output = ipw.Output()


        def button_record_pressed(b):
            """
            Save the project info in the project database file (projects_info.csv).
            """

            with button_record_output:
                button_record_output.clear_output(wait=True)

                Projects_DB_file = self.folder_db / 'projects_info.csv'
                Projects_DB = pd.read_csv(Projects_DB_file)  
                persons = self.get_users()

                institutions = pd.read_csv(self.folder_db / 'institutions.txt')['name'].values

                
                project_leader_name = project_leader.value.split(',')[0].strip()
                project_leader_surname = project_leader.value.split(',')[1].strip()
                project_leader_initials = persons.query(f'name == "{project_leader_name}" and surname == "{project_leader_surname}"')['initials'].values[0]

                if coresearchers.value[0] == 'none':
                    coresearchers_initials = 'none'

                else:
                    coresearchers_initials = []
                    for coresearcher in [x for x in coresearchers.value]:
                        coresearcher_name = coresearcher.split(',')[0].strip()
                        coresearcher_surname = coresearcher.split(',')[1].strip()
                        coresearcher_initials = persons.query(f'name == "{coresearcher_name}" and surname == "{coresearcher_surname}"')['initials'].values[0]
                        coresearchers_initials.append(coresearcher_initials)

                
                    coresearchers_initials = '-'.join(coresearchers_initials)
                
                if wg_methods.value == 'none':
                    methods_acronym = 'none'

                else:
                    methods_acronym = "_".join(wg_methods.value)
             
                new_row = pd.DataFrame({'project_id':project_Id.value,
                        'institution':institution.value, 
                        'start_date':startDate.value, 
                        'end_date':endDate.value,
                        'project_leader':project_leader_initials,  
                        'co-researchers':coresearchers_initials,                       
                        'keywords':project_keyword.value,
                        'methods':methods_acronym},                                               
                        index=[0] 
                        )  
                
                if institution.value not in institutions:                       
                    institutions.append(str(institution.value))         
                    institutions = sorted(institutions)   

                    with open(self.folder_db / 'institutions.txt', 'w') as f:
                        f.write('\n'.join(institutions).strip())  
                    f.close()                
                

                # Add additional parameters to the new record
                for param, widget in additional_param_widgets.items():
                    new_row[param] = widget.value

                Projects_DB_new = pd.concat([Projects_DB, new_row],)
                Projects_DB_new.to_csv(Projects_DB_file, index= False)
                print(f'Project {project_Id.value} added to database.')

        recording.on_click(button_record_pressed)


        # Display the widgets
        display(ipw.HBox([
            ipw.VBox([
                ipw.HBox([
                    ipw.VBox([project_Id,institution, project_keyword, startDate, endDate],layout=Layout(width="60%", height="100%")),
                    ipw.VBox([project_leader, coresearchers],layout=Layout(width="60%", height="100%")),
                    ipw.VBox([wg_methods],layout=Layout(width="60%", height="100%"))
                    ]),                
                ], layout=Layout(width="70%", height="100%")),                        
            ], layout=Layout(width="100%", height="100%"))
        ) 

        display(*[widget for widget in additional_param_widgets.values()])
        display(ipw.HBox([recording, button_record_output]))


    def add_techniques(self):
        """Register a new object technique.

        Returns
        -------
        ipywdigets
            fill in the name of the technique to be registered. 
        """

        # Define ipython widgets

        technique_widget = ipw.Text(        
            value='',
            placeholder='Enter a name',
            description='Technique',   
            style=style,
            layout=Layout(width="40%", height="30px")            
        )    

        recording = ipw.Button(
            description='Record technique',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_record_output = ipw.Output()


        # Define the path of the users database file

        databases_folder = self.folder_db
        techniques_filename = 'object_techniques.txt'


        # Define some functions    

        def get_existing_techniques(file_path):
            try:
                return self.get_techniques()        
                
            except FileNotFoundError:            
                return
                

        def update_text_file(file_path, name):

            # Check if the technique has already been registered        
            existing_techniques = get_existing_techniques(file_path)

            if technique_widget.value in existing_techniques:
                print(f'The technique {technique_widget.value} has already been registered.')

            else:
                existing_techniques.append(str(technique_widget.value).lower())         
                existing_techniques = sorted(existing_techniques)
                
                with open(databases_folder / techniques_filename, 'w') as f:
                        f.write('\n'.join(existing_techniques))

                f.close()            
                
                print(f"Technique added: {name}")

        

        def button_record_pressed(b):
            """
            Save the technique name in the object_techniques.txt file.
            """

            button_record_output.clear_output(wait=True)

            name = technique_widget.value.strip()
            

            with button_record_output:            
                
                if name: # ensure all fields are filled
                    update_text_file(databases_folder / techniques_filename, name)
                else:                    
                    print("Please enter all fields (Name)")
    
    
        # Link the widget button to the function
        recording.on_click(button_record_pressed)

        # Display the widgets
        display(technique_widget)
        display(ipw.HBox([recording, button_record_output]))

    
    def add_types(self, name:Optional[str] = None):
        """Register a new object type.

        Parameters
        ----------
        name : Optional[str], optional
            name of the object type, by default None

        Returns
        -------
        ipywdigets
            fill in the name of the type to be registered. 
        """

        # Define ipython widgets

        wg_type = ipw.Text(        
            value=name,
            placeholder='Enter a name',
            description='Type',
            style=style,
            layout=Layout(width="40%", height="30px")               
        )    

        recording = ipw.Button(
            description='Record type',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_record_output = ipw.Output()


        # Define the path of the users database file

        databases_folder = self.folder_db
        types_filename = 'object_types.txt'


        # Define some functions
        def update_text_file(new_value):

            # Check if the type has already been registered        
            existing_types = self.get_types()

            if new_value in existing_types:
                print(f'The type "{new_value}" has already been registered.')

            else:
                existing_types.append(str(new_value).lower())         
                existing_types = sorted(existing_types)
                
                with open(databases_folder / types_filename, 'w') as f:
                        f.write('\n'.join(existing_types))

                f.close()            
                
                print(f"Type added: {new_value}")

        

        def button_record_pressed(b):
            """
            Save the type name in the object_types.txt file.
            """

            button_record_output.clear_output(wait=True)
            type_name = wg_type.value.strip()
            
            with button_record_output:            
                
                if type_name: # ensure all fields are filled
                    update_text_file(type_name)
                else:                    
                    print("Please enter a type name")
    
    
        # Link the widget button to the function
        recording.on_click(button_record_pressed)

        # Display the widgets
        display(wg_type)
        display(ipw.HBox([recording, button_record_output]))
    
    
    def add_white_standards(self):
        """Record a new white standard in the white_standards.txt file
        """

        # Function to get the existing standards ID from the file
        def get_existing_standards():
            try:
                df_standards = self.get_white_standards()
                existing_standards = df_standards['ID'].values                
                return existing_standards
            except FileNotFoundError:
                # If the file does not exist, return an empty set
                return set()
            
        # Function to update the text file if the ID is unique
        def update_text_file(ID, description):
            # Check if the ID already exists
            existing_standards = get_existing_standards()
                        
            if ID in existing_standards:
                print(f"ID '{ID}' already exists. Please use a different ID.")
            else:
                df_standards = self.get_white_standards()
                df_standards = pd.concat([df_standards, pd.DataFrame(data=[ID,description], index=['ID','description']).T])
                df_standards = df_standards.sort_values(by='ID')
                df_standards.to_csv(self.folder_db/'white_standards.txt',index=False)
               
                print(f"Added: {ID} : {description}")

        # Define ipython widgets
        wg_ID = ipw.Text(        
            value='',
            placeholder='Enter an ID',
            description='ID', 
            layout=Layout(width="40%", height="30px"),
            style=style,              
        )

        wg_description = ipw.Text(        
            value='',
            placeholder='Enter a brief description',
            description='Description', 
            layout=Layout(width="40%", height="30px"),
            style=style,            
        )

        recording = ipw.Button(
            description='Record standard',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the standard info in the white_standards.txt file.
            """

            button_record_output.clear_output(wait=True)

            id = wg_ID.value.strip()            
            description = wg_description.value.strip()

            with button_record_output:

                if id and description: # ensure all fields are filled
                    update_text_file(id, description)
                else:                    
                    print("Please enter all fields (ID, description)")

        recording.on_click(button_record_pressed)

        display(wg_ID,wg_description)
        display(ipw.HBox([recording, button_record_output]))
    
           
    def get_creators(self):
        """Retrieve the registered creators of objects.

        Returns
        -------
        pandas dataframe
            It returns the surname and name of the creators inside a two-columns dataframe.
        """

        if (Path(self.folder_db) / 'object_creators.txt').exists():
            df_creators = pd.read_csv(Path(self.folder_db) / 'object_creators.txt')
            return df_creators
        
        else:
            print(f'The file {Path(self.folder_db) / "object_creators.txt"} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return

    
    def get_users(self):
        """Retrieve the registered users.

        Returns
        -------
        pandas dataframe
            It returns the name,surname, and initials of the users inside a three-columns dataframe.
        """
        
        filename = 'users_info.txt'
        if (Path(self.folder_db) / filename).exists():
            df_persons = pd.read_csv(Path(self.folder_db) / filename)
            return df_persons
        
        else:
            print(f'The file {Path(self.folder_db) / filename} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return
        

    def get_institutions(self):
        """Retrieve the registered institutions.

        Returns
        -------
        pandas dataframe
            It returns the name and acronym of the institutions inside a two-columns dataframe.
        """

        if (Path(self.folder_db) / 'institutions.txt').exists():
            df_institutions = pd.read_csv(Path(self.folder_db) / 'institutions.txt')
            return df_institutions
        
        else:
            print(f'The file {Path(self.folder_db) / "institutions.txt"} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return


    def get_devices(self):
        """Retrieve the registered analytical devices.

        Returns
        -------
        pandas dataframe
            It returns the information regarding the devices inside a dataframe.
        """

        if (Path(self.folder_db) / 'devices.txt').exists():
            df_devices = pd.read_csv(Path(self.folder_db) / 'devices.txt')
            return df_devices
        
        else:
            print(f'The file {Path(self.folder_db) / "devices.txt"} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return


    def get_lamps(self):
        """Retrieve the registered lamps.

        Returns
        -------
        pandas dataframe
            It returns the ID and description of the lamps inside a two-columns dataframe.
        """

        if (Path(self.folder_db) / 'lamps.txt').exists():
            df_lamps = pd.read_csv(Path(self.folder_db) / 'lamps.txt')
            return df_lamps
        
        else:
            print(f'The file {Path(self.folder_db) / "lamps.txt"} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return  
    
    
    def get_materials(self):
        """Retrieve the registered materials.

        Returns
        -------
        List
            It returns the materials as strings inside a list.
        """
        
        materials_filename = 'object_materials.txt'
        
        if not (self.folder_db / materials_filename).exists():
            print(f'Please create an empty file called "{materials_filename}" in the the following folder: {self.folder_db}')
            return
        
        else:            
            materials_df = pd.read_csv(self.folder_db / materials_filename, header=None)
            materials = sorted(list(materials_df.values.flatten()), key=str.lower)              
            return materials

    
    def get_methods(self):
        """Retrieve the registered scientific methods used to analyze objects.

        Returns
        -------
        pandas dataframe
            It returns the name and acronym of the analytical methods inside a two-columns dataframe.
        """

        databases_folder = self.folder_db
        methods_filename = 'analytical_methods.txt'

        if not (databases_folder / methods_filename).exists():
            print(f'Please create an empty file called "{methods_filename}" in the the following folder: {databases_folder}')
            return
        
        else:
            df_methods = pd.read_csv((databases_folder / methods_filename))            
            return df_methods
    
    
    def get_objects(self,object_category:Union[str,list]=None, object_type:Union[str,list]=None, object_technique:Union[str,list]=None, object_owner:Union[str,list] = None, project_id:Union[str,list] = None, object_id:Union[str,list] = None, match_all:Optional[bool]=False):
        """Retrieve information about the objects

        Parameters
        ----------
        object_category : Union[str,list], optional
            Category of objects, by default None
            There are only four categories of objects ('heritage', 'model', 'reference', 'sample')
            If only one category is entered, you may enter it as a string, otherwise use a list.
        
        object_type : Union[str,list], optional
            Object type(s) for describing objects, by default None
            If only one type is entered, you may enter it as a string, otherwise use a list.
            For a list of all the types mentioned, use the function "get_types()".
        
        object_technique : Union[str,list], optional
            Technique(s) used to create the objects, by default None
            If only one technique is entered, you may enter it as a string, otherwise use a list.
            For a list of all the techniques mentioned, use the function "get_techniques()".
        
        object_owner : Union[str,list], optional
            Institution(s) that own the objects, by default None
            If only one institution is entered, you may enter it as a string, otherwise use a list.
        
        project_id : Union[str,list], optional
            ID number of one or several projects, by default None
            If only one ID is entered, you may enter it as a string, otherwise use a list.
        
        object_id : Union[str,list], optional
            _description_, by default None
        
        match_all : Optional[bool], optional
            Whether all the wanted queries should match, by default False

        Returns
        -------
        pandas dataframe
            It returns the object info inside a dataframe where each line corresponds to a single object.
        """       

        databases_folder = self.folder_db
        objects_filename = 'objects_info.csv'
        df_objects = pd.read_csv((databases_folder / objects_filename)).fillna('none')

        if not (databases_folder / objects_filename).exists():
            print(f'Please create a .csv file called "{objects_filename}" in the the following folder: {databases_folder} ')
            return
        

        if object_category == None and object_type == None and object_technique == None and object_owner == None and project_id == None and object_id == None:
            return df_objects
        
        if isinstance(object_category, str):
            object_category = [object_category]

        if isinstance(object_type, str):
            object_type = [object_type]

        if isinstance(object_technique, str):
            object_technique = [object_technique]    

        if isinstance(object_owner, str):
            object_owner = [object_owner]

        if isinstance(project_id, str):
            project_id = [project_id]

        if isinstance(object_id, str):
            object_id = [object_id]

        


        df_institutions = self.get_institutions()
        list_acronyms = df_institutions['acronym'].values

        if object_owner != None:
            object_owner = [df_institutions.query(f'acronym == "{x}"')['name'].values[0] if x in list_acronyms else 'none' for x in object_owner]
            object_owner = [x for x in object_owner if x != 'none']
            

        
        parameters = ['object_category','object_type','object_technique','object_owner','project_id', 'object_id']
        input_values = [object_category, object_type, object_technique, object_owner, project_id, object_id]

        filters = {}
        

        for x,y in zip(parameters, input_values):
            if y != None:
                filters[x] = y
        
        
        def match_criteria(row):
            results = []
            for col, values in filters.items():
                if col in df_objects.columns:
                    matches = [bool(re.search(fr'(^|_){v}(_|$)', row[col])) for v in values]
                    results.append(all(matches) if match_all else any(matches))
            
            return all(results) if match_all else any(results)
        
        return df_objects[df_objects.apply(match_criteria, axis=1)]
    
            
    def get_projects(self, PL:Union[str,list]=None, coresearchers:Union[str,list]=None, methods:Union[str,list]=None, institutions:Union[str,list] = None, project_id:Union[str,list] = None, match_all:Optional[bool]=False):
        """Retrieve information about the registered projects

        Parameters
        ----------
        PL : Union[str,list], optional
            The initials of the main researcher, by default None
            If only one initials is entered, you may enter it as a string, otherwise use a list.

        coresearchers : Union[str,list], optional
            The initials of the co-researchers, by default None
            If only one initials is entered, you may enter it as a string, otherwise use a list.

        methods : Union[str,list], optional
            Acronym of the method, by default None
            If only one method is entered, you may enter it as a string, otherwise use a list.

        institutions : Union[str,list], optional
            Acronym of the institutions, by default None
            If only one institution is entered, you may enter it as a string, otherwise use a list.

        project_id : Union[str,list], optional
            ID of the project, by default None
            If only one ID is entered, you may enter it as a string, otherwise use a list.

        match_all : Optional[bool], optional
            Whether all the wanted queries should match, by default False

        Returns
        -------
        pandas dataframe
            It return the desired info about registered projects.
        """ 

        databases_folder = self.folder_db
        projects_filename = 'projects_info.csv'
        df_projects = pd.read_csv((databases_folder / projects_filename))

        if not (databases_folder / projects_filename).exists():
            print(f'Please create a file called "projects_info.csv" in the the following folder: {databases_folder}')
            return
        

        if PL == None and methods == None and institutions == None and project_id == None:
            return df_projects
        
        if isinstance(PL, str):
            PL = [PL]

        if isinstance(coresearchers, str):
            coresearchers = [coresearchers]

        if isinstance(methods, str):
            methods = [methods]    

        if isinstance(institutions, str):
            institutions = [institutions]
        

        df_institutions = self.get_institutions()
        list_acronyms = df_institutions['acronym'].values

        if institutions != None:
            institutions = [df_institutions.query(f'acronym == "{x}"')['name'].values[0] if x in list_acronyms else 'none' for x in institutions]
            institutions = [x for x in institutions if x != 'none']

        
        parameters = ['project_leader', 'co-researchers', 'methods', 'institution', 'project_id']
        input_values = [PL, coresearchers, methods, institutions, project_id]

        filters = {}

        for x,y in zip(parameters, input_values):
            if y != None:
                filters[x] = y
        
        
        def match_criteria(row):
            results = []
            for col, values in filters.items():
                if col in df_projects.columns:
                    matches = [bool(re.search(fr'(^|_){v}(_|$)', row[col])) for v in values]
                    
                    results.append(all(matches) if match_all else any(matches))
            
            return all(results) if match_all else any(results)
        
        return df_projects[df_projects.apply(match_criteria, axis=1)]
    
    
    def get_white_standards(self):
        """Retrieve the registered white standards.

        Returns
        -------
        pandas dataframe
            It returns the ID and description of the white standards inside a two-columns dataframe.
        """

        if (Path(self.folder_db) / 'white_standards.txt').exists():
            df_references = pd.read_csv(Path(self.folder_db) / 'white_standards.txt')
            return df_references
        
        else:
            print(f'The file {Path(self.folder_db) / "white_standards.txt"} is not existing. Make sure to create one by running the function "create_DB" from the microfading package.')
            return

    
    def get_techniques(self):
        """Retrieve the registered techniques used to create the objects.

        Returns
        -------
        List
            It returns the techniques as strings inside a list.
        """
        
        techniques_filename = 'object_techniques.txt'
        
        if not (self.folder_db / techniques_filename).exists():
            print(f'Please create an empty file called "object_techniques.txt" in the the following folder: {self.folder_db}')
            return
        
        else:            
            techniques_df = pd.read_csv(self.folder_db / 'object_techniques.txt', header=None)
            techniques = sorted(list(techniques_df.values.flatten()), key=str.lower)             
            return techniques
        

    def get_types(self):
        """Retrieve the registered types of objects.

        Returns
        -------
        List
            It returns the types as strings inside a list.
        """
        
        types_filename = 'object_types.txt'
        
        if not (self.folder_db / types_filename).exists():
            print(f'Please create an empty file called "object_types.txt" in the the following folder: {self.folder_db}')
            return
        
        else:            
            types_df = pd.read_csv(self.folder_db / 'object_types.txt', header=None)
            types = sorted(list(types_df.values.flatten()), key=str.lower)              
            return types

    
    def update_projects(self, project_id:Union[str,list] = 'all', column:Optional[str] = None, new_value:Optional[str] = None, widgets:Optional[bool] = True):
        """Update the content of the projects_info.csv file.

        Parameters
        ----------
        
        project_id : Union[str,list], optional
            Select which project_id(s) (i.e. row(s)) should be updated, by default 'all'
            If you only wish to update the value for a single project, you can enter the project_id as a string.
            If you wish to update the value for several projects, enter the project_ids as strings inside a list
            When 'all', it will the update the value for all the projects.
        
        column : Optional[str], optional
            Select which column (parameter) should be updated, by default None
        
        new_value : Optional[str], optional
            New value to be written in the projects_info.csv file, by default None

        widgets : Optional[bool], optional
            Whether to display widgets to update the projects database file, by default True
            When False, you will have to pass in arguments for the project_id, the column, and the new_value
                    
        
        Returns
        -------
        ipywdigets or string
        If the parameter "widgets" is set to True, it will return several ipywidgets from which you you will be able to update the content of the projects database file. When "widgets" is set to False, it will automatically update the content of the file with requested input (project_id, column, and new_value) and it will return a string.
        """   

        if not (Path(self.folder_db) / 'projects_info.csv').exists():
            print(f'The file "projects_info.csv" is missing in your databases folder ({self.folder_db}). Either add the file to the folder or recreate the database.')

            return
        
        db_projects = self.get_projects().set_index('project_id')
        project_ids = tuple(db_projects.index)


        def update_project_info(project_id:str, parameter:str, new_value:str):

            if project_id not in project_ids:
                print(f'Error ! The project ID ({project_id}) is not registered in the projects_info.csv file.')
                return
                
            db_projects.loc[project_id, parameter] = new_value 
            db_projects.to_csv(Path(self.folder_db) / 'projects_info.csv',index=True)

    
        if widgets:
            
            wg_project_ids = ipw.Combobox(
                placeholder='Select a project id',
                options=project_ids,              
                description='Project id',
                ensure_option=False,
                disabled=False,
                layout=Layout(width="50%", height="30px"),
                style=style,
            )

            wg_project_columns = ipw.Dropdown(
                placeholder='Select a parameter',
                options= db_projects.columns,              
                description='Project parameter',
                ensure_option=False,
                disabled=False,
                layout=Layout(width="50%", height="30px"),
                style=style,
            )

            wg_new_value = ipw.Text(
                description='New value',
                placeholder='Enter a new value for the selected parameter',
                layout=Layout(width="50%", height="30px"),
                style=style,

            )

            wg_updating = ipw.Button(
                description='Update project',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',            
            )

            button_record_output = ipw.Output()

            def button_record_pressed(b):
                """
                Update the project info.
                """

                button_record_output.clear_output(wait=True)

                update_project_info(wg_project_ids.value, wg_project_columns.value, wg_new_value.value)


                with button_record_output:
                    
                    print(f'A new value "{wg_new_value.value}" has been successfully reassigned to the parameter "{wg_project_columns.value}" of the project "{wg_project_ids.value}".')

            wg_updating.on_click(button_record_pressed)

            display(wg_project_ids,wg_project_columns, wg_new_value)
            display(ipw.HBox([wg_updating, button_record_output]))



        else:    
        
            if project_id == 'all':
                project_id = db_projects.index

            elif isinstance(project_id, str):
                project_id = [project_id]

               
            for project in project_id:

                if project not in db_projects.index:
                    print(f'Error ! The project ID {project} is not registered in the projects_info.csv file.')
                    return
                
                db_projects.loc[project, column] = new_value         
            
            
            db_projects.to_csv(Path(self.folder_db) / 'projects_info.csv',index=True)
            print('projects_info.csv file successfully updated.')

        
    
    def update_objects(self, object_id:Union[str,list] = 'all', column:Optional[str] = None, new_value:Optional[str] = None,  widgets:Optional[bool] = True):
        """Update the content of the objects_info.csv file.

        Parameters
        ----------
        object_id : Union[str,list], optional
            Select which object_id(s) (i.e. row(s)) should be updated, by default 'all'
            If you only wish to update the value for a single object, you can enter the object_id as a string.
            If you wish to update the value for several objects, enter the object_ids as strings inside a list
            When 'all', it will the update the value for all the objects.
        
        column : Optional[str], optional
            Select which column (parameter) should be updated, by default None
        
        new_value : Optional[str], optional
            New value to be written in the objects_info.csv file, by default None
                
        widgets : Optional[bool], optional
            Whether to display widgets to update the objects database file, by default True
            When False, you will have to pass in arguments for the object_id, the column, and the new_value
                    
        
        Returns
        -------
        ipywdigets or string
        If the parameter "widgets" is set to True, it will return several ipywidgets from which you you will be able to update the content of the objects database file. When "widgets" is set to False, it will automatically update the content of the file with requested input (object_id, column, and new_value) and it will return a string.

        """  

        if not (Path(self.folder_db) / 'objects_info.csv').exists():
            print(f'The file "objects_info.csv" is missing in your databases folder ({self.folder_db}). Either add the file to the folder or recreate the database.')

            return
        
        db_objects = self.get_objects().set_index('object_id')
        object_ids = tuple(db_objects.index)


        def update_object_info(object_id:str, parameter:str, new_value:str):

            if object_id not in object_ids:
                print(f'Error ! The object ID ({object_id}) is not registered in the objects_info.csv file.')
                return
                
            db_objects.loc[object_id, parameter] = new_value 
            db_objects.to_csv(Path(self.folder_db) / 'objects_info.csv', index=True)


        if widgets:
            
            wg_object_ids = ipw.Combobox(
                placeholder='Select an object id',
                options=object_ids,              
                description='Object id',
                ensure_option=False,
                disabled=False,
                layout=Layout(width="50%", height="30px"),
                style=style,
            )

            wg_object_columns = ipw.Dropdown(
                placeholder='Select a parameter',
                options= db_objects.columns,              
                description='Object parameter',
                ensure_option=False,
                disabled=False,
                layout=Layout(width="50%", height="30px"),
                style=style,
            )

            wg_new_value = ipw.Text(
                description='New value',
                placeholder='Enter a new value for the selected parameter',
                layout=Layout(width="50%", height="30px"),
                style=style,

            )

            wg_updating = ipw.Button(
                description='Update Object',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',            
            )

            button_record_output = ipw.Output()

            def button_record_pressed(b):
                """
                Update the object info.
                """

                button_record_output.clear_output(wait=True)

                update_object_info(wg_object_ids.value, wg_object_columns.value, wg_new_value.value)


                with button_record_output:
                    
                    print(f'A new value "{wg_new_value.value}" has been successfully reassigned to the parameter "{wg_object_columns.value}" of the object "{wg_object_ids.value}".')

            wg_updating.on_click(button_record_pressed)

            display(wg_object_ids,wg_object_columns, wg_new_value)
            display(ipw.HBox([wg_updating, button_record_output]))


        else:        

            if object_id == 'all':
                object_id = db_objects.index
            elif isinstance(object_id, str):
                object_id = [object_id]

               
            for object in object_id:

                if object not in db_objects.index:
                    print(f'Error ! The object ID {object} is not registered in the objects_info.csv file.')
                    return
                
                db_objects.loc[object, column] = new_value         
            
            
            db_objects.to_csv(Path(self.folder_db) / 'objects_info.csv', index=True)
            print('objects_info.csv file successfully updated.')


    def delete_creators(self):
        """Remove one of several creators from the database file.
        """

        creators_df = self.get_creators()
        creators_list = [f'{x[0]}, {x[1]}' if isinstance(x[1],str) else x[0] for x in creators_df.values]       

        wg_creators = ipw.SelectMultiple(          
            options=  creators_list,
            description='Creators',
            rows=10             
        )

        deleting = ipw.Button(
            description='Delete creators',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        
        def button_delete_pressed(b):
            """
            Delete the institution info in the institutions.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            creators_filename = 'object_creators.txt'
            creators_df = self.get_creators()            
                            
            for creator in list(wg_creators.value):
                                    
                if ',' in creator:
                    surname = creator.split(',')[0].strip()
                    name = creator.split(',')[1].strip()
                    creators_df = creators_df.drop(creators_df[(creators_df['surname'] == surname) & (creators_df['name'] == name)].index)

                else:                                   
                    creators_df = creators_df.drop(creators_df[(creators_df['surname'] == creator)].index)

                        
            creators_df.to_csv(self.folder_db / creators_filename, index=False)

            with button_delete_output:
                print(f'Creators deleted: {wg_creators.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(wg_creators)
        display(ipw.HBox([deleting, button_delete_output]))  


    def delete_devices(self, ID:Optional[str] = None):
        """Remove devices from the database file.

        Parameters
        ----------
        ID : Optional[str,list], optional
            ID of the devices, by default None
        """

        devices_ID = list(self.get_devices()['ID'])

        if ID == None:
            ID = [devices_ID[0]]

        elif isinstance(ID,str):
            ID = [ID]

     
        wg_devices = ipw.SelectMultiple(        
            value=ID,
            options=  devices_ID,
            description='devices ID', 
            rows=10            
        )


        deleting = ipw.Button(
            description='Delete devices',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        
        def button_delete_pressed(b):
            """
            Delete the institution info in the institutions.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            devices_filename = 'devices.txt'
            df_devices = self.get_devices()

            for id in list(wg_devices.value):
                df_devices = df_devices.drop(df_devices[df_devices['ID'] == id].index)

            df_devices.to_csv(self.folder_db / devices_filename, index=False)

            with button_delete_output:
                print(f'Devices deleted: {wg_devices.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(wg_devices)
        display(ipw.HBox([deleting, button_delete_output]))  


    def delete_institutions(self, acronym:Optional[str] = None):
        """Remove an institution from the database file.

        Parameters
        ----------
        acronym : Optional[str], optional
            Acronym of the institution, by default None
        """

        if acronym == None:
            acronym = 'Select an acronym'

        df_institutions = self.get_institutions()
        institution_acronyms = list(df_institutions['acronym'])

        if acronym not in  ['Select an acronym'] + institution_acronyms:
            print(f'The acronym you entered "{acronym}" has not been registered in the database.')
            acronym = 'Select an acronym'

        wg_acronym = ipw.Dropdown(        
            value=acronym,
            options=  ['Select an acronym'] + institution_acronyms,
            description='Acronym',
            style=style,
            layout=Layout(width="17%", height="30px")        
        )

        wg_institution_name = ipw.Text(
            value='',
            description='',
            disabled=False         
        )

        deleting = ipw.Button(
            description='Delete institution',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()


        def change_acronym(change):            
            new_acronym = change.new
            name = df_institutions.query(f'acronym == "{new_acronym}"')['name'].values[0]            
            wg_institution_name.value = name

                    
        def button_delete_pressed(b):
            """
            Delete the institution info in the institutions.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            institutions_filename = 'institutions.txt'
            df_institutions = self.get_institutions()
            df_institutions = df_institutions.drop(df_institutions[df_institutions['acronym'] == wg_acronym.value].index)

            df_institutions.to_csv(self.folder_db / institutions_filename, index=False)

            with button_delete_output:
                print(f'Institution deleted: {wg_acronym.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)
        wg_acronym.observe(change_acronym, names='value')

        # Display the widgets
        display(ipw.HBox([wg_acronym, wg_institution_name]))
        display(ipw.HBox([deleting, button_delete_output]))


    def delete_lamps(self, id:Optional[str] = None):
        """Remove a lamp from the database file.

        Parameters
        ----------
        id : Optional[str], optional
            ID number of the lamp, by default None
        """

        if id == None:
            id = 'Select an ID'

        df_lamps = self.get_lamps()
        id_list = list(df_lamps['ID'])

        if id not in  ['Select an ID'] + id_list:
            print(f'The ID you entered "{id}" has not been registered in the database.')
            id = 'Select an ID'

        wg_id = ipw.Dropdown(        
            value=id,
            options=['Select an ID'] + id_list,
            description='ID',   
            layout=Layout(width="15%", height="30px"),
            style=style,          
        )
        
        wg_description = ipw.Text(
            value='',
            description='',
            disabled=False,
            layout=Layout(width="70%", height="30px"),
            style=style,
        )           

        deleting = ipw.Button(
            description='Delete lamp',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()


        def change_id(change):
            new_id = change.new
            description = df_lamps.query(f'ID == "{new_id}"')['description'].values[0]            
            wg_description.value = description
        

        def button_delete_pressed(b):
            """
            Delete the lamp info in the lamps.txt file.
            """

            button_delete_output.clear_output(wait=True)

            lamps_folder = self.folder_db
            lamps_filename = 'lamps.txt'

            df_lamps = self.get_lamps()
            df_lamps = df_lamps.drop(df_lamps[df_lamps['ID'] == wg_id.value].index)

            df_lamps.to_csv(lamps_folder/lamps_filename, index=False)

            with button_delete_output:
                print(f'ID {wg_id.value} deleted.')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)
        wg_id.observe(change_id, names='value')

        # Display the widgets
        display(ipw.HBox([wg_id, wg_description]))
        display(ipw.HBox([deleting, button_delete_output]))
    
    
    def delete_materials(self):
        """Remove one or several object materials from the database file.
        """
        
        materials = self.get_materials()        

        wg_materials = ipw.SelectMultiple(            
            options=  materials,
            description='Materials',  
            rows=10,           
        )

        deleting = ipw.Button(
            description='Delete materials',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        
        def button_delete_pressed(b):
            """
            Delete the materials in the object_materials.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            materials_filename = 'object_materials.txt'
            materials = self.get_materials()

            for material in list(wg_materials.value):
                materials.remove(material)
            
            pd.Series(materials).to_csv(self.folder_db / materials_filename, index=False, header=False)

            with button_delete_output:
                print(f'Materials deleted: {wg_materials.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(wg_materials)
        display(ipw.HBox([deleting, button_delete_output]))
    
    
    def delete_methods(self, acronym:Optional[str] = None):
        """Remove an analytical method from the database file.

        Parameters
        ----------
        acronym : Optional[str], optional
            Acronym of the method, by default None
        """

        if acronym == None:
            acronym = 'Select an acronym'

        df_methods = self.get_methods()
        method_acronyms = list(df_methods['acronym'])

        if acronym not in  ['Select an acronym'] + method_acronyms:
            print(f'The acronym you entered "{acronym}" has not been registered in the database.')
            acronym = 'Select an acronym'

        wg_acronym = ipw.Dropdown(        
            value=acronym,
            options=  ['Select an acronym'] + method_acronyms,
            description='Acronym',
            style=style,
            layout=Layout(width="17%", height="30px")        
        )

        wg_method_name = ipw.Text(
            value='',
            description='',
            disabled=False         
        )

        deleting = ipw.Button(
            description='Delete method',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()


        def change_acronym(change):            
            new_acronym = change.new
            name = df_methods.query(f'acronym == "{new_acronym}"')['name'].values[0]            
            wg_method_name.value = name

                    
        def button_delete_pressed(b):
            """
            Delete the method info in the analytical_methods.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            methods_filename = 'analytical_methods.txt'
            df_methods = self.get_methods()
            df_methods = df_methods.drop(df_methods[df_methods['acronym'] == wg_acronym.value].index)

            df_methods.to_csv(self.folder_db / methods_filename, index=False)

            with button_delete_output:
                print(f'Method deleted: {wg_acronym.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)
        wg_acronym.observe(change_acronym, names='value')

        # Display the widgets
        display(ipw.HBox([wg_acronym, wg_method_name]))
        display(ipw.HBox([deleting, button_delete_output]))

    
    def delete_objects(self, object_id:Optional[str] = None):
        """Remove a  object from the database file.

        Parameters
        ----------
        object_id : Optional[str], optional
            ID number of the object, by default None
        """

        if object_id == None:
            object_id = 'Select an object ID'

        object_ids = sorted(list(self.get_objects()['object_id']), key=str.lower)

        if object_id not in  ['Select an object ID'] + object_ids:
            print(f'The object ID you entered "{object_id}" has not been registered in the database.')
            object_id = 'Select an object ID'

        objectId_widget = ipw.Dropdown(        
            value=object_id,
            options=['Select an object ID'] + object_ids,
            description='Object ID',             
        )


        deleting = ipw.Button(
            description='Delete object',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        


        def button_delete_pressed(b):
            """
            Delete the object info in the objects_info.csv file.
            """

            button_delete_output.clear_output(wait=True)

            objects_folder = self.folder_db
            objects_filename = 'objects_info.csv'

            df_objects = self.get_objects()
            df_objects = df_objects.drop(df_objects[df_objects['object_id'] == objectId_widget.value].index)

            df_objects.to_csv(objects_folder/objects_filename, index=False)

            with button_delete_output:
                print(f'Object deleted: {objectId_widget.value}')



        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(objectId_widget)
        display(ipw.HBox([deleting, button_delete_output]))

    
    def delete_projects(self, project_id:Optional[str] = None):
        """Remove a  project from the database file.

        Parameters
        ----------
        project_id : Optional[str], optional
            ID number of the project, by default None
        """

        if project_id == None:
            project_id = 'Select a project ID'

        project_ids = list(self.get_projects()['project_id'])

        if project_id not in  ['Select a project ID'] + project_ids:
            print(f'The project ID you entered "{project_id}" has not been registered in the database.')
            project_id = 'Select a project ID'

        projectId_widget = ipw.Dropdown(        
            value=project_id,
            options=['Select a project ID'] + project_ids,
            description='Project ID',             
        )


        deleting = ipw.Button(
            description='Delete project',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        


        def button_delete_pressed(b):
            """
            Delete the project info in the projects_info.csv file.
            """

            button_delete_output.clear_output(wait=True)

            projects_folder = self.folder_db
            projects_filename = 'projects_info.csv'

            df_projects = self.get_projects()
            df_projects = df_projects.drop(df_projects[df_projects['project_id'] == projectId_widget.value].index)

            df_projects.to_csv(projects_folder/projects_filename, index=False)

            with button_delete_output:
                print(f'Project deleted: {projectId_widget.value}')



        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(projectId_widget)
        display(ipw.HBox([deleting, button_delete_output]))
    
    
    def delete_techniques(self):
        """Remove one or several object techniques from the database file.
        """
        
        techniques = self.get_techniques()        

        wg_techniques = ipw.SelectMultiple(            
            options=  techniques,
            description='Techniques',  
            rows=10,           
        )

        deleting = ipw.Button(
            description='Delete techniques',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        
        def button_delete_pressed(b):
            """
            Delete the techniques in the object_techniques.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            techniques_filename = 'object_techniques.txt'
            techniques = self.get_techniques()

            for technique in list(wg_techniques.value):
                techniques.remove(technique)
            
            pd.Series(techniques).to_csv(self.folder_db / techniques_filename, index=False, header=False)

            with button_delete_output:
                print(f'Techniques deleted: {wg_techniques.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(wg_techniques)
        display(ipw.HBox([deleting, button_delete_output]))


    def delete_types(self):
        """Remove one or several object types from the database file.
        """
        
        types = self.get_types()        

        wg_types = ipw.SelectMultiple(            
            options=  types,
            description='Types',  
            rows=10,           
        )

        deleting = ipw.Button(
            description='Delete types',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()

        
        def button_delete_pressed(b):
            """
            Delete the types in the object_types.txt file.
            """

            button_delete_output.clear_output(wait=True)
            
            types_filename = 'object_types.txt'
            types = self.get_types()

            for type in list(wg_types.value):
                types.remove(type)
            
            pd.Series(types).to_csv(self.folder_db / types_filename, index=False, header=False)

            with button_delete_output:
                print(f'Types deleted: {wg_types.value}')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)

        # Display the widgets
        display(wg_types)
        display(ipw.HBox([deleting, button_delete_output]))
       

    def delete_users(self,initials:Optional[str] = None):
        """Remove a user from the database file.

        Parameters
        ----------
        initials : Optional[str], optional
            Initials of the user, by default None
        """

        if initials == None:
            initials = 'Select the initials'

        df_users = self.get_users()
        initials_list = list(df_users['initials'])

        if initials not in  ['Select the initials'] + initials_list:
            print(f'The initials you entered "{initials}" has not been registered in the database.')
            initials = 'Select the initials'

        wg_initials = ipw.Dropdown(        
            value=initials,
            options=['Select the initials'] + initials_list,
            description='Initials',    
            layout=Layout(width="20%", height="30px"),
            style=style,         
        )
        
        wg_name_surname = ipw.Text(
            value='',
            description='',
            disabled=False,
            layout=Layout(width="30%", height="30px"),
            style=style,
        )           

        deleting = ipw.Button(
            description='Delete user',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()


        def change_initials(change):
            new_initials = change.new
            name = df_users.query(f'initials == "{new_initials}"')['name'].values[0]
            surname = df_users.query(f'initials == "{new_initials}"')['surname'].values[0]
            wg_name_surname.value = f'{name} {surname}'

        

        def button_delete_pressed(b):
            """
            Delete the person info in the users_info.txt file.
            """

            button_delete_output.clear_output(wait=True)

            users_folder = self.folder_db
            users_filename = 'users_info.txt'

            df_users = self.get_users()
            df_users = df_users.drop(df_users[df_users['initials'] == wg_initials.value].index)

            df_users.to_csv(users_folder/users_filename, index=False)

            with button_delete_output:
                print(f'User {wg_initials.value} deleted.')



        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)
        wg_initials.observe(change_initials, names='value')

        # Display the widgets
        display(ipw.HBox([wg_initials, wg_name_surname]))
        display(ipw.HBox([deleting, button_delete_output]))


    def delete_white_standards(self,id:Optional[str] = None):
        """Remove a white standard from the database file.

        Parameters
        ----------
        id : Optional[str], optional
            ID number of the white standard, by default None
        """

        if id == None:
            id = 'Select an ID'

        df_standards = self.get_white_standards()
        id_list = list(df_standards['ID'])

        if id not in  ['Select an ID'] + id_list:
            print(f'The ID you entered "{id}" has not been registered in the database.')
            id = 'Select an ID'

        wg_id = ipw.Dropdown(        
            value=id,
            options=['Select an ID'] + id_list,
            description='ID',   
            layout=Layout(width="15%", height="30px"),
            style=style,          
        )
        
        wg_description = ipw.Text(
            value='',
            description='',
            disabled=False,
            layout=Layout(width="70%", height="30px"),
            style=style,
        )           

        deleting = ipw.Button(
            description='Delete standard',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )        
            
        button_delete_output = ipw.Output()


        def change_id(change):
            new_id = change.new
            description = df_standards.query(f'ID == "{new_id}"')['description'].values[0]            
            wg_description.value = description
        

        def button_delete_pressed(b):
            """
            Delete the standard info in the white_standards.txt file.
            """

            button_delete_output.clear_output(wait=True)

            standards_folder = self.folder_db
            standards_filename = 'white_standards.txt'

            df_standards = self.get_white_standards()
            df_standards = df_standards.drop(df_standards[df_standards['ID'] == wg_id.value].index)

            df_standards.to_csv(standards_folder/standards_filename, index=False)

            with button_delete_output:
                print(f'ID {wg_id.value} deleted.')


        # Link the widget button to the function
        deleting.on_click(button_delete_pressed)
        wg_id.observe(change_id, names='value')

        # Display the widgets
        display(ipw.HBox([wg_id, wg_description]))
        display(ipw.HBox([deleting, button_delete_output]))  
