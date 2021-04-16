# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os


class PhotoBoothApp:
	def __init__(self, vs, outputPath):
		# store the video stream object and output path, then initialize
		# the most recently read frame, thread for reading frames, and
		# the thread stop event
		self.vs = vs
		self.outputPath = outputPath
		self.frame = None
		self.thread = None
		self.stopEvent = None

		# initialize the root window and image panel
		self.root = tki.Tk()
		self.panel = None
		self.panel_o = None
		self.panel_c = None

		# setting
		self.root.geometry("1300x700")  # screen

		# create a button, that when pressed, will take the current
		# frame and save it to file
		# - main photo
		btn = tki.Button(self.root, text="Snapshot!",
						 command=self.takeSnapshot)
		btn.pack(side="bottom", fill="both", expand="yes", padx=10,
				 pady=10)

		# - compare photo
		btn = tki.Button(self.root, text="Compare!",
						 command=self.takeSnapshot_compare)
		btn.pack(side="bottom", fill="both", expand="yes", padx=10,
				 pady=10)

		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PyImageSearch PhotoBooth")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():
				# grab the frame from the video stream and resize it to
				# have a maximum width of 300 pixels
				self.frame = self.vs.read()
				self.frame = imutils.resize(self.frame, width=300)

				# OpenCV represents images in BGR order; however PIL
				# represents images in RGB order, so we need to swap
				# the channels, then convert to PIL and ImageTk format
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)

				# if the panel is not None, we need to initialize it
				# if self.canvas is None:
				self.panel = tki.Canvas(cursor="cross")
				self.panel.pack()
					# self.panel = tki.Label(image=image, cursor="cross")
					# self.panel.image = image
					# self.panel.pack(side="left", padx=10, pady=10)
				self.panel.create_image(0, 0, image=image, anchor=tki.NW)
				# otherwise, simply update the panel
				# else:
				# 	pass
					# self.panel.configure(image=image)
					# self.panel.image = image

				# **additional
				self.x = self.y = 0
				# self.canvas = Canvas(self, cursor="cross")

				# self.sbarv = Scrollbar(self, orient=VERTICAL)
				# self.sbarh = Scrollbar(self, orient=HORIZONTAL)
				# self.sbarv.config(command=self.canvas.yview)
				# self.sbarh.config(command=self.canvas.xview)

				# self.canvas.config(yscrollcommand=self.sbarv.set)
				# self.canvas.config(xscrollcommand=self.sbarh.set)

				# self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
				# self.sbarv.grid(row=0, column=1, stick=N + S)
				# self.sbarh.grid(row=1, column=0, sticky=E + W)

				self.panel.bind("<ButtonPress-1>", self.on_button_press)
				self.panel.bind("<B1-Motion>", self.on_move_press)
				self.panel.bind("<ButtonRelease-1>", self.on_button_release)

				self.rect = None
				self.start_x = None
				self.start_y = None

		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")

	def takeSnapshot(self):
		# grab the current timestamp and use it to construct the
		# output path
		ts = datetime.datetime.now()
		filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		p = os.path.sep.join((self.outputPath, filename))

		# save the file
		cv2.imwrite(p, self.frame.copy())

		if os.path.exists(p):
			self.show_image(str(p), "original")
			print("saved/show: ", p)
		else:
			print("waiting for image ..")

	def takeSnapshot_compare(self):
		# grab the current timestamp and use it to construct the
		# output path
		ts = datetime.datetime.now()
		filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		p = os.path.sep.join((self.outputPath, filename))

		# save the file
		cv2.imwrite(p, self.frame.copy())

		if os.path.exists(p):
			self.show_image(str(p), "compare")
			print("saved/show: ", p)
		else:
			print("waiting for image ..")

	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("[INFO] closing...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()

	# own create fn
	def show_image(self, file_path, mode):
		load_img = Image.open(file_path)
		if mode == "original":
			size = [300, 220, 200, 10]
			load_img = load_img.resize((size[0], size[1]), Image.ANTIALIAS)
			image = ImageTk.PhotoImage(load_img)
			self.panel_o = tki.Label(image=image)
			self.panel_o.image = image
			self.panel_o.pack(side="left", padx=size[2], pady=size[3])
		elif mode == "compare":
			size = [300, 220, 10, 10]
			load_img = load_img.resize((size[0], size[1]), Image.ANTIALIAS)
			image = ImageTk.PhotoImage(load_img)
			self.panel_c = tki.Label(image=image)
			self.panel_c.image = image
			self.panel_c.pack(side="right", padx=size[2], pady=size[3])

	def on_button_press(self, event):
		# save mouse drag start position
		self.start_x = self.panel.canvasx(event.x)
		self.start_y = self.panel.canvasy(event.y)

		# create rectangle if not yet exist
		if not self.rect:
			self.rect = self.panel.create_rectangle(self.x, self.y, 1, 1, outline='red')

	def on_move_press(self, event):
		curX = self.panel.canvasx(event.x)
		curY = self.panel.canvasy(event.y)

		w, h = self.panel.winfo_width(), self.panel.winfo_height()
		if event.x > 0.9 * w:
			self.panel.xview_scroll(1, 'units')
		elif event.x < 0.1 * w:
			self.panel.xview_scroll(-1, 'units')
		if event.y > 0.9 * h:
			self.panel.yview_scroll(1, 'units')
		elif event.y < 0.1 * h:
			self.panel.yview_scroll(-1, 'units')

		# expand rectangle as you drag the mouse
		self.panel.coords(self.rect, self.start_x, self.start_y, curX, curY)

	def on_button_release(self, event):
		pass
