SMART AUTO DOWNLOAD SORTER (Windows 10/11)

WHAT IT DOES
- Watches your browser's Downloads folder.
- Leaves files already present when the program starts untouched.
- Reads the label after the final underscore and before the extension.
- Sends known class labels to the matching existing course folder under S:\Year 2\Sem 3.
- Sends an unknown/new label to a new folder on your Desktop.
- Creates a file-type subfolder (PDF, Excel, Word, etc.) when missing.
- Waits for downloads to finish and avoids overwriting same-named files.

YOUR DESTINATIONS
Known class labels use your existing course folders:
  _gis.pdf      -> S:\Year 2\Sem 3\Introduction to Geographical Information Systems\PDF\
  _gis.xlsx     -> S:\Year 2\Sem 3\Introduction to Geographical Information Systems\Excel\
  _fsr.pdf      -> S:\Year 2\Sem 3\Foundations of Social Research\PDF\
  _matlab.docx  -> S:\Year 2\Sem 3\Introduction to MATLAB\Word\
  _sdg.csv      -> S:\Year 2\Sem 3\Sustainable Development Analytics (STEM)\Excel\

Configured known tags:
  ctp, critical, philosophy, criticalthinking -> Critical thinking and Philosophy
  fsr, research, socialresearch, foundations -> Foundations of Social Research
  gis, qgis, geography, geographicalinformation -> Introduction to Geographical Information Systems
  matlab -> Introduction to MATLAB
  r, rprogramming -> Introduction to R programming
  db, database, databases -> Micro and Macro Databases (STEM)
  nmd, disaster, disasters, naturaldisasters -> Natural and Man-made Disasters
  sdg, sda, sustainability, sustainabledevelopmentanalytics -> Sustainable Development Analytics (STEM)
  tsw, writing, scientificwriting -> Technical and Scientific Writing

If a new tag is used, for example climate:
  report_climate.pdf -> Desktop\Climate\PDF\report_climate.pdf
  data_climate.xlsx -> Desktop\Climate\Excel\data_climate.xlsx

If a known mapped course folder cannot be found under S:\Year 2\Sem 3, the program leaves the file in Downloads and logs an error. It does not silently create a wrong course folder on the S: drive.

NAMING RULE
The last underscore-delimited part before the extension is the label:
  lecture_notes_gis.pdf
  survey_gis.xlsx
  essay_writing.docx
Files without a label after the final underscore are left in Downloads.
CSV files go in Excel by default. Unknown extensions go under Other.

HOW TO START
1. Extract this ZIP to a permanent folder, such as Documents\AutoDownloadSorter.
2. Double-click start_auto_sorter.bat.
3. Keep the terminal window open while you want automatic sorting active.
4. Test using a newly downloaded file named demo_gis.pdf.
5. Press Ctrl+C in the terminal to stop the sorter.

RUN AT WINDOWS SIGN-IN (OPTIONAL)
1. Keep the extracted folder in a permanent location.
2. Press Win+R, type shell:startup, and press Enter.
3. Create a shortcut to start_auto_sorter.bat in the Startup folder.
4. Windows will start the sorter when you sign in. The terminal window stays open.

CUSTOMIZATION
- Edit DOWNLOADS_DIR if your browser uses a different download location.
- Edit SEMESTER_ROOT if your semester folders are stored somewhere else.
- Add or change aliases in COURSE_FOLDER_BY_TAG near the top of the Python file.
- Edit EXTENSION_FOLDERS to change file-type folder names.
- If a destination already contains the same filename, the script adds (1), (2), etc.

REQUIREMENTS
- Windows 10/11 and Python 3 installed with the Windows py launcher.
- No extra Python packages are required.
