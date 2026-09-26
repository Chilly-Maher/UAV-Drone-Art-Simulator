Steps to use:
1. Place desired files inside input folder, located in drone_art/input.
The usable static files are:
  - .png
  - .jpg
  - .jpeg

For the static files you will want to input your images frame by frame (ie each image is one frame).
The usable video files are:
  - .mp4
  - .mov
  - -m4v
  - .avi
  - .mkv

These work about how you would expect.

2. Run main.py. If you do not have all the packages installed already, type this into the terminal: pip install pillow imageio imageio-ffmpeg av numpy
   
3. Open the output folder, located in drone_art/output
Here you will find each individual frame printed out as "filename_drone.jpg", as well as animation.gif and symbol_stream.csv.
  - The individual frames are not really useful, save for tweaking purposes
  - animation.gif is the final product. If any tweaks need to be made, check the config file, the comments are quite thorough
  - symbol_stream.csv very quickly hits the maximum cells that excel has to offer if you go above 104 frames. You can go beyond this in the configs

4. To reuse:
   -  clear out the output folder (not strictly necessary, but it gets messy quickly. I would recommend shift+del to not have 1159 images of a cat in your recycle bin).
   -  **Close the excel sheet if not done already.** Program won't run because it can't write to an in-use file. 
