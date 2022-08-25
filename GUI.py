from tkinter import Tk, Label, Button, Entry, END, W, filedialog, messagebox, PhotoImage

import chart_studio.plotly as py
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import Clustering
import PreProcessing


class GUI:

    def __init__(self, master):
        """ the constructor of the GUI class. includes all buttons, entry and the layout of the window.
            includes the fields of the data that need to be saved - the data we read from the file,
            the file pth and directory and flag to know if we finished all the preparations
            before running the pre-process and ckuster in the data.
            :param: master  - is the main window of the GUI
            :returns:   """

        self.master = master
        master.title("K Means Clustering")

        # key and user to save the choropleth map
        self.key = 'eMWqR1OTGq8p5Ar8v8X8'
        self.user = "nono20794"

        # flags to know if all inputs are correct
        self.cluster_done = False
        self.runs_done = False
        self.pre_process_done = False
        self.error_msg = ""

        # fields to save the inputs and data
        self.file_path = ""
        self.dir = ""
        self.data = None
        self.new_data_after_processing = None
        self.number_of_clusters = 0
        self.number_of_runs = 0
        self.pre_process_handler = PreProcessing.PreProcessing()
        self.cluster_handler = Clustering.Clustering()

        # figures to show the scatter plot and map
        self.canvas_cluster = None
        self.image_map = None

        # input entry
        self.entry_clusters = Entry(master, width=20)
        self.entry_runs = Entry(master, width=20)

        # buttons
        self.browse_button = Button(master, text="Browse",
                                    command=lambda: self.browse_file())
        self.pre_process_button = Button(master, text="Pre-process",
                                         command=lambda: self.pre_process())
        self.cluster_button = Button(master, text="Cluster", command=lambda: self.cluster())

        # labels
        self.file_label = Label(master, text="Open Path:")
        self.file_browse_label = Label(master, text="File Path:", background="white", width=60, height=1,
                                       borderwidth=0.5,
                                       relief="solid")
        self.cluster_label = Label(master, text="Number of clusters k:")
        self.runs_label = Label(master, text="Number of runs:")
        self.image_label = Label(self.master, image=self.image_map)

        # layout
        self.file_label.grid(row=0, column=0, sticky=W)
        self.browse_button.grid(row=0, column=2, padx=5)
        self.file_browse_label.grid(row=0, column=1)

        self.cluster_label.grid(row=1, column=0, sticky=W)
        self.entry_clusters.grid(row=1, column=1, sticky=W)

        self.runs_label.grid(row=2, column=0, sticky=W)
        self.entry_runs.grid(row=2, column=1, sticky=W)

        self.pre_process_button.grid(row=4, column=1)
        self.cluster_button.grid(row=5, column=1)

    def check_clusters(self):
        """ this methode gets a new entry for number of clusters and verify the input.
            number of clusters should be int and bigger than zero.
            :param:
            :returns:  error message if the input is invalid occurred """
        new_k = self.entry_clusters.get()
        try:
            self.number_of_clusters = int(new_k)
            if self.number_of_clusters > 0:
                self.cluster_done = True
                return ""
            else:
                self.number_of_clusters = 0
                self.cluster_done = False
                self.pre_process_done = False
                return "number of clusters should be larger than zero"
                # return False
        except ValueError:
            self.number_of_clusters = 0
            self.cluster_done = False
            self.pre_process_done = False
            return " number of clusters should be an integer"
            # return False

    def check_runs(self):
        """ this methode gets a new entry for number of runs of the algorithm and verify the input.
            number of runs should be int and bigger than zero.
            :param:
            :returns: error message if the input is invalid occurred"""
        new_runs = self.entry_runs.get()
        try:
            self.number_of_runs = int(new_runs)
            if self.number_of_runs > 0:
                self.runs_done = True
                return ""
                # return True
            else:
                self.number_of_runs = 0
                self.runs_done = False
                self.pre_process_done = False
                return "number of runs should be larger than zero"
                # return False
        except ValueError:
            self.number_of_runs = 0
            self.runs_done = False
            self.pre_process_done = False
            return "nuber of runs should be an integer"
            # return False

    def browse_file(self):
        """ this methode gets a new entry for the file to process.
            a pop-up window would appear to the user to choose a file from its computer.
            the methode would store the file path, save its directory to save future outputs in the same folder.
            :param
            :returns:"""

        # if the user try the algorithm again and change the inputs, will delete all figures in the window
        if self.canvas_cluster is not None:
            try:
                self.canvas_cluster.get_tk_widget().grid_forget()
            except AttributeError:
                pass
        if self.image_map is not None:
            try:
                self.image_label.grid_forget()
            except Exception:
                pass

        try:
            self.file_browse_label.config(text="File Path:")
            self.pre_process_done = False

            filename = filedialog.askopenfilename(initialdir="/",
                                                  title="Select a File",
                                                  filetypes=(("Excel files",
                                                              "*.xlsx*"),
                                                             ("all files",
                                                              "*.*")))
            if not filename:  # if a file was not selected , or a wrong file was selected
                self.file_path = "ERROR"
                self.dir = ""
                self.error_msg = "the file path is empty, choose a new file"
            else:
                self.file_browse_label.config(text="File Path: " + filename)
                self.file_path = filename
                self.data = pd.read_excel(self.file_path)
                if self.data.empty:
                    raise ValueError("emptyData")
                self.pre_process_handler.add_data(self.data)
                file_split = self.file_path.rsplit('/', 1)
                self.dir = file_split[0]  # save the directory of the file
        except (pd.errors.EmptyDataError, ValueError):
            self.file_path = "ERROR"
            self.dir = ""
            self.error_msg = "the file is empty"
        except Exception as err:
            self.file_path = "ERROR"
            self.dir = ""
            self.error_msg = str(err)

    def pre_process(self):
        """ this methode is used to process the data from the user.
            will call the pre-process handler to process the data : fill na values, Standardization and data collection
            the methode will only start when the user entered all the inputs correctly
            will show error messages if the inputs are incorrect, or while during the process was an error
            :param
            :returns:"""

        # if the user try the algorithm again and change the inputs, will delete all figures in the window
        if self.canvas_cluster is not None:
            try:
                self.canvas_cluster.get_tk_widget().grid_forget()
            except AttributeError:
                pass
        if self.image_map is not None:
            try:
                self.image_label.grid_forget()
            except Exception:
                pass

        if self.file_path == 'ERROR':
            messagebox.showerror("K Means Clustering", "The file you have chosen is invalid, choose a new file: "+self.error_msg)
            self.pre_process_done = False
            return

        # check valid inputs for clusters and runs
        err_k = self.check_clusters()
        err_runs = self.check_runs()

        if not self.cluster_done:
            messagebox.showerror("K Means Clustering", "number of clusters is invalid\n " + err_k)
            self.pre_process_done = False
            return
        if not self.runs_done:
            messagebox.showerror("K Means Clustering", "number of runs is invalid\n " + err_runs)
            self.pre_process_done = False
            return
        try:  # call the pre_process handler to run the functions
            self.pre_process_handler.fill_na()
            self.pre_process_handler.standardization()
            self.new_data_after_processing = self.pre_process_handler.data_collection()
        except Exception as arr:
            messagebox.showerror("K Means Clustering", 'Error while pre  processing the data: ' + str(arr))
            return
        # finish pre-process
        self.pre_process_done = True
        messagebox.showinfo('K Means Clustering', "Preprocessing completed successfully!")

    def cluster(self):
        """ this methode is used to cluster the data from the user.
            will call the cluster handler to cluster the data: will calculate the k-means of the data
                and create the scatter plot and the choropleth_map
            will save the map image to the file folder and save the new dataset to an Excel file
            the methode will only start if the pre-process was done correctly
            will show error messages if the inputs are incorrect, or while during the process was an error
            :param
            :returns:"""

        # if the user try the algorithm again and change the inputs, will delete all figures in the window
        if self.canvas_cluster is not None:
            try:
                self.canvas_cluster.get_tk_widget().grid_forget()
            except AttributeError:
                pass
        if self.image_map is not None:
            try:
                self.image_label.grid_forget()
            except Exception:
                pass

        # check if changes are made between running the pre process and clustering
        err_k = self.check_clusters()
        err_runs = self.check_runs()

        if not self.pre_process_done:
            messagebox.showerror("K Means Clustering", 'please complete the pre - process first ')
            return

        try:  # call the cluster handler to run the functions
            self.cluster_handler.add_k_runs_data(self.number_of_clusters, self.number_of_runs,
                                                 self.new_data_after_processing)
            fig = self.cluster_handler.k_means()
            self.new_data_after_processing.to_excel(self.dir + "/new_clustered_Dataset.xlsx")

            # show the figure in the window to the user
            self.canvas_cluster = FigureCanvasTkAgg(fig, master=self.master)
            self.canvas_cluster.get_tk_widget().grid(row=6, column=1, padx=10, pady=10)
            self.canvas_cluster.draw()
        except Exception as err:
            messagebox.showerror("K Means Clustering", 'Error while clustering and plotting the data:\n ' + str(err))
            return

        try:
            choropleth_map = self.cluster_handler.create_map()  # crate the map
            py.sign_in(self.user, self.key)
            file_name = self.dir + '/map.png'
            py.image.save_as(choropleth_map, filename=file_name)  # save the map image to the folder

            # show the figure in the window to the user
            self.image_map = PhotoImage(file=file_name)
            self.image_label.config(image=self.image_map)
            self.image_label.grid(row=6, column=2, padx=10, pady=10)
            self.master.eval('tk::PlaceWindow . center')
        except Exception as err:
            messagebox.showerror("K Means Clustering", "error while creating the choropleth_map:\n" + str(err))
            return
        messagebox.showinfo("K Means Clustering", "Clustering completed successfully!")


root = Tk()
my_gui = GUI(root)
root.mainloop()
