def pufiles():
    '''
    tkinter GUI: Prompts the User to choose one/some Files
    Returns a list of all file-paths
    '''
    from tkinter.filedialog import askopenfilenames
    names = list(askopenfilenames(initialdir=".",
                            filetypes =(("All Files","*.*"),),
                            title = "Choose some files."
                            ))
    try:
        global imagetargets
        imagetargets = names
        return names
    except:
        return False

def pufile():
    '''
    tkinter GUI: Prompts the User to choose one Files
    Returns a string of the file-path
    '''
    from tkinter.filedialog import askopenfilename
    name = askopenfilename(initialdir=".",
                           filetypes =(("All Files","*.*"),),
                           title = "Choose a file."
                           )
    try:
        global imagetarget
        imagetarget = name
        return name
    except:
        return False
    
def pudir():
    '''
    tkinter GUI: Prompts the User to choose a Directory (imagebase)
    Returns a string of the Dir-path
    '''
    from tkinter.filedialog import askdirectory
    name = askdirectory(initialdir=".",
                           title = "Choose a folder."
                           )
    try:
        global imagebase
        imagebase = name
        return name
    except:
        return False

def pusavefile():
    from tkinter.filedialog import asksaveasfilename
    name = asksaveasfilename(initialdir=".",filetypes =(("All Files","*.*"),),
                           title = "Choose a Filename."
                           )
    try:
        return name
    except:
        return False